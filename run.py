"""
run.py — Uttaradi Math Guru Lekhana Seva Application Entry Point
"""
import os

# Load .env FIRST before any other imports so config picks up env vars
from dotenv import load_dotenv
load_dotenv()

# Now import the app factory
from app import create_app

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # Create necessary directories
    dirs = [
        os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'gurus'),
        os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'books'),
        os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'media'),
        os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'ai_docs'),
        'ai/chroma_db',
        'flask_session',
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    debug = env == 'development'
    print(f"\n{'='*50}")
    print(f"  Uttaradi Math — Guru Lekhana Seva")
    print(f"  Environment : {env}")
    print(f"  Database    : {app.config['SQLALCHEMY_DATABASE_URI'][:60]}...")
    print(f"  Debug       : {debug}")
    print(f"  URL         : http://127.0.0.1:5000")
    print(f"{'='*50}\n")

    app.run(debug=debug, host='0.0.0.0', port=5000)
