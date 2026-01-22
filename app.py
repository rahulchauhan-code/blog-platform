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
    
    # Database initialization: Flask-Migrate handles all schema management
    # Database initialization & safety checks
    # IMPORTANT: In production we require a proper DATABASE_URL and committed migrations.
    with app.app_context():
        try:
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '') or os.environ.get('DATABASE_URL')
            # Masked display for logs (show scheme and host only)
            masked_uri = None
            try:
                if db_uri:
                    if '://' in db_uri:
                        scheme, rest = db_uri.split('://', 1)
                        host = rest.split('@')[-1].split('/')[0]
                        masked_uri = f"{scheme}://{host}"
                    else:
                        masked_uri = db_uri
            except Exception:
                masked_uri = 'unknown'

            # If running in production, ensure DATABASE_URL is provided and not sqlite
            if config_name == 'production':
                if not db_uri:
                    logger.critical('No DATABASE_URL detected in production. Aborting startup to avoid falling back to SQLite.')
                    raise SystemExit('Missing DATABASE_URL in production environment. Set DATABASE_URL to your PostgreSQL connection string.')
                if db_uri.startswith('sqlite'):
                    logger.critical('Detected SQLite DATABASE_URL in production (%s). Aborting startup.', masked_uri)
                    raise SystemExit('Refusing to run with SQLite in production. Configure DATABASE_URL to point to PostgreSQL.')

                # Ensure migrations exist and were committed
                migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
                versions_dir = os.path.join(migrations_dir, 'versions')
                if not (os.path.isdir(migrations_dir) and os.path.isdir(versions_dir) and any(os.scandir(versions_dir))):
                    logger.critical('No Flask-Migrate migrations found in repo. Aborting startup.')
                    raise SystemExit('Migrations missing. Run `flask db init` (if first time), `flask db migrate` and commit the migrations, then deploy.')

            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if tables:
                logger.info('Database initialized with tables: %s (db=%s)', tables, masked_uri)
            else:
                # If migrations exist, suggest running upgrade; otherwise instruct to create migrations
                logger.error('No tables found in database (db=%s). Ensure migrations are applied: run `flask db upgrade`.', masked_uri)
                if config_name == 'production':
                    raise SystemExit('No tables present in the database. Apply migrations (flask db upgrade) before starting in production.')
        except SystemExit:
            raise
        except Exception as e:
            logger.exception(f"Error checking database tables: {str(e)}")
    
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
