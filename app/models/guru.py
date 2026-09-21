from datetime import datetime
from slugify import slugify
from app.extensions import db

class Guru(db.Model):
    __tablename__ = 'gurus'
    
    id = db.Column(db.Integer, primary_key=True)
    guru_order = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    traditional_name = db.Column(db.String(200), nullable=True)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    short_description = db.Column(db.Text, nullable=True)
    biography = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    birth_date = db.Column(db.String(100), nullable=True)
    aradhana_date = db.Column(db.String(100), nullable=True)
    
    lekhana_text = db.Column(db.Text, nullable=True)
    lekhana_sanskrit = db.Column(db.Text, nullable=True)
    lekhana_kannada = db.Column(db.Text, nullable=True)
    lekhana_english = db.Column(db.Text, nullable=True)
    
    previous_guru_id = db.Column(db.Integer, db.ForeignKey('gurus.id'), nullable=True)
    next_guru_id = db.Column(db.Integer, db.ForeignKey('gurus.id'), nullable=True)
    
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sources = db.relationship('GuruSource', backref='guru', lazy='dynamic', cascade='all, delete-orphan')
    works = db.relationship('GuruWork', backref='guru', lazy='dynamic', cascade='all, delete-orphan')
    lekhana_sessions = db.relationship('LekhanaSession', backref='guru', lazy='dynamic')
    seva_progress = db.relationship('SevaProgress', backref='guru', lazy='dynamic')
    events = db.relationship('CalendarEvent', backref='guru', lazy='dynamic')
    
    previous_guru = db.relationship('Guru', remote_side=[id], foreign_keys=[previous_guru_id])
    next_guru = db.relationship('Guru', remote_side=[id], foreign_keys=[next_guru_id])

    @property
    def display_lekhana(self):
        if not self.is_verified or not self.lekhana_text:
            return "[PLACEHOLDER - Awaiting Admin Verification]"
        return self.lekhana_text

    def get_slug(self):
        if not self.slug:
            self.slug = slugify(self.name)
        return self.slug

    def to_dict(self):
        return {
            'id': self.id,
            'guru_order': self.guru_order,
            'name': self.name,
            'traditional_name': self.traditional_name,
            'slug': self.slug,
            'short_description': self.short_description,
            'biography': self.biography,
            'image_url': self.image_url,
            'is_verified': self.is_verified,
            'lekhana_text': self.display_lekhana
        }

class GuruSource(db.Model):
    __tablename__ = 'guru_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    guru_id = db.Column(db.Integer, db.ForeignKey('gurus.id'), nullable=False)
    source_title = db.Column(db.String(255), nullable=False)
    source_type = db.Column(db.String(50), nullable=True) # book, link, article
    source_url = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

class GuruWork(db.Model):
    __tablename__ = 'guru_works'
    
    id = db.Column(db.Integer, primary_key=True)
    guru_id = db.Column(db.Integer, db.ForeignKey('gurus.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    title_devanagari = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    work_type = db.Column(db.String(100), nullable=True) # stotra, grantha, bhashya
