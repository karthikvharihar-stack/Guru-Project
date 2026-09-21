import uuid
from datetime import datetime
from app.models.lekhana import LekhanaSession, LekhanaEntry, SevaProgress
from app.extensions import db

def create_session(guru_id, user_id, mode, target_count, language):
    session = LekhanaSession(
        guru_id=guru_id,
        user_id=user_id,
        mode=mode,
        target_count=target_count,
        language=language,
        session_uuid=str(uuid.uuid4())
    )
    db.session.add(session)
    db.session.commit()
    return session

def save_entry(session_id, mode, typed_text=None, drawing_data=None):
    session = LekhanaSession.query.get(session_id)
    if not session:
        return None, 0
    entry_number = session.completed_count + 1
    
    is_valid = True
    if mode == 'type' and typed_text and session.guru.lekhana_text:
        is_valid = validate_lekhana_text(typed_text, session.guru.lekhana_text)
        
    entry = LekhanaEntry(
        session_id=session_id,
        entry_number=entry_number,
        mode=mode,
        typed_text=typed_text,
        drawing_data=drawing_data,
        is_valid=is_valid
    )
    
    if is_valid:
        session.completed_count += 1
        if session.user_id:
            update_seva_progress(session.user_id, session.guru_id, increment=1, session_id=session.id)
        if session.completed_count >= session.target_count:
            session.status = 'completed'
            session.completed_at = datetime.utcnow()
            
    db.session.add(entry)
    db.session.commit()
    
    return entry, session.completed_count

def validate_lekhana_text(typed_text, guru_lekhana_text):
    if not guru_lekhana_text:
        return True
    
    clean_typed = ''.join(e for e in typed_text.lower() if e.isalnum())
    clean_target = ''.join(e for e in guru_lekhana_text.lower() if e.isalnum())
    
    # Simple check for now
    return len(clean_typed) >= min(len(clean_target) * 0.8, 10)

def complete_session(session_id):
    session = LekhanaSession.query.get(session_id)
    if not session:
        return False
    if session.status != 'completed':
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        db.session.commit()
    return True

def get_user_seva_summary(user_id):
    progress = SevaProgress.query.filter_by(user_id=user_id).all()
    total_lekhana = sum(p.total_completed for p in progress)
    return {
        'total_completed': total_lekhana,
        'guru_breakdown': progress
    }

def update_seva_progress(user_id, guru_id, increment=1, session_id=None):
    """Increment SevaProgress for a user-guru pair by the given amount."""
    if not user_id:
        return
        
    progress = SevaProgress.query.filter_by(user_id=user_id, guru_id=guru_id).first()
    if not progress:
        progress = SevaProgress(user_id=user_id, guru_id=guru_id, total_completed=0)
        db.session.add(progress)
        
    progress.total_completed += increment
    progress.updated_at = datetime.utcnow()
    if session_id:
        progress.last_session_id = session_id
    db.session.commit()
