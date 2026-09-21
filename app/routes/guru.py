from flask import Blueprint, render_template, request, jsonify
from app.models.guru import Guru
from app.models.content import Book, Article, Media

guru_bp = Blueprint('guru', __name__)


@guru_bp.route('/')
def parampara():
    """Guru Parampara — display all verified gurus in order."""
    gurus = (Guru.query
             .filter_by(is_active=True, is_verified=True)
             .order_by(Guru.guru_order.asc())
             .all())
    # Show draft notice only in admin; public sees only verified
    return render_template('guru/parampara.html', gurus=gurus)


@guru_bp.route('/<slug>')
def profile(slug):
    """Individual Guru profile page."""
    guru = Guru.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Only show unverified to admin; redirect public to 404
    if not guru.is_verified:
        from flask import abort, session
        if not session.get('admin_logged_in'):
            abort(404)

    # Related media — search by guru name
    related_media = (Media.query
                     .filter(Media.speaker.ilike(f'%{guru.name}%'), Media.is_active == True)
                     .limit(6).all())

    return render_template(
        'guru/profile.html',
        guru=guru,
        related_media=related_media
    )
