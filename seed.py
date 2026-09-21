"""
Seed Script â€” Uttaradi Math Guru Lekhana Seva
=============================================

Creates:
  - Database tables
  - Default admin user
  - 5 placeholder Guru records (is_verified=False)
  - Sample calendar events
  - Sample books
  - Sample media

IMPORTANT:
  All Guru content is marked as PLACEHOLDER.
  NO real Guru names, Lekhana, or historical details are invented.
  The administrator must replace all placeholder content with verified data.

Usage:
  python seed.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Ensure app is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User, AdminUser
from app.models.guru import Guru, GuruWork, GuruSource
from app.models.content import Book, Article, Media, CalendarEvent
from datetime import date


def create_tables(app):
    with app.app_context():
        db.create_all()
        print("âœ“ Database tables created.")


def create_admin(app):
    with app.app_context():
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')
        admin_name = os.environ.get('ADMIN_NAME', 'Administrator')

        existing = AdminUser.query.filter_by(email=admin_email).first()
        if existing:
            print(f"  Admin already exists: {admin_email}")
            return existing

        admin = AdminUser(
            name=admin_name,
            email=admin_email,
            role='super_admin',
            is_active=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"âœ“ Admin created: {admin_email} (role: super_admin)")
        print(f"  âš  IMPORTANT: Change the admin password in .env before deployment!")
        return admin


def create_placeholder_gurus(app):
    """
    Create clearly-marked placeholder Guru records.
    ALL fields are placeholders â€” admin must replace with verified content.
    """
    with app.app_context():
        if Guru.query.count() > 0:
            print("  Gurus already exist, skipping placeholder creation.")
            return

        placeholder_gurus = [
            {
                'guru_order': 1,
                'name': '[PLACEHOLDER] Guru Parampara â€” Member 1',
                'traditional_name': '[Awaiting Verified Sanskrit Name]',
                'slug': 'guru-placeholder-1',
                'short_description': (
                    'This is a placeholder record. The administrator must replace this with '
                    'the verified name, biography, and information of the first Guru in the Parampara.'
                ),
                'biography': (
                    'This Guru\'s verified biography has not yet been entered by the administrator. '
                    'Please log in to /admin and update this record with accurate, source-verified '
                    'information. Do not publish placeholder content.'
                ),
                'birth_date': '[Awaiting Verified Date]',
                'aradhana_date': '[Awaiting Verified Date]',
                'lekhana_text': '[LEKHANA TEXT â€” AWAITING ADMIN VERIFICATION. Do not display publicly.]',
                'lekhana_sanskrit': '[Sanskrit Lekhana â€” Awaiting Verification]',
                'lekhana_kannada': '[à²•à²¨à³à²¨à²¡ à²²à³‡à²–à²¨ â€” à²ªà²°à²¿à²¶à³€à²²à²¨à³† à²¬à²¾à²•à²¿]',
                'lekhana_english': '[English Translation â€” Awaiting Verification]',
                'is_verified': False,
            },
            {
                'guru_order': 2,
                'name': '[PLACEHOLDER] Guru Parampara â€” Member 2',
                'traditional_name': '[Awaiting Verified Sanskrit Name]',
                'slug': 'guru-placeholder-2',
                'short_description': (
                    'Placeholder record. Administrator must replace with verified content.'
                ),
                'biography': (
                    'This Guru\'s verified biography has not yet been entered. '
                    'Please update via the admin panel with source-verified information.'
                ),
                'birth_date': '[Awaiting Verified Date]',
                'aradhana_date': '[Awaiting Verified Date]',
                'lekhana_text': '[LEKHANA TEXT â€” AWAITING ADMIN VERIFICATION]',
                'lekhana_sanskrit': '[Sanskrit Lekhana â€” Awaiting Verification]',
                'lekhana_kannada': '[à²•à²¨à³à²¨à²¡ à²²à³‡à²–à²¨ â€” à²ªà²°à²¿à²¶à³€à²²à²¨à³† à²¬à²¾à²•à²¿]',
                'lekhana_english': '[English Translation â€” Awaiting Verification]',
                'is_verified': False,
            },
            {
                'guru_order': 3,
                'name': '[PLACEHOLDER] Guru Parampara â€” Member 3',
                'traditional_name': '[Awaiting Verified Sanskrit Name]',
                'slug': 'guru-placeholder-3',
                'short_description': (
                    'Placeholder record. Administrator must replace with verified content.'
                ),
                'biography': (
                    'This Guru\'s verified biography has not yet been entered. '
                    'Please update via the admin panel.'
                ),
                'birth_date': '[Awaiting Verified Date]',
                'aradhana_date': '[Awaiting Verified Date]',
                'lekhana_text': '[LEKHANA TEXT â€” AWAITING ADMIN VERIFICATION]',
                'lekhana_sanskrit': '[Sanskrit Lekhana â€” Awaiting Verification]',
                'lekhana_kannada': '[à²•à²¨à³à²¨à²¡ à²²à³‡à²–à²¨ â€” à²ªà²°à²¿à²¶à³€à²²à²¨à³† à²¬à²¾à²•à²¿]',
                'lekhana_english': '[English Translation â€” Awaiting Verification]',
                'is_verified': False,
            },
            {
                'guru_order': 4,
                'name': '[PLACEHOLDER] Guru Parampara â€” Member 4',
                'traditional_name': '[Awaiting Verified Sanskrit Name]',
                'slug': 'guru-placeholder-4',
                'short_description': (
                    'Placeholder record. Administrator must replace with verified content.'
                ),
                'biography': (
                    'This Guru\'s verified biography has not yet been entered. '
                    'Please update via the admin panel.'
                ),
                'birth_date': '[Awaiting Verified Date]',
                'aradhana_date': '[Awaiting Verified Date]',
                'lekhana_text': '[LEKHANA TEXT â€” AWAITING ADMIN VERIFICATION]',
                'lekhana_sanskrit': '[Sanskrit Lekhana â€” Awaiting Verification]',
                'lekhana_kannada': '[à²•à²¨à³à²¨à²¡ à²²à³‡à²–à²¨ â€” à²ªà²°à²¿à²¶à³€à²²à²¨à³† à²¬à²¾à²•à²¿]',
                'lekhana_english': '[English Translation â€” Awaiting Verification]',
                'is_verified': False,
            },
            {
                'guru_order': 5,
                'name': '[PLACEHOLDER] Guru Parampara â€” Member 5',
                'traditional_name': '[Awaiting Verified Sanskrit Name]',
                'slug': 'guru-placeholder-5',
                'short_description': (
                    'Placeholder record. Administrator must replace with verified content.'
                ),
                'biography': (
                    'This Guru\'s verified biography has not yet been entered. '
                    'Please update via the admin panel.'
                ),
                'birth_date': '[Awaiting Verified Date]',
                'aradhana_date': '[Awaiting Verified Date]',
                'lekhana_text': '[LEKHANA TEXT â€” AWAITING ADMIN VERIFICATION]',
                'lekhana_sanskrit': '[Sanskrit Lekhana â€” Awaiting Verification]',
                'lekhana_kannada': '[à²•à²¨à³à²¨à²¡ à²²à³‡à²–à²¨ â€” à²ªà²°à²¿à²¶à³€à²²à²¨à³† à²¬à²¾à²•à²¿]',
                'lekhana_english': '[English Translation â€” Awaiting Verification]',
                'is_verified': False,
            },
        ]

        created = []
        for data in placeholder_gurus:
            guru = Guru(**data)
            db.session.add(guru)
            created.append(guru)

        db.session.flush()  # Get IDs before commit

        # Link previous/next
        for i, guru in enumerate(created):
            if i > 0:
                guru.previous_guru_id = created[i - 1].id
            if i < len(created) - 1:
                guru.next_guru_id = created[i + 1].id

        db.session.commit()
        print(f"âœ“ Created {len(created)} placeholder Guru records (is_verified=False).")
        print("  âš  IMPORTANT: These are placeholders. Update via /admin with verified content.")


def create_sample_events(app):
    with app.app_context():
        if CalendarEvent.query.count() > 0:
            print("  Calendar events already exist, skipping.")
            return

        events = [
            CalendarEvent(
                title='[PLACEHOLDER] Guru Aradhana â€” Sample Event 1',
                event_date=date(2025, 1, 15),
                tithi='[Placeholder Tithi]',
                event_type='aradhana',
                description='This is a sample placeholder event. Replace with verified dates and details.',
                is_active=True,
            ),
            CalendarEvent(
                title='[PLACEHOLDER] Guru Aradhana â€” Sample Event 2',
                event_date=date(2025, 3, 20),
                tithi='[Placeholder Tithi]',
                event_type='festival',
                description='This is a sample placeholder event. Replace with verified dates and details.',
                is_active=True,
            ),
            CalendarEvent(
                title='[PLACEHOLDER] Guru Jayanthi â€” Sample Event 3',
                event_date=date(2025, 6, 10),
                tithi='[Placeholder Tithi]',
                event_type='event',
                description='Sample event placeholder. Admin must update with verified information.',
                is_active=True,
            ),
        ]
        for event in events:
            db.session.add(event)
        db.session.commit()
        print(f"âœ“ Created {len(events)} placeholder calendar events.")


def create_sample_books(app):
    with app.app_context():
        if Book.query.count() > 0:
            print("  Books already exist, skipping.")
            return

        books = [
            Book(
                title='[PLACEHOLDER] Introduction to Dvaita Vedanta',
                author='[Author â€” Awaiting Admin Entry]',
                category='Dvaita Vedanta',
                language='English',
                description=(
                    'This is a placeholder book entry. The administrator must replace this '
                    'with a real book with proper attribution and verified information.'
                ),
                is_active=True,
            ),
            Book(
                title='[PLACEHOLDER] Guru Parampara â€” Reference Work',
                author='[Author â€” Awaiting Admin Entry]',
                category='Guru Parampara',
                language='Kannada',
                description=(
                    'Placeholder entry for Granthalaya. Replace with verified content.'
                ),
                is_active=True,
            ),
        ]
        for book in books:
            db.session.add(book)
        db.session.commit()
        print(f"âœ“ Created {len(books)} placeholder book entries.")


def create_sample_media(app):
    with app.app_context():
        if Media.query.count() > 0:
            print("  Media already exists, skipping.")
            return

        media_items = [
            Media(
                title='[PLACEHOLDER] Introduction Pravachana',
                speaker='[Speaker â€” Awaiting Admin Entry]',
                topic='[Topic â€” Awaiting Admin Entry]',
                language='Kannada',
                media_type='video',
                embed_url='',
                duration='',
                is_active=True,
            ),
        ]
        for item in media_items:
            db.session.add(item)
        db.session.commit()
        print(f"âœ“ Created {len(media_items)} placeholder media entries.")


def create_directories():
    """Create required upload and AI directories."""
    dirs = [
        'uploads/gurus',
        'uploads/books',
        'uploads/media',
        'uploads/ai_docs',
        'ai/chroma_db',
        'flask_session',
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print(f"âœ“ Created {len(dirs)} required directories.")


def main():
    print("\n" + "="*60)
    print("  Uttaradi Math â€” Guru Lekhana Seva: Database Seeder")
    print("="*60 + "\n")

    env = os.environ.get('FLASK_ENV', 'development')
    print(f"Environment: {env}\n")

    app = create_app(env)

    print("Creating directories...")
    create_directories()

    print("Creating database tables...")
    create_tables(app)

    print("Creating admin user...")
    create_admin(app)

    print("Creating placeholder Gurus...")
    create_placeholder_gurus(app)

    print("Creating sample calendar events...")
    create_sample_events(app)

    print("Creating sample books...")
    create_sample_books(app)

    print("Creating sample media...")
    create_sample_media(app)

    print("\n" + "="*60)
    print("  Seeding complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Set GEMINI_API_KEY in .env for AI features")
    print("  2. Log in to /admin to add verified Guru data")
    print("  3. Replace ALL placeholder content with verified information")
    print("  4. Mark Gurus as 'verified' in the admin panel to make them public")
    print("  5. Never publish placeholder content to devotees")
    print("\n  Admin login: " + os.environ.get('ADMIN_EMAIL', 'admin@example.com'))
    print("  Admin password: Set in .env (ADMIN_PASSWORD)")
    print("")


if __name__ == '__main__':
    main()

