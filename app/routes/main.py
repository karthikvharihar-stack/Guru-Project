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
