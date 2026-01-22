"""
Translation Service for Flask Blog App

PRODUCTION-SAFE IMPLEMENTATION for Render deployment:
- All translation happens server-side ONLY (backend)
- API keys loaded from environment variables
- HTTPS enforced for all external API calls
- Proper error handling and logging for Render monitoring
- Graceful fallback to MyMemory API if LibreTranslate fails
- Rate limiting detection and cooldown to prevent service degradation
"""

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
    total=2,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
    raise_on_status=False,
)
_adapter = HTTPAdapter(max_retries=_retry_strategy)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

# Small in-memory cache to avoid repeated identical requests
_CACHE_MAXSIZE = 512

# Simple cooldown state to avoid repeatedly calling rate-limited services
_last_rate_limit_hit = 0.0
_COOLDOWN_SECONDS = 60


class TranslationService:
    """Service to handle text translation with backend-only architecture.
    
    Features:
    - Server-side translation only (no client-side API calls)
    - Environment variable API key support
    - HTTPS enforcement for Render security
    - Comprehensive error logging
    - Automatic fallback to MyMemory API
    - Rate limit protection
    """
    
    @staticmethod
    def translate_text(text, target_lang='en', source_lang='auto'):
        """
        Translate text to the target language using backend API only.
        
        PRODUCTION NOTES:
        - All translation happens server-side ONLY
        - API key is loaded from TRANSLATION_API_KEY environment variable
        - HTTPS is enforced for all API calls
        - Rate limiting is handled gracefully with cooldown and fallback
        - All errors are logged for Render monitoring
        
        Args:
            text (str): Text to translate
            target_lang (str): Target language code (e.g., 'en', 'es', 'fr')
            source_lang (str): Source language code (default: 'auto' for auto-detection)
            
        Returns:
            str: Translated text or original text if translation fails
        """
        # Return original if no translation needed
        if not text or target_lang == 'en' or not text.strip():
            return text
        
        # Check if translations are disabled globally
        try:
            if os.environ.get('TRANSLATION_ENABLED', '').lower() == 'false':
                logger.info('Translation disabled via TRANSLATION_ENABLED env var')
                return text
        except Exception:
            pass

        try:
            if not current_app.config.get('TRANSLATION_ENABLED', True):
                logger.info('Translation disabled by app config')
                return text
        except Exception:
            pass

        try:
            # Get configuration from environment variables (priority) or app config
            api_url = os.environ.get('TRANSLATION_API_URL') or current_app.config.get('TRANSLATION_API_URL', '')
            api_key = os.environ.get('TRANSLATION_API_KEY') or current_app.config.get('TRANSLATION_API_KEY', '')

            logger.debug(f"Backend translation initiated: text={text[:50]}..., target={target_lang}, source={source_lang}")

            # Check rate limit cooldown
            try:
                global _last_rate_limit_hit
                if _last_rate_limit_hit and (time.time() - _last_rate_limit_hit) < _COOLDOWN_SECONDS:
                    logger.warning(f"Translation in cooldown (hit limit {_COOLDOWN_SECONDS}s ago); returning original text")
                    return text
            except Exception as e:
                logger.warning(f"Cooldown check failed: {e}")

            # Attempt cached translation
            try:
                cached_result = TranslationService._cached_translate_call(api_url, api_key, text, target_lang, source_lang)
                logger.debug(f"Cached translation succeeded: {cached_result[:50]}...")
                return cached_result
            except Exception as e:
                logger.warning(f"Cached translation failed: {e}; attempting direct call")
                
                # Fallback: try direct LibreTranslate or MyMemory
                if api_url and api_url.strip():
                    try:
                        result = TranslationService._translate_with_libretranslate(text, target_lang, source_lang, api_url, api_key)
                        logger.info(f"Direct LibreTranslate translation succeeded")
                        return result
                    except Exception as e:
                        logger.warning(f"LibreTranslate failed: {e}; falling back to MyMemory")
                        return TranslationService._translate_with_mymemory(text, target_lang, source_lang)
                else:
                    logger.info("No LibreTranslate URL configured; using MyMemory fallback")
                    return TranslationService._translate_with_mymemory(text, target_lang, source_lang)

        except Exception as e:
            logger.exception(f"Unexpected translation error: {str(e)}; returning original text")
            return text
    
    @functools.lru_cache(maxsize=_CACHE_MAXSIZE)
    def _cached_translate_call(api_url, api_key, text, target_lang, source_lang):
        """Cached wrapper around translation calls to reduce repeated API usage.
        
        Uses LRU cache to avoid redundant external API calls for identical requests.
        """
        # Prefer configured endpoint, fall back to MyMemory
        if api_url and api_url.strip():
            try:
                return TranslationService._translate_with_libretranslate(text, target_lang, source_lang, api_url, api_key)
            except Exception as e:
                logger.debug(f"Cached call to LibreTranslate failed: {e}; falling back to MyMemory")
                return TranslationService._translate_with_mymemory(text, target_lang, source_lang)
        else:
            return TranslationService._translate_with_mymemory(text, target_lang, source_lang)
    
    @staticmethod
    def _translate_with_libretranslate(text, target_lang, source_lang, api_url, api_key):
        """Translate using LibreTranslate API with proper error handling and HTTPS enforcement.
        
        PRODUCTION NOTES:
        - Enforces HTTPS for security on Render
        - Includes API key from environment if available
        - Handles rate limiting (429) gracefully
        - Logs all errors for Render monitoring
        - Implements timeout to prevent blocking
        
        Args:
            text (str): Text to translate
            target_lang (str): Target language
            source_lang (str): Source language
            api_url (str): LibreTranslate API endpoint
            api_key (str): API key (optional)
            
        Returns:
            str: Translated text or raises exception
            
        Raises:
            ValueError: If API URL missing
            requests.exceptions.RequestException: On HTTP errors
        """
        if not api_url:
            logger.warning("LibreTranslate API URL not configured")
            raise ValueError("No LibreTranslate API URL provided")
        
        # Enforce HTTPS for production security
        if not api_url.startswith('https://'):
            logger.warning(f"LibreTranslate URL must use HTTPS; got: {api_url}")
            api_url = api_url.replace('http://', 'https://')
            logger.info(f"Converted to HTTPS: {api_url}")
        
        # Build payload with API key
        payload = {
            'q': text,
            'source': source_lang,
            'target': target_lang
        }
        
        if api_key and api_key.strip():
            payload['api_key'] = api_key
            logger.debug("Using API key for LibreTranslate request (key hidden in logs)")
        else:
            logger.debug("No API key provided; attempting public endpoint")
        
        try:
            logger.debug(f"Calling LibreTranslate: {api_url}")
            response = _session.post(api_url, json=payload, timeout=5)
            
            # Handle rate limiting (429)
            if response.status_code == 429:
                logger.error("LibreTranslate rate limit exceeded (429)")
                global _last_rate_limit_hit
                _last_rate_limit_hit = time.time()
                raise requests.exceptions.HTTPError(f"Rate limited (429)")
            
            # Log other HTTP errors
            if response.status_code >= 400:
                logger.error(f"LibreTranslate returned {response.status_code}: {response.text[:200]}")
                response.raise_for_status()
            
            # Parse JSON response
            try:
                result = response.json()
                logger.debug(f"LibreTranslate response received (status={response.status_code})")
            except ValueError as e:
                logger.error(f"LibreTranslate returned invalid JSON: {response.text[:200]}")
                raise requests.exceptions.RequestException(f"Invalid JSON response: {e}")
            
            # Extract translated text from response
            translated = result.get('translatedText') or result.get('result') or result.get('translation')
            if not translated:
                logger.error(f"No translation found in response: {result}")
                raise ValueError("No translation in response")
            
            logger.info(f"LibreTranslate translation successful: '{translated[:50]}...'")
            return translated

        except requests.exceptions.Timeout as e:
            logger.error(f"LibreTranslate timeout (5s): {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"LibreTranslate connection error (possible IP block or DNS issue): {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"LibreTranslate HTTP error: {e}")
            raise
    
    @staticmethod
    def _translate_with_mymemory(text, target_lang, source_lang='en'):
        """Translate using MyMemory API as fallback (free, no auth required).
        
        PRODUCTION NOTES:
        - Used as graceful fallback when LibreTranslate is unavailable
        - Uses HTTPS only for Render production safety
        - Normalizes language codes to two-letter format
        - Returns original text on error (never raises)
        
        Args:
            text (str): Text to translate
            target_lang (str): Target language
            source_lang (str): Source language (default: 'en')
            
        Returns:
            str: Translated text or original text on error
        """
        # Normalize language codes to two-letter format
        src = source_lang if source_lang and source_lang != 'auto' else 'en'
        tgt = target_lang if target_lang else 'en'
        # Extract first two chars (e.g., 'en-US' -> 'en')
        src = src[:2] if src else 'en'
        tgt = tgt[:2] if tgt else 'en'

        url = 'https://api.mymemory.translated.net/get'  # HTTPS enforced
        params = {
            'q': text,
            'langpair': f'{src}|{tgt}'
        }

        try:
            logger.debug(f"Calling MyMemory fallback: langpair={src}|{tgt}")
            response = _session.get(url, params=params, timeout=5)
            
            # Handle rate limiting (429)
            if response.status_code == 429:
                logger.error(f"MyMemory rate limit exceeded (429) for: {text[:60]}...")
                global _last_rate_limit_hit
                _last_rate_limit_hit = time.time()
                return text
            
            # Log other HTTP errors but don't raise to avoid breaking the request
            if response.status_code >= 400:
                logger.error(f"MyMemory returned {response.status_code}: {response.text[:200]}")
                return text
            
            # Parse response
            try:
                result = response.json()
                logger.debug(f"MyMemory response received (status={response.status_code})")
            except ValueError as e:
                logger.error(f"MyMemory invalid JSON: {response.text[:200]}")
                return text

            # Check MyMemory response status
            if result.get('responseStatus') == 200:
                translated = result.get('responseData', {}).get('translatedText', text)
                if translated and translated != text:
                    logger.info(f"MyMemory translation succeeded: '{translated[:50]}...'")
                    return translated
                else:
                    logger.info(f"MyMemory returned original text (no translation found)")
                    return text
            else:
                logger.warning(f"MyMemory API error: status={result.get('responseStatus')}")
                return text

        except requests.exceptions.Timeout as e:
            logger.error(f"MyMemory timeout (5s): {e}")
            return text
        except requests.exceptions.ConnectionError as e:
            logger.error(f"MyMemory connection error: {e}")
            return text
        except requests.exceptions.RequestException as e:
            logger.error(f"MyMemory request error: {e}")
            return text
    
    @staticmethod
    def get_supported_languages():
        """Get list of supported languages for the UI.
        
        Returns:
            dict: Language code -> Language name mapping
        """
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
