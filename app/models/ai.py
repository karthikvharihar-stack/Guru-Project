from datetime import datetime
from app.extensions import db

class AIDocument(db.Model):
    __tablename__ = 'ai_documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    source_type = db.Column(db.String(50), nullable=False) # pdf, txt, article
    file_path = db.Column(db.String(500), nullable=True)
    is_indexed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chunks = db.relationship('AIChunk', backref='document', lazy='dynamic', cascade='all, delete-orphan')

class AIChunk(db.Model):
    __tablename__ = 'ai_chunks'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('ai_documents.id'), nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    embedding_id = db.Column(db.String(100), nullable=True)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    target_table = db.Column(db.String(100), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True) # JSON stored as string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
