"""
Search Service — Global search across Gurus, Books, Articles, Media, Events.
"""
from app.models.guru import Guru
from app.models.content import Book, Article, Media, CalendarEvent
from flask import url_for


def global_search(query: str) -> dict:
    """
    Search all content types for the query string.
    Returns dict with keys: gurus, books, articles, media, events, total
    """
    if not query or len(query.strip()) < 2:
        return {'gurus': [], 'books': [], 'articles': [], 'media': [], 'events': [], 'total': 0}

    q = f"%{query.strip()}%"

    gurus = Guru.query.filter(
        Guru.is_verified == True,
        Guru.is_active == True,
        (Guru.name.ilike(q) | Guru.traditional_name.ilike(q) |
         Guru.short_description.ilike(q) | Guru.lekhana_text.ilike(q))
    ).limit(10).all()

    books = Book.query.filter(
        Book.is_active == True,
        (Book.title.ilike(q) | Book.author.ilike(q) | Book.description.ilike(q))
    ).limit(8).all()

    articles = Article.query.filter(
        Article.is_active == True,
        (Article.title.ilike(q) | Article.author.ilike(q))
    ).limit(8).all()

    media = Media.query.filter(
        Media.is_active == True,
        (Media.title.ilike(q) | Media.speaker.ilike(q) | Media.topic.ilike(q))
    ).limit(8).all()

    events = CalendarEvent.query.filter(
        CalendarEvent.is_active == True,
        (CalendarEvent.title.ilike(q) | CalendarEvent.description.ilike(q))
    ).limit(5).all()

    total = len(gurus) + len(books) + len(articles) + len(media) + len(events)
    return {
        'gurus': gurus,
        'books': books,
        'articles': articles,
        'media': media,
        'events': events,
        'total': total,
        'query': query.strip()
    }


def autocomplete(query: str, limit: int = 8) -> list:
    """
    Fast autocomplete search — returns list of dicts with type, title, url.
    """
    if not query or len(query.strip()) < 2:
        return []

    q = f"%{query.strip()}%"
    results = []

    # Gurus
    gurus = Guru.query.filter(
        Guru.is_verified == True,
        Guru.is_active == True,
        Guru.name.ilike(q)
    ).limit(4).all()
    for g in gurus:
        results.append({
            'type': 'Guru',
            'title': g.name,
            'subtitle': f"Guru #{g.guru_order}",
            'url': f"/guru/{g.slug}"
        })

    # Books
    remaining = limit - len(results)
    if remaining > 0:
        books = Book.query.filter(
            Book.is_active == True,
            Book.title.ilike(q)
        ).limit(remaining).all()
        for b in books:
            results.append({
                'type': 'Book',
                'title': b.title,
                'subtitle': b.author or '',
                'url': f"/granthalaya/book/{b.id}"
            })

    # Articles
    remaining = limit - len(results)
    if remaining > 0:
        articles = Article.query.filter(
            Article.is_active == True,
            Article.title.ilike(q)
        ).limit(remaining).all()
        for a in articles:
            results.append({
                'type': 'Article',
                'title': a.title,
                'subtitle': a.author or '',
                'url': f"/granthalaya/article/{a.id}"
            })

    return results[:limit]
