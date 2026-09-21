from flask import Blueprint, render_template, request, jsonify
from app.models.content import CalendarEvent
from datetime import datetime, date

calendar_bp = Blueprint('calendar_bp', __name__)


@calendar_bp.route('/')
def index():
    """Calendar main page."""
    today = date.today()
    # Upcoming events (next 60 days)
    upcoming = (CalendarEvent.query
                .filter(CalendarEvent.is_active == True,
                        CalendarEvent.event_date >= today)
                .order_by(CalendarEvent.event_date.asc())
                .limit(20).all())

    # Current month for initial display
    current_month = today.month
    current_year = today.year

    return render_template(
        'calendar/index.html',
        upcoming=upcoming,
        current_month=current_month,
        current_year=current_year,
        today=today
    )


@calendar_bp.route('/events')
def events_api():
    """AJAX endpoint: return events for a given month/year as JSON."""
    try:
        month = int(request.args.get('month', date.today().month))
        year = int(request.args.get('year', date.today().year))
    except ValueError:
        return jsonify({'error': 'Invalid month or year'}), 400

    # Date range for the month
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    events = (CalendarEvent.query
              .filter(CalendarEvent.is_active == True,
                      CalendarEvent.event_date >= start,
                      CalendarEvent.event_date < end)
              .order_by(CalendarEvent.event_date.asc())
              .all())

    return jsonify([{
        'id': e.id,
        'title': e.title,
        'date': e.event_date.isoformat(),
        'day': e.event_date.day,
        'tithi': e.tithi,
        'event_type': e.event_type,
        'description': e.description,
        'guru_name': e.guru.name if e.guru else None,
    } for e in events])
