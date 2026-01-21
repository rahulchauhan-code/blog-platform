"""Routes package initialization"""
from .main import main_bp
from .auth import auth_bp
from .posts import posts_bp

__all__ = ['main_bp', 'auth_bp', 'posts_bp']
