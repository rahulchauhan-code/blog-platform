import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

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
        if not text or target_lang == 'en':
            return text
            
        try:
            api_url = current_app.config.get('TRANSLATION_API_URL', '')
            api_key = current_app.config.get('TRANSLATION_API_KEY', '')

            logger.debug(f"Translating text to {target_lang}: {text[:50]}...")

            # Try configured translation endpoint first, otherwise fall back to MyMemory
            if api_url and api_url.strip():
                try:
                    return TranslationService._translate_with_libretranslate(
                        text, target_lang, source_lang, api_url, api_key
                    )
                except Exception as e:
                    # Log and fall back to MyMemory
                    logger.warning(f"LibreTranslate failed, falling back to MyMemory: {e}")
                    return TranslationService._translate_with_mymemory(text, target_lang, source_lang)
            else:
                return TranslationService._translate_with_mymemory(text, target_lang, source_lang)

        except Exception as e:
            logger.exception(f"Unexpected translation error: {str(e)}")
            return text
    
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
            # Let requests follow redirects by default and prefer JSON payloads
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()

            try:
                result = response.json()
            except ValueError:
                # Non-JSON response — log and raise so caller can fall back
                logger.warning("LibreTranslate returned non-JSON response: %s", response.text[:200])
                raise

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
            response = requests.get(url, params=params, timeout=10)
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
