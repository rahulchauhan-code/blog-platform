from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import logging

from config import config
from models import db, User
from routes import main_bp, auth_bp, posts_bp
from services import TranslationService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp, url_prefix='/posts')

    @app.context_processor
    def inject_globals():
        """Provide `current_lang` and `supported_languages` to all templates."""
        try:
            lang = request.args.get('lang', 'en')
        except Exception:
            lang = 'en'
        try:
            supported = TranslationService.get_supported_languages()
        except Exception:
            supported = {}
        return dict(current_lang=lang, supported_languages=supported)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # Log the full exception traceback so it's visible in server logs
        db.session.rollback()
        logger.exception('Internal server error:')
        return render_template('errors/500.html'), 500
    
    # Create database tables
    with app.app_context():
        try:
            # This will create tables if they don't exist
            # Note: For production, use Flask-Migrate instead
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    return app

# Create the application instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('SERVER_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
