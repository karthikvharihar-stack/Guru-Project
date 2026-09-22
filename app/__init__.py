import os
from datetime import datetime
from flask import Flask, render_template
from dotenv import load_dotenv

# Load .env before config is applied (handles cases where run.py hasn't loaded it yet)
load_dotenv()

from config import config_by_name
from app.extensions import db, login_manager, mail, limiter, migrate, session_ext, csrf


def create_app(config_name='development'):
    app = Flask(__name__)
    config_obj = config_by_name[config_name]

    # Dynamically build DB URI so it picks up .env values loaded above
    if config_name == 'development':
        if os.environ.get('USE_SQLITE', 'False').lower() in ['true', '1', 't']:
            config_obj.SQLALCHEMY_DATABASE_URI = 'sqlite:///guru_project_dev.db'
        else:
            user = os.environ.get('DB_USER', 'root')
            pw = os.environ.get('DB_PASSWORD', '')
            host = os.environ.get('DB_HOST', 'localhost')
            port = os.environ.get('DB_PORT', '3306')
            name = os.environ.get('DB_NAME', 'uttaradi_math')
            config_obj.SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{pw}@{host}:{port}/{name}"

    app.config.from_object(config_obj)

    # Create required directories
    _create_directories(app)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    session_ext.init_app(app)
    csrf.init_app(app)

    # Flask-Login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to save your Seva progress.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.guru import guru_bp
    from app.routes.lekhana import lekhana_bp
    from app.routes.seva import seva_bp
    from app.routes.pravachana import pravachana_bp
    from app.routes.calendar import calendar_bp
    from app.routes.search import search_bp
    from app.routes.jijnasa import jijnasa_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(guru_bp, url_prefix='/guru')
    app.register_blueprint(lekhana_bp, url_prefix='/lekhana')
    app.register_blueprint(seva_bp)
    app.register_blueprint(pravachana_bp, url_prefix='/pravachana')
    app.register_blueprint(calendar_bp, url_prefix='/calendar')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(jijnasa_bp, url_prefix='/guru-jijnasa')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Serve uploaded files
    from flask import send_from_directory
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(upload_folder, filename)

    # Context processors
    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.utcnow().year,
            'site_name': 'Uttaradi Math',
            'site_tagline': 'Guru Smarana • Guru Lekhana • Guru Parampara',
        }

    # CSRF exempt for AI/AJAX endpoints
    from app.extensions import csrf as csrf_ext
    csrf_ext.exempt(jijnasa_bp)
    csrf_ext.exempt(lekhana_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None


def _create_directories(app):
    """Create required directories if they don't exist."""
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    dirs = [
        os.path.join(upload_folder, 'gurus'),
        os.path.join(upload_folder, 'books'),
        os.path.join(upload_folder, 'media'),
        os.path.join(upload_folder, 'ai_docs'),
        'ai/chroma_db',
        'flask_session',
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
