import requests
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    """Minimal translation service wrapper.

    This provides `get_supported_languages()` and a `translate()` stub.
    It prefers calling the configured TRANSLATION_API_URL but falls back
    to a small built-in set if the external API is unreachable.
    """

    @staticmethod
    def get_supported_languages():
        try:
            from flask import current_app
            url = current_app.config.get('TRANSLATION_API_URL')
            if not url:
                raise RuntimeError('No TRANSLATION_API_URL')
            # Attempt a safe, read-only request to see if the service is available
            resp = requests.get(url.replace('/translate', '/languages'), timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                return {item.get('code'): item.get('name') for item in data}
        except Exception:
            logger.debug('Translation API not available, using defaults', exc_info=True)

        # Fallback minimal language set
        return {'en': 'English', 'es': 'Spanish', 'fr': 'French'}

    @staticmethod
    def translate(text, source='auto', target='en'):
        try:
            from flask import current_app
            if not current_app.config.get('TRANSLATION_ENABLED'):
                return text
            payload = {
                'q': text,
                'source': source,
                'target': target,
                'format': 'text'
            }
            headers = {}
            api_key = current_app.config.get('TRANSLATION_API_KEY')
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            resp = requests.post(current_app.config.get('TRANSLATION_API_URL'), json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json().get('translatedText') or text
        except Exception:
            logger.debug('Translation failed, returning original text', exc_info=True)
        return text
