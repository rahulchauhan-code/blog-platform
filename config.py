import os
from dotenv import load_dotenv
from datetime import timedelta

# Base directory of the application (used for sqlite file path)
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration - Using SQLite for demo (change to Oracle in production)
    # For Oracle: oracle+cx_oracle://username:password@host:port/?service_name=service
    # For PostgreSQL: postgresql://username:password@host:port/database
    # For MySQL: mysql://username:password@host:port/database
    
    # Prefer DATABASE_URL; fall back to SPRING_DATASOURCE_URL or individual SPRING vars if provided
    _db_url = os.environ.get('DATABASE_URL') or os.environ.get('SPRING_DATASOURCE_URL')
    if not _db_url:
        _spring_user = os.environ.get('SPRING_DATASOURCE_USERNAME')
        _spring_pass = os.environ.get('SPRING_DATASOURCE_PASSWORD')
        _spring_host = os.environ.get('SPRING_DATASOURCE_HOST')
        _spring_db = os.environ.get('SPRING_DATASOURCE_DB')
        if _spring_user and _spring_pass and _spring_host and _spring_db:
            _db_url = f"postgresql://{_spring_user}:{_spring_pass}@{_spring_host}/{_spring_db}"

    # Use a file-based SQLite DB inside the instance folder by default so the
    # database file is colocated with the app and easier to mount/persist.
    default_sqlite_path = os.path.join(basedir, 'instance', 'blog.db')
    SQLALCHEMY_DATABASE_URI = _db_url or f"sqlite:///{default_sqlite_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    
    # Translation API
    TRANSLATION_API_URL = os.environ.get('TRANSLATION_API_URL', 'https://libretranslate.de/translate')
    TRANSLATION_API_KEY = os.environ.get('TRANSLATION_API_KEY', '')
    # Toggle runtime translation to avoid external API calls in production
    TRANSLATION_ENABLED = os.environ.get('TRANSLATION_ENABLED', 'true').lower() == 'true'
    
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
