from flask import Blueprint, render_template, request, jsonify
from app.services.search_service import global_search, autocomplete

search_bp = Blueprint('search', __name__)


@search_bp.route('/')
def index():
    """Full search results page."""
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('search/index.html', results=None, query='')

    results = global_search(query)
    return render_template('search/index.html', results=results, query=query)


@search_bp.route('/autocomplete')
def autocomplete_api():
    """AJAX autocomplete endpoint."""
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 8)), 20)

    if len(query) < 2:
        return jsonify([])

    suggestions = autocomplete(query, limit=limit)
    return jsonify(suggestions)
