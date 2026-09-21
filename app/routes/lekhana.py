from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort, send_file
from flask_login import login_required, current_user
from app.models.guru import Guru
from app.models.lekhana import LekhanaSession
from app.services.lekhana_service import create_session, save_entry, complete_session
from app.services.pdf_service import generate_acknowledgement
import io

lekhana_bp = Blueprint('lekhana', __name__)


@lekhana_bp.route('/')
def index():
    """Select a Guru page — shows all verified Gurus."""
    gurus = (Guru.query
             .filter_by(is_active=True, is_verified=True)
             .order_by(Guru.guru_order.asc())
             .all())
    return render_template('lekhana/selection.html', gurus=gurus)


@lekhana_bp.route('/<guru_slug>')
def selection(guru_slug):
    """Select Lekhana for a specific Guru."""
    guru = Guru.query.filter_by(slug=guru_slug, is_active=True, is_verified=True).first_or_404()
    return render_template('lekhana/selection.html', gurus=[guru])


@lekhana_bp.route('/<guru_slug>/start', methods=['POST'])
def start(guru_slug):
    """Create a new Lekhana session and redirect to the writing pad."""
    guru = Guru.query.filter_by(slug=guru_slug, is_active=True, is_verified=True).first_or_404()

    mode = request.form.get('mode', 'type').strip()
    if mode not in ('type', 'handwrite', 'mobile'):
        mode = 'type'

    try:
        target_count = int(request.form.get('target_count', 108))
        if target_count not in (11, 21, 51, 108, 1008):
            target_count = 108
    except (ValueError, TypeError):
        target_count = 108

    language = request.form.get('language', 'en')
    user_id = current_user.id if current_user.is_authenticated else None

    session_obj = create_session(guru.id, user_id, mode, target_count, language)
    return redirect(url_for('lekhana.pad', uuid=session_obj.session_uuid))


@lekhana_bp.route('/session/<uuid>')
def pad(uuid):
    """Writing pad — the main Lekhana writing interface."""
    session_obj = LekhanaSession.query.filter_by(session_uuid=uuid).first_or_404()
    if session_obj.is_completed:
        return redirect(url_for('lekhana.done', uuid=uuid))

    # Eager-load the guru
    guru = Guru.query.get(session_obj.guru_id)
    if not guru:
        abort(404)

    return render_template('lekhana/pad.html', session=session_obj, guru=guru)


@lekhana_bp.route('/session/<uuid>/entry', methods=['POST'])
def entry(uuid):
    """AJAX: save one Lekhana entry, return updated count."""
    session_obj = LekhanaSession.query.filter_by(session_uuid=uuid).first_or_404()

    if session_obj.is_completed:
        return jsonify({'error': 'Session already completed.'}), 400

    data = request.get_json(silent=True) or {}
    typed_text = data.get('typed_text')
    drawing_data = data.get('drawing_data')
    mode = data.get('mode', session_obj.mode)

    # Basic input size guards
    if typed_text and len(typed_text) > 2000:
        return jsonify({'error': 'Text too long.'}), 400
    if drawing_data and len(drawing_data) > 2 * 1024 * 1024:  # 2MB
        return jsonify({'error': 'Drawing data too large.'}), 400

    entry_obj, count = save_entry(session_obj.id, mode, typed_text, drawing_data)

    return jsonify({
        'success': True,
        'completed_count': count,
        'target_count': session_obj.target_count,
        'is_completed': session_obj.is_completed
    })


@lekhana_bp.route('/session/<uuid>/complete', methods=['POST'])
def complete(uuid):
    """Mark the session as completed."""
    session_obj = LekhanaSession.query.filter_by(session_uuid=uuid).first_or_404()
    complete_session(session_obj.id)
    return jsonify({
        'success': True,
        'redirect': url_for('lekhana.done', uuid=uuid)
    })


@lekhana_bp.route('/session/<uuid>/done')
def done(uuid):
    """Completion / acknowledgement page."""
    session_obj = LekhanaSession.query.filter_by(session_uuid=uuid).first_or_404()
    guru = Guru.query.get(session_obj.guru_id)
    return render_template('lekhana/done.html', session=session_obj, guru=guru)


@lekhana_bp.route('/session/<uuid>/certificate')
def certificate(uuid):
    """Generate and download PDF acknowledgement."""
    session_obj = LekhanaSession.query.filter_by(session_uuid=uuid).first_or_404()

    try:
        pdf_bytes = generate_acknowledgement(session_obj)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'guru_lekhana_seva_acknowledgement_{uuid[:8]}.pdf'
        )
    except Exception as e:
        flash('Could not generate acknowledgement. Please try again.', 'danger')
        return redirect(url_for('lekhana.done', uuid=uuid))
