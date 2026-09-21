from flask import Blueprint, render_template, request
from app.models.content import Media

pravachana_bp = Blueprint('pravachana', __name__)

LANGUAGES = ['English', 'Kannada', 'Sanskrit', 'Hindi']


@pravachana_bp.route('/')
def index():
    """Pravachana (discourse) listing page."""
    search_q = request.args.get('q', '').strip()
    language = request.args.get('language', '').strip()
    media_type = request.args.get('type', '').strip()
    speaker = request.args.get('speaker', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Media.query.filter_by(is_active=True)

    if search_q:
        query = query.filter(
            (Media.title.ilike(f'%{search_q}%')) |
            (Media.speaker.ilike(f'%{search_q}%')) |
            (Media.topic.ilike(f'%{search_q}%'))
        )
    if language:
        query = query.filter(Media.language.ilike(f'%{language}%'))
    if media_type in ('video', 'audio'):
        query = query.filter(Media.media_type == media_type)
    if speaker:
        query = query.filter(Media.speaker.ilike(f'%{speaker}%'))

    media = query.order_by(Media.created_at.desc()).paginate(page=page, per_page=12, error_out=False)

    # Unique speakers for filter
    speakers = [m[0] for m in Media.query.filter_by(is_active=True)
                .with_entities(Media.speaker).distinct().all() if m[0]]

    return render_template(
        'pravachana/index.html',
        media=media,
        languages=LANGUAGES,
        speakers=speakers,
        search_q=search_q,
        selected_language=language,
        selected_type=media_type
    )


@pravachana_bp.route('/<int:media_id>')
def detail(media_id):
    item = Media.query.filter_by(id=media_id, is_active=True).first_or_404()
    return render_template('pravachana/detail.html', media=item)
