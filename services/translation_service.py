"""Translation service for multi-language support"""
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

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
        
        # Skip translation if source and target are the same
        if source_lang == target_lang:
            return text
        
        # Skip empty text
        if not text or not text.strip():
            return text
        
        try:
            api_url = 'https://api.mymemory.translated.net/get'
            
            # MyMemory API uses GET requests with query parameters
            params = {
                'q': text,
                'langpair': f'{source_lang}|{target_lang}'
            }
            
            response = requests.get(
                api_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # MyMemory API response format
                if 'responseData' in result:
                    translated_text = result['responseData'].get('translatedText', text)
                    
                    # Check if translation was successful (not empty or same as original)
                    if translated_text and translated_text != text:
                        logger.debug(f'Translated from {source_lang} to {target_lang}')
                        return translated_text
                    else:
                        logger.debug('Translation returned same text, using original')
                        return text
                else:
                    logger.warning('Unexpected API response format')
                    return text
            else:
                logger.warning(f'Translation API returned status {response.status_code}')
                return text
                
        except requests.exceptions.Timeout:
            logger.error('Translation request timed out')
            return text
        except requests.exceptions.RequestException as e:
            logger.error(f'Translation request failed: {e}')
            return text
        except Exception as e:
            logger.error(f'Unexpected error during translation: {e}')
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
