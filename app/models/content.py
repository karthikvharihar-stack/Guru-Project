from datetime import datetime
from app.extensions import db

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    language = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(255), nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    language = db.Column(db.String(50), nullable=True)
    author = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Media(db.Model):
    __tablename__ = 'media'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    speaker = db.Column(db.String(255), nullable=True)
    topic = db.Column(db.String(255), nullable=True)
    language = db.Column(db.String(50), nullable=True)
    media_type = db.Column(db.String(50), nullable=False) # video, audio
    embed_url = db.Column(db.String(500), nullable=True)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    tithi = db.Column(db.String(100), nullable=True)
    event_type = db.Column(db.String(50), nullable=False, default='event')  # aradhana, festival, event
    guru_id = db.Column(db.Integer, db.ForeignKey('gurus.id'), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
