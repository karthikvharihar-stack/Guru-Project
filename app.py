"""
app.py — Production WSGI Entry Point for Guru Lekhana Seva
Allows both `gunicorn app:app` and `gunicorn run:app` to work seamlessly on Render/Railway.
"""
from run import app

if __name__ == '__main__':
    app.run()
