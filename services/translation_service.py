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
            
            # Use MyMemory API (free, no authentication needed)
            # If custom API URL is set, try that first
            if api_url and api_url.strip():
                return TranslationService._translate_with_libretranslate(text, target_lang, source_lang, api_url, api_key)
            else:
                return TranslationService._translate_with_mymemory(text, target_lang)
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
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
        
        response = requests.post(api_url, json=payload, timeout=10, allow_redirects=False)
        
        # Handle redirects manually
        if response.status_code in (301, 302, 303, 307, 308):
            logger.debug(f"API redirected, following manually...")
            redirect_url = response.headers.get('Location')
            if redirect_url:
                response = requests.post(redirect_url, json=payload, timeout=10)
        
        response.raise_for_status()
        result = response.json()
        return result.get('translatedText', text)
    
    @staticmethod
    def _translate_with_mymemory(text, target_lang):
        """Translate using MyMemory API (free, no auth required)"""
        # Map language codes to MyMemory codes
        lang_map = {
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-PT',
            'ru': 'ru-RU',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'zh': 'zh-CN',
            'ar': 'ar-AR',
            'hi': 'hi-IN',
            'en': 'en-US'
        }
        
        target_code = lang_map.get(target_lang, target_lang)
        
        url = 'https://api.mymemory.translated.net/get'
        params = {
            'q': text,
            'langpair': f'en|{target_code}'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('responseStatus') == 200:
            translated = result['responseData'].get('translatedText', text)
            logger.info(f"Translation successful via MyMemory: {translated[:50]}...")
            return translated
        else:
            logger.warning(f"MyMemory API returned status {result.get('responseStatus')}")
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
