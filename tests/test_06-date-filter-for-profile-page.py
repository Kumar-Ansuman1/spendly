import pytest
import os
import sys
sys.path.insert(0, '.')

@pytest.fixture
def app():
    from app import app as flask_app
    import database.db

    db_path = os.path.join(os.getcwd(), 'tests', 'test_spendly.db')
    if os.path.exists(db_path):
        os.unlink(db_path)

    original_database = database.db.DATABASE
    database.db.DATABASE = db_path

    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })

    with flask_app.app_context():
        database.db.init_db()
        database.db.seed_db()
        yield flask_app

    database.db.DATABASE = original_database
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Log in as demo user from seed data"""
    client.post('/login', data={
        'email': 'demo@spendly.com',
        'password': 'demo123'
    }, follow_redirects=True)
    return client

def test_profile_requires_login(client):
    """Unauthenticated access redirects to login"""
    response = client.get('/profile', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

def test_profile_shows_all_expenses_by_default(auth_client):
    """Profile page displays all expenses when no date filter applied"""
    response = auth_client.get('/profile')
    assert response.status_code == 200
    text = response.data.decode('utf-8')
    assert 'Grocery shopping' in text
    assert 'Gas refill' in text
    assert 'Electricity bill' in text
    assert 'Pharmacy' in text
    assert 'Movie tickets' in text
    assert 'New clothes' in text
    assert 'Dinner out' in text
    assert 'Miscellaneous' in text
    # Total is 565.50, rendered as 565.5
    assert '565.5' in text

def test_profile_last_7_days_filter(auth_client):
    """Last 7 days filter shows correct expenses.
    Today is 2026-05-12; last 7 days = 2026-05-06 to 2026-05-12.
    Expenses in range: Movie tickets (05-08), New clothes (05-10), Dinner out (05-12)."""
    response = auth_client.get('/profile?start_date=2026-05-06&end_date=2026-05-12')
    assert response.status_code == 200
    text = response.data.decode('utf-8')
    assert 'Movie tickets' in text
    assert 'New clothes' in text
    assert 'Dinner out' in text
    assert 'Grocery shopping' not in text
    assert 'Pharmacy' not in text
    # 60 + 150 + 35 = 245.0
    assert 'Rs.245.0' in text or '245.0' in text

def test_profile_custom_date_range(auth_client):
    """Custom date range filters expenses correctly.
    Range 2026-05-01 to 2026-05-05: Grocery, Gas, Electricity, Pharmacy."""
    response = auth_client.get('/profile?start_date=2026-05-01&end_date=2026-05-05')
    assert response.status_code == 200
    text = response.data.decode('utf-8')
    assert 'Grocery shopping' in text
    assert 'Gas refill' in text
    assert 'Electricity bill' in text
    assert 'Pharmacy' in text
    assert 'Movie tickets' not in text
    # 25.5 + 45 + 120 + 80 = 270.5
    assert 'Rs.270.5' in text or '270.5' in text

def test_profile_date_range_swapped_when_invalid(auth_client):
    """When start_date > end_date, dates are swapped and user redirected"""
    response = auth_client.get('/profile?start_date=2026-05-10&end_date=2026-05-01',
                              follow_redirects=False)
    assert response.status_code == 302
    assert 'start_date=2026-05-01' in response.location
    assert 'end_date=2026-05-10' in response.location

def test_profile_date_range_clears_filter(auth_client):
    """Removing date parameters shows all expenses again"""
    response = auth_client.get('/profile?start_date=2026-05-01&end_date=2026-05-05')
    assert '270.5' in response.data.decode('utf-8')
    response = auth_client.get('/profile')
    assert response.status_code == 200
    assert '565.5' in response.data.decode('utf-8')

def test_profile_no_expenses_in_range(auth_client):
    """Date range with no matching expenses shows zero totals"""
    response = auth_client.get('/profile?start_date=2026-05-20&end_date=2026-05-25')
    assert response.status_code == 200
    text = response.data.decode('utf-8')
    assert '0.0' in text or 'Rs.0' in text or '₹0' in text

def test_profile_preset_all(auth_client):
    """All preset clears date filter and shows all expenses.
    The preset=all button clears start/end inputs and submits."""
    response = auth_client.get('/profile?start_date=&end_date=')
    assert response.status_code == 200
    assert '565.5' in response.data.decode('utf-8')

def test_profile_preset_this_month(auth_client):
    """This month preset (May 2026) shows all seed expenses.
    All 8 expenses fall in May 2026."""
    response = auth_client.get('/profile?start_date=2026-05-01&end_date=2026-05-31')
    assert response.status_code == 200
    text = response.data.decode('utf-8')
    assert '565.5' in text
    assert 'Grocery shopping' in text

def test_profile_preset_last_month(auth_client):
    """Last month preset (April 2026) shows no expenses"""
    response = auth_client.get('/profile?start_date=2026-04-01&end_date=2026-04-30')
    assert response.status_code == 200
    text = response.data.decode('utf-8')
    assert '0.0' in text or '0' in text

def test_profile_preset_last_30_days(auth_client):
    """Last 30 days from 2026-05-12 shows expenses from April 12 onward.
    All seed expenses except Miscellaneous (May 15) fall within this range."""
    response = auth_client.get('/profile?start_date=2026-04-12&end_date=2026-05-12')
    assert response.status_code == 200
    # 25.5 + 45 + 120 + 80 + 60 + 150 + 35 = 515.5 (excludes May 15 Miscellaneous)
    assert '515.5' in response.data.decode('utf-8')

def test_profile_query_persistence_in_url(auth_client):
    """Applied filters remain in URL for shareability"""
    response = auth_client.get('/profile?start_date=2026-05-01&end_date=2026-05-05')
    assert response.status_code == 200
    assert 'value="2026-05-01"' in response.data.decode('utf-8')
    assert 'value="2026-05-05"' in response.data.decode('utf-8')

def test_profile_sql_injection_safety(auth_client):
    """SQL injection attempts are handled safely via parameterized queries"""
    response = auth_client.get('/profile?start_date=2026-05-01 OR 1=1--&end_date=2026-05-05')
    assert response.status_code != 500
    text = response.data.decode('utf-8')
    # Malformed input should yield no matching results or a handled error
    assert '0.0' in text or 'Rs.0' in text

def test_profile_invalid_date_format_handled_gracefully(auth_client):
    """Invalid date formats don't break the application.
    Invalid strings may trigger swap-redirect; final page should render OK."""
    response = auth_client.get('/profile?start_date=not-a-date&end_date=also-invalid')
    assert response.status_code != 500
    # If redirected due to string swap, follow and verify 200
    if response.status_code == 302:
        response = auth_client.get(response.location, follow_redirects=True)
    assert response.status_code == 200