from datetime import datetime
from app.extensions import db
from sqlalchemy import UniqueConstraint

class LekhanaSession(db.Model):
    __tablename__ = 'lekhana_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    guru_id = db.Column(db.Integer, db.ForeignKey('gurus.id'), nullable=False)
    session_uuid = db.Column(db.String(36), unique=True, nullable=False)
    mode = db.Column(db.String(20), nullable=False) # type, handwrite, mobile
    target_count = db.Column(db.Integer, nullable=False, default=108)
    completed_count = db.Column(db.Integer, nullable=False, default=0)
    language = db.Column(db.String(20), nullable=False, default='en')
    status = db.Column(db.String(20), nullable=False, default='in_progress') # in_progress, completed, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    entries = db.relationship('LekhanaEntry', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def progress_percent(self):
        if self.target_count == 0:
            return 0
        return min(100, int((self.completed_count / self.target_count) * 100))
        
    @property
    def is_completed(self):
        return self.completed_count >= self.target_count or self.status == 'completed'

class LekhanaEntry(db.Model):
    __tablename__ = 'lekhana_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lekhana_sessions.id'), nullable=False)
    entry_number = db.Column(db.Integer, nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    typed_text = db.Column(db.Text, nullable=True)
    drawing_data = db.Column(db.Text, nullable=True) # For handwriting coordinates or image ref
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SevaProgress(db.Model):
    __tablename__ = 'seva_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    guru_id = db.Column(db.Integer, db.ForeignKey('gurus.id'), nullable=False)
    total_completed = db.Column(db.Integer, default=0)
    last_session_id = db.Column(db.Integer, db.ForeignKey('lekhana_sessions.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    last_session = db.relationship('LekhanaSession', foreign_keys=[last_session_id])
    
    __table_args__ = (
        UniqueConstraint('user_id', 'guru_id', name='uq_user_guru_seva'),
    )
