from flask import Blueprint, render_template, request, jsonify, abort
from app.models.content import Book, Article

granthalaya_bp = Blueprint('granthalaya', __name__)

CATEGORIES = [
    'Guru Parampara', 'Dvaita Vedanta', 'Stotras',
    'Sanskrit Texts', 'Kannada Texts', 'English Resources',
    'Articles', 'Books', 'PDFs'
]

LANGUAGES = ['English', 'Kannada', 'Sanskrit', 'Hindi']


@granthalaya_bp.route('/')
def index():
    """Digital library — books and articles."""
    search_q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    language = request.args.get('language', '').strip()
    page = request.args.get('page', 1, type=int)

    book_query = Book.query.filter_by(is_active=True)
    article_query = Article.query.filter_by(is_active=True)

    if search_q:
        book_query = book_query.filter(
            (Book.title.ilike(f'%{search_q}%')) |
            (Book.author.ilike(f'%{search_q}%')) |
            (Book.description.ilike(f'%{search_q}%'))
        )
        article_query = article_query.filter(
            (Article.title.ilike(f'%{search_q}%')) |
            (Article.author.ilike(f'%{search_q}%'))
        )

    if category:
        book_query = book_query.filter(Book.category == category)
        article_query = article_query.filter(Article.category == category)

    if language:
        book_query = book_query.filter(Book.language.ilike(f'%{language}%'))
        article_query = article_query.filter(Article.language.ilike(f'%{language}%'))

    books = book_query.order_by(Book.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    articles = article_query.order_by(Article.created_at.desc()).limit(10).all()

    return render_template(
        'granthalaya/index.html',
        books=books,
        articles=articles,
        categories=CATEGORIES,
        languages=LANGUAGES,
        search_q=search_q,
        selected_category=category,
        selected_language=language
    )


@granthalaya_bp.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.filter_by(id=book_id, is_active=True).first_or_404()
    return render_template('granthalaya/book_detail.html', book=book)


@granthalaya_bp.route('/article/<int:article_id>')
def article_detail(article_id):
    article = Article.query.filter_by(id=article_id, is_active=True).first_or_404()
    return render_template('granthalaya/article_detail.html', article=article)
