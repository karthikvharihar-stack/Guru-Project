import os
from datetime import timedelta

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp3', 'mp4'}
    
    # AI & Services
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day; 50 per hour"

class DevelopmentConfig(BaseConfig):
    DEBUG = True

    @staticmethod
    def _build_uri():
        if os.environ.get('USE_SQLITE', 'False').lower() in ['true', '1', 't']:
            return 'sqlite:///guru_project_dev.db'
        user = os.environ.get('DB_USER', 'root')
        pw = os.environ.get('DB_PASSWORD', '')
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '3306')
        name = os.environ.get('DB_NAME', 'uttaradi_math')
        return f"mysql+pymysql://{user}:{pw}@{host}:{port}/{name}"

    SQLALCHEMY_DATABASE_URI = 'sqlite:///guru_project_dev.db'  # default overridden by factory

class ProductionConfig(BaseConfig):
    DEBUG = False
    
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'uttaradi_math')
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///guru_project_test.db'
    WTF_CSRF_ENABLED = False

config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig,
    testing=TestingConfig
)
