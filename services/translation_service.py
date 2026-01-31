"""Translation service for multi-language support"""
import logging
import time

logger = logging.getLogger(__name__)

# Simple in-memory cache to reduce repeated translation calls
_translation_cache = {}
_CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours
_NEGATIVE_CACHE_TTL_SECONDS = 5 * 60  # 5 minutes

def _get_cached_translation(cache_key):
    entry = _translation_cache.get(cache_key)
    if not entry:
        return None
    value, expires_at = entry
    if expires_at < time.time():
        _translation_cache.pop(cache_key, None)
        return None
    return value

def _set_cached_translation(cache_key, value, ttl_seconds):
    _translation_cache[cache_key] = (value, time.time() + ttl_seconds)

try:
    import translators as ts
    TRANSLATORS_AVAILABLE = True
except ImportError:
    TRANSLATORS_AVAILABLE = False
    logger.warning('translators library not installed - translations will be disabled')

from flask import current_app

class TranslationService:
    """Service for translating text content"""
    
    @staticmethod
    def translate(text, source_lang='en', target_lang='es'):
        """
        Translate text from source language to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: 'en')
            target_lang: Target language code (default: 'es')
            
        Returns:
            Translated text or original text if translation fails
        """
        # Check if translation is enabled
        if not current_app.config.get('TRANSLATION_ENABLED', True):
            logger.debug('Translation disabled, returning original text')
            return text
        
        # Check if translators library is available
        if not TRANSLATORS_AVAILABLE:
            logger.debug('Translators library not available')
            return text
        
        # Skip translation if source and target are the same
        if source_lang == target_lang:
            return text
        
        # Skip empty text
        if not text or not text.strip():
            return text
        
        cache_key = f'{source_lang}|{target_lang}|{text}'
        cached = _get_cached_translation(cache_key)
        if cached is not None:
            return cached

        try:
            # Use Google Translate via translators library
            translated_text = ts.google(text, from_language=source_lang, to_language=target_lang)
            
            if translated_text and translated_text != text:
                logger.debug(f'Translated from {source_lang} to {target_lang}')
                _set_cached_translation(cache_key, translated_text, _CACHE_TTL_SECONDS)
                return translated_text
            else:
                logger.debug('Translation returned same text, using original')
                _set_cached_translation(cache_key, text, _CACHE_TTL_SECONDS)
                return text
                
        except Exception as e:
            logger.error(f'Translation failed: {e}')
            _set_cached_translation(cache_key, text, _NEGATIVE_CACHE_TTL_SECONDS)
            return text
    
    @staticmethod
    def get_supported_languages():
        """
        Get dictionary of supported languages with their names
        
        Returns:
            Dictionary of language codes and names
        """
        return {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'ar': 'العربية',
            'hi': 'हिन्दी'
        }
