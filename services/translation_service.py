import requests
import os
import logging
import functools
from flask import current_app
import time

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Shared session with retries to handle transient errors and 429s
_session = requests.Session()
_retry_strategy = Retry(
    total=0,
    backoff_factor=0.1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
    raise_on_status=False,
)
_adapter = HTTPAdapter(max_retries=_retry_strategy)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

# Small in-memory cache to avoid repeated identical requests
_CACHE_MAXSIZE = 1024

# Simple cooldown state to avoid repeatedly calling rate-limited services
_last_rate_limit_hit = 0.0
_COOLDOWN_SECONDS = 60

class TranslationService:
    """Service to handle text translation using LibreTranslate API"""
    
    @staticmethod
    def translate_text(text, target_lang='en', source_lang='auto'):
        """
        Translate text to the target language
        
        Args:
            text (str): Text to translate
            target_lang (str): Target language code (e.g., 'en', 'es', 'fr')
            source_lang (str): Source language code (default: 'auto' for auto-detection)
            
        Returns:
            str: Translated text or original text if translation fails
        """
        # Environment-level override: if TRANSLATION_ENABLED env var set to 'false', skip translations
        try:
            if os.environ.get('TRANSLATION_ENABLED', '').lower() == 'false':
                logger.info('Translation disabled by TRANSLATION_ENABLED env var; returning original text')
                return text
        except Exception:
            pass

        # Short-circuit if translations are disabled in config (production hotfix)
        try:
            if not current_app.config.get('TRANSLATION_ENABLED', True):
                logger.info('Translation disabled by configuration; returning original text')
                return text
        except Exception:
            # if current_app unavailable, continue
            pass

        if not text or target_lang == 'en':
            return text
            
        try:
            api_url = current_app.config.get('TRANSLATION_API_URL', '')
            api_key = current_app.config.get('TRANSLATION_API_KEY', '')

            logger.debug(f"Translating text to {target_lang}: {text[:50]}...")

            # If we recently hit a rate limit, avoid calling external services to
            # prevent blocking the web worker. Return original text as a safe fallback.
            try:
                global _last_rate_limit_hit
                if _last_rate_limit_hit and (time.time() - _last_rate_limit_hit) < _COOLDOWN_SECONDS:
                    logger.warning("Translation service in cooldown; skipping external calls")
                    return text
            except Exception:
                # Fall through to normal behavior if cooldown check fails
                pass

            # Use cached wrapper to reduce duplicate translations and API calls
            try:
                return TranslationService._cached_translate_call(api_url, api_key, text, target_lang, source_lang)
            except Exception as e:
                logger.warning(f"Cached translation call failed, attempting uncached fallback: {e}")
                # Best-effort: try uncached calls
                if api_url and api_url.strip():
                    try:
                        return TranslationService._translate_with_libretranslate(text, target_lang, source_lang, api_url, api_key)
                    except Exception:
                        return TranslationService._translate_with_mymemory(text, target_lang, source_lang)
                else:
                    return TranslationService._translate_with_mymemory(text, target_lang, source_lang)

        except Exception as e:
            logger.exception(f"Unexpected translation error: {str(e)}")
            return text
    
    @functools.lru_cache(maxsize=_CACHE_MAXSIZE)
    def _cached_translate_call(api_url, api_key, text, target_lang, source_lang):
        """Cached wrapper around translation calls to reduce repeated API usage."""
        # Prefer configured endpoint, fall back to MyMemory
        if api_url and api_url.strip():
            try:
                return TranslationService._translate_with_libretranslate(text, target_lang, source_lang, api_url, api_key)
            except Exception:
                return TranslationService._translate_with_mymemory(text, target_lang, source_lang)
        else:
            return TranslationService._translate_with_mymemory(text, target_lang, source_lang)
    
    @staticmethod
    def _translate_with_libretranslate(text, target_lang, source_lang, api_url, api_key):
        """Translate using LibreTranslate API"""
        payload = {
            'q': text,
            'source': source_lang,
            'target': target_lang
        }
        
        if api_key:
            payload['api_key'] = api_key
        
        try:
            # Use shared session (with retry/backoff) and prefer JSON payloads

            response = _session.post(api_url, json=payload, timeout=3)
            # Handle rate limiting gracefully: fall back to MyMemory if over limit
            if response.status_code == 429:
                logger.warning("LibreTranslate responded with 429 Too Many Requests; falling back to MyMemory")
                global _last_rate_limit_hit
                _last_rate_limit_hit = time.time()
                return TranslationService._translate_with_mymemory(text, target_lang, source_lang)

            response.raise_for_status()

            try:
                result = response.json()
            except ValueError:
                # Non-JSON response — log and fall back to MyMemory
                logger.warning("LibreTranslate returned non-JSON response: %s", response.text[:200])
                return TranslationService._translate_with_mymemory(text, target_lang, source_lang)

            # LibreTranslate typical key
            translated = result.get('translatedText') or result.get('result') or result.get('translation')
            return translated or text

        except requests.exceptions.RequestException as e:
            logger.exception(f"HTTP error calling LibreTranslate ({api_url}): {e}")
            raise
    
    @staticmethod
    def _translate_with_mymemory(text, target_lang, source_lang='en'):
        """Translate using MyMemory API (free, no auth required)"""
        # Use simple two-letter codes for MyMemory langpair. If source is 'auto', assume 'en'.
        src = source_lang if source_lang and source_lang != 'auto' else 'en'
        tgt = target_lang if target_lang else 'en'

        url = 'https://api.mymemory.translated.net/get'
        params = {
            'q': text,
            'langpair': f'{src}|{tgt}'
        }

        try:
            response = _session.get(url, params=params, timeout=3)
            # If we hit rate limits, record and return original text (do not raise)
            if response.status_code == 429:
                logger.warning("MyMemory returned 429 Too Many Requests for text: %s...", text[:60])
                global _last_rate_limit_hit
                _last_rate_limit_hit = time.time()
                return text

            response.raise_for_status()
            result = response.json()

            if result.get('responseStatus') == 200:
                translated = result['responseData'].get('translatedText', text)
                logger.info(f"Translation successful via MyMemory: {translated[:50]}...")
                return translated
            else:
                logger.warning(f"MyMemory API returned status {result.get('responseStatus')}: {result}")
                return text

        except requests.exceptions.RequestException as e:
            logger.exception(f"Error calling MyMemory: {e}")
            return text
    
    @staticmethod
    def get_supported_languages():
        """Get list of supported languages"""
        return {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi'
        }
