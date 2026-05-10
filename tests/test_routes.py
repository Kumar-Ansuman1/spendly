import pytest
import sys
sys.path.insert(0, '.')
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestProfileRoute:
    def test_unauthenticated_redirects(self, client):
        response = client.get("/profile")
        assert response.status_code == 302
        assert "/login" in response.location

    def test_authenticated_seed_user(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.get("/profile")
        assert response.status_code == 200
        assert b"Demo User" in response.data
        assert b"demo@spendly.com" in response.data
        assert "₹" in response.data.decode("utf-8")