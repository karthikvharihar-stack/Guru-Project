from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models.lekhana import LekhanaSession, SevaProgress
from app.models.guru import Guru
from app.extensions import db

seva_bp = Blueprint('seva', __name__)


@seva_bp.route('/my-seva')
@login_required
def dashboard():
    """User's personal Seva dashboard."""
    # Get all seva progress records for this user
    progress_records = (SevaProgress.query
                        .filter_by(user_id=current_user.id)
                        .join(Guru)
                        .order_by(SevaProgress.updated_at.desc())
                        .all())

    # Get recent sessions
    recent_sessions = (LekhanaSession.query
                       .filter_by(user_id=current_user.id)
                       .order_by(LekhanaSession.created_at.desc())
                       .limit(20).all())

    # Summary stats
    total_completed = sum(p.total_completed for p in progress_records)
    gurus_with_seva = len(progress_records)
    completed_targets = sum(
        1 for s in recent_sessions
        if s.status == 'completed'
    )

    # In-progress sessions (not completed)
    active_sessions = [s for s in recent_sessions if s.status == 'in_progress']

    stats = {
        'total_lekhana': total_completed,
        'gurus_count': gurus_with_seva,
        'completed_targets': completed_targets,
        'active_sessions': len(active_sessions),
    }

    return render_template(
        'seva/dashboard.html',
        progress_records=progress_records,
        recent_sessions=recent_sessions,
        active_sessions=active_sessions,
        stats=stats
    )
