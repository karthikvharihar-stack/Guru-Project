from flask import Blueprint, render_template
from app.models.guru import Guru
from app.models.content import CalendarEvent, Book
from datetime import datetime, date

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # Today's guru: pick based on day-of-year cycling through verified gurus
    verified_gurus = (Guru.query
                      .filter_by(is_active=True, is_verified=True)
                      .order_by(Guru.guru_order.asc())
                      .all())

    today_guru = None
    if verified_gurus:
        day_index = datetime.utcnow().timetuple().tm_yday
        today_guru = verified_gurus[day_index % len(verified_gurus)]

    # Recent gurus for parampara preview (first 6)
    recent_gurus = verified_gurus[:6]

    # Upcoming events
    upcoming_events = (CalendarEvent.query
                       .filter(CalendarEvent.is_active == True,
                               CalendarEvent.event_date >= date.today())
                       .order_by(CalendarEvent.event_date.asc())
                       .limit(3).all())

    # Featured books
    featured_books = (Book.query
                      .filter_by(is_active=True)
                      .order_by(Book.created_at.desc())
                      .limit(3).all())

    return render_template(
        'index.html',
        today_guru=today_guru,
        recent_gurus=recent_gurus,
        upcoming_events=upcoming_events,
        featured_books=featured_books
    )


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    return render_template('contact.html')


@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')


@main_bp.route('/terms')
def terms():
    return render_template('terms.html')


@main_bp.route('/sitemap.xml')
def sitemap():
    from flask import Response
    gurus = Guru.query.filter_by(is_active=True, is_verified=True).all()
    urls = [
        'https://uttaradi-math.example.com/',
        'https://uttaradi-math.example.com/guru',
        'https://uttaradi-math.example.com/lekhana',
        'https://uttaradi-math.example.com/granthalaya',
        'https://uttaradi-math.example.com/pravachana',
        'https://uttaradi-math.example.com/calendar',
        'https://uttaradi-math.example.com/guru-jijnasa',
        'https://uttaradi-math.example.com/about',
    ]
    for guru in gurus:
        urls.append(f'https://uttaradi-math.example.com/guru/{guru.slug}')
        urls.append(f'https://uttaradi-math.example.com/lekhana/{guru.slug}')

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml += f'  <url><loc>{url}</loc></url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')


@main_bp.route('/robots.txt')
def robots():
    from flask import Response
    content = "User-agent: *\nDisallow: /admin/\nDisallow: /auth/\nSitemap: https://uttaradi-math.example.com/sitemap.xml"
    return Response(content, mimetype='text/plain')


# ── DIGITAL DEEPA LIVE API ───────────────────────────────────────────────────

def _get_deepa_file():
    import os
    from flask import current_app
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    return os.path.join(upload_folder, 'deepas.json')


def _load_deepa_data():
    import json, os
    file_path = _get_deepa_file()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    # Default initial state with a sacred baseline count
    return {
        'count': 108,
        'diyas': [
            {'name': 'Sri Devotee', 'prayer': 'Guru Smarana & Lokakshema', 'time': 'Just now'},
            {'name': 'Bhakta', 'prayer': 'Sri Moola Rama Kripa', 'time': 'Today'},
            {'name': 'Hari Bhakta', 'prayer': 'Vidya & Jnana Prapti', 'time': 'Today'}
        ]
    }


def _save_deepa_data(data):
    import json
    file_path = _get_deepa_file()
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


@main_bp.route('/api/deepa', methods=['GET'])
def get_deepas():
    from flask import jsonify
    data = _load_deepa_data()
    return jsonify(data)


from app.extensions import csrf

@main_bp.route('/api/deepa/light', methods=['POST'])
@csrf.exempt
def light_deepa():
    from flask import request, jsonify
    from datetime import datetime
    req_data = request.get_json(silent=True) or {}
    name = (req_data.get('name') or 'A Devotee').strip()[:60]
    prayer = (req_data.get('prayer') or 'Guru Smarana & Peace').strip()[:140]

    data = _load_deepa_data()
    data['count'] = data.get('count', 108) + 1

    new_diya = {
        'name': name or 'A Devotee',
        'prayer': prayer or 'Guru Smarana & Peace',
        'time': datetime.now().strftime('%d %b, %I:%M %p')
    }

    diyas = data.get('diyas', [])
    diyas.insert(0, new_diya)
    data['diyas'] = diyas[:50]  # Keep latest 50

    _save_deepa_data(data)

    return jsonify({
        'success': True,
        'count': data['count'],
        'diya': new_diya,
        'message': '॥ श्री मूलरामो विजयते ॥ Deepa offered successfully!'
    })
