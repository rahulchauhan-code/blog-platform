from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import logging

from config import config
from models import db, User
from routes import main_bp, auth_bp, posts_bp
from services import TranslationService
from flask import jsonify, request, abort
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Application factory pattern"""
    # Use instance_relative_config so the `instance/` folder is available
    # for runtime files (like the sqlite DB) and can be mounted/persisted
    app = Flask(__name__, instance_relative_config=True)
    # Ensure the instance folder exists (Flask expects it for instance_relative_config)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception:
        # If creating instance path fails, continue — DB init will surface errors.
        logger.exception('Could not create instance path')
    
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

    # Debug endpoint (disabled unless DEBUG_KEY env var is set)
    @app.route('/_debug_db')
    def _debug_db():
        debug_key = app.config.get('DEBUG_KEY') or os.environ.get('DEBUG_KEY')
        provided = request.args.get('key')
        if not debug_key or provided != debug_key:
            abort(404)

        from sqlalchemy import inspect
        try:
            uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            result = {'database_uri': uri, 'tables': tables}
            # include simple counts for key tables if present
            if 'post' in tables:
                count = db.session.execute('SELECT COUNT(*) FROM post').scalar()
                result['post_count'] = int(count or 0)
            return jsonify(result)
        except Exception as e:
            logger.exception('Error inspecting database')
            return jsonify({'error': str(e)}), 500

    # Lightweight healthcheck endpoint that does not touch the database
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'}), 200

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
            # If migrations aren't present on the server, create tables as a safe fallback.
            # Preferred approach: include migration files and run `flask db upgrade` during deploy.
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if not tables:
                logger.info('No tables found in DB — creating tables with db.create_all()')
                db.create_all()
                logger.info('Database tables created (db.create_all()).')
            else:
                logger.info('Database already has tables: %s', tables)
        except Exception as e:
            logger.exception(f"Error initializing database: {str(e)}")
    
    return app

# Create the application instance
# Prefer explicit FLASK_ENV or FLASK_CONFIG; default to 'production' on hosts
config_name = os.environ.get('FLASK_ENV') or os.environ.get('FLASK_CONFIG') or 'production'
app = create_app(config_name)

# Log chosen configuration and translation flag at startup
try:
    logger.info('App started with config=%s TRANSLATION_ENABLED=%s', config_name, app.config.get('TRANSLATION_ENABLED'))
except Exception:
    pass

if __name__ == '__main__':
    port = int(os.environ.get('SERVER_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
