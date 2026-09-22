"""
Comprehensive end-to-end test suite for Uttaradi Math — Guru Lekhana Seva platform
"""
import sys
import os

# Set UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.user import User, AdminUser
from app.models.guru import Guru
from app.models.lekhana import LekhanaSession, LekhanaEntry, SevaProgress
from app.models.content import Book, Media, CalendarEvent

def run_tests():
    app = create_app('development')
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for programmatic test client
    client = app.test_client()
    
    passed = 0
    failed = 0
    
    def report(name, condition, details=""):
        nonlocal passed, failed
        if condition:
            print(f"[PASS] {name}")
            passed += 1
        else:
            print(f"[FAIL] {name} - {details}")
            failed += 1

    with app.app_context():
        print("=" * 60)
        print("  RUNNING E2E TEST SUITE — UTTARADI MATH")
        print("=" * 60)

        # 1. Homepage
        res = client.get('/')
        report("Homepage Loads", res.status_code == 200)
        report("Homepage Contains Lotus & Brand", "Uttaradi Math".encode('utf-8') in res.data)

        # 2. Guru Parampara Page
        res = client.get('/guru/')
        report("Guru Parampara Page", res.status_code == 200 and "Guru Parampara".encode('utf-8') in res.data)

        # 3. Guru Profile Page (First Guru)
        first_guru = Guru.query.order_by(Guru.guru_order.asc()).first()
        if first_guru:
            prev_v = first_guru.is_verified
            first_guru.is_verified = True
            db.session.commit()

            res = client.get(f'/guru/{first_guru.slug}')
            report(f"Guru Profile ({first_guru.name})", res.status_code == 200)
            report("Guru Profile Tabs Present", b"tab-about" in res.data and b"tab-lekhana" in res.data)

            # 4. Lekhana Selection Page
            res = client.get('/lekhana/')
            report("Lekhana Selection Page", res.status_code == 200 and "Guru Lekhana Seva".encode('utf-8') in res.data)

            # 5. Start Lekhana Session
            res = client.post(f'/lekhana/{first_guru.slug}/start', data={
                'target_count': '11',
                'mode': 'type'
            }, follow_redirects=False)
            
            report("Start Lekhana Session Redirect", res.status_code == 302 and '/lekhana/session/' in res.headers['Location'])
            
            session_url = res.headers['Location']
            uuid = session_url.split('/lekhana/session/')[1]
            
            # 6. Writing Pad
            res = client.get(session_url)
            report("Lekhana Pad View", res.status_code == 200 and b"lekhana-pad-root" in res.data)
            
            # 7. AJAX Lekhana Entry Submission
            res = client.post(f'/lekhana/session/{uuid}/entry', json={
                'typed_text': first_guru.lekhana_text or 'Sri Rama'
            })
            report("Submit Lekhana Entry (AJAX)", res.status_code == 200 and res.json.get('success') is True)
            
            # 8. Complete Session
            res = client.post(f'/lekhana/session/{uuid}/complete')
            report("Complete Lekhana Session", res.status_code == 200 and res.json.get('success') is True)
            
            # 9. Done Page
            res = client.get(f'/lekhana/session/{uuid}/done')
            report("Lekhana Done / Acknowledgement Page", res.status_code == 200 and "Lekhana Seva Completed".encode('utf-8') in res.data)
            
            # 10. PDF Acknowledgement Download
            res = client.get(f'/lekhana/session/{uuid}/certificate')
            report("Download PDF Acknowledgement", res.status_code == 200 and res.content_type == 'application/pdf')

            # Restore original verification
            first_guru.is_verified = prev_v
            db.session.commit()
        else:
            report("Guru Profile Flow", False, "No gurus found")

        # 11. Global Search & Autocomplete
        res = client.get('/search/?q=madhva')
        report("Search Results Page", res.status_code == 200)
        
        res = client.get('/search/autocomplete?q=madhva')
        report("Search Autocomplete API", res.status_code == 200 and isinstance(res.json, list))

        # 15. Guru Jijnasa AI Assistant
        res = client.get('/guru-jijnasa/')
        report("Guru Jijnasa AI Page", res.status_code == 200 and "Guru Jijnasa".encode('utf-8') in res.data)
        
        res = client.post('/guru-jijnasa/ask', json={'question': 'Who is Sri Madhvacharya?'})
        report("Guru Jijnasa Ask Endpoint", res.status_code == 200 and 'answer' in res.json)

        # 16. Devotee Authentication Flow
        test_email = 'bhakta_test@example.com'
        User.query.filter_by(email=test_email).delete()
        db.session.commit()

        # Register
        res = client.post('/auth/register', data={
            'name': 'Test Bhakta',
            'email': test_email,
            'password': 'Password@123'
        }, follow_redirects=True)
        report("Devotee Registration", res.status_code == 200 and b"Registration successful" in res.data)

        # Login
        res = client.post('/auth/login', data={
            'email': test_email,
            'password': 'Password@123'
        }, follow_redirects=True)
        report("Devotee Login", res.status_code == 200 and b"Logged in successfully" in res.data)

        # My Seva Dashboard
        res = client.get('/my-seva')
        report("My Seva Dashboard (Authenticated)", res.status_code == 200 and b"Test Bhakta" in res.data)

        # Logout
        res = client.get('/auth/logout', follow_redirects=True)
        report("Devotee Logout", res.status_code == 200 and b"logged out" in res.data)

        # 17. Admin Flow
        res = client.get('/admin/')
        report("Admin Login Redirect When Unauthenticated", res.status_code in (302, 308))

        # Login Admin
        res = client.post('/admin/login', data={
            'email': 'admin@uttaradi-math.local',
            'password': os.environ.get('ADMIN_PASSWORD', 'Admin@1234!')
        }, follow_redirects=True)
        report("Admin Login", res.status_code == 200 and b"Dashboard" in res.data)

        # Admin Gurus List
        res = client.get('/admin/gurus')
        report("Admin Gurus Management", res.status_code == 200 and b"Guru" in res.data)

        # Admin Content Pages
        res = client.get('/admin/content/books')
        report("Admin Books List", res.status_code == 200 and b"Books" in res.data)

        res = client.get('/admin/content/media')
        report("Admin Media List", res.status_code == 200 and b"Media" in res.data)

        res = client.get('/admin/content/events')
        report("Admin Events List", res.status_code == 200 and b"Events" in res.data)

        res = client.get('/admin/users')
        report("Admin Users List", res.status_code == 200 and b"Devotee Users" in res.data)

        res = client.get('/admin/analytics')
        report("Admin Analytics View", res.status_code == 200 and b"Analytics" in res.data)

        res = client.get('/admin/ai-knowledge-base')
        report("Admin AI Knowledge Base", res.status_code == 200 and b"Knowledge Base" in res.data)

        # Admin Logout
        res = client.get('/admin/logout', follow_redirects=True)
        report("Admin Logout", res.status_code == 200 and b"logged out" in res.data)

        print("=" * 60)
        print(f"  RESULTS: {passed} PASSED, {failed} FAILED")
        print("=" * 60)

        # Clean up test user
        User.query.filter_by(email=test_email).delete()
        db.session.commit()

        return failed == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
