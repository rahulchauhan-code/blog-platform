import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    # Prefer DATABASE_URL for production (Render provides this); fall back to SQLite for local dev
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///blog.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    
    # Translation API - Using MyMemory (free, no API key required)
    TRANSLATION_API_URL = os.environ.get('TRANSLATION_API_URL', 'https://api.mymemory.translated.net/get')
    TRANSLATION_API_KEY = os.environ.get('TRANSLATION_API_KEY', '')
    # Toggle runtime translation to avoid external API calls in production
    TRANSLATION_ENABLED = os.environ.get('TRANSLATION_ENABLED', 'true').lower() == 'true'

    # Debug endpoint guard key (empty disables access)
    DEBUG_KEY = os.environ.get('DEBUG_KEY', '')
    
    # Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 604800  # 7 days in seconds
    # Flask-Login remember cookie duration
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True
    # Disable translations by default in production to avoid rate limits/outages
    TRANSLATION_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
