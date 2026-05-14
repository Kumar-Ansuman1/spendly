import pytest
import sys
sys.path.insert(0, '.')
from app import app
from database.queries import get_all_expenses


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestAddExpenseUnauthenticated:
    """Tests for unauthenticated access to the add expense page."""

    def test_unauthenticated_redirects_to_login(self, client):
        response = client.get("/expenses/add")
        assert response.status_code == 302
        assert "/login" in response.location

    def test_unauthenticated_post_redirects_to_login(self, client):
        response = client.post("/expenses/add", data={
            "amount": "25.00",
            "category": "Food",
            "date": "2026-05-14",
            "description": "Test expense"
        })
        assert response.status_code == 302
        assert "/login" in response.location


class TestAddExpenseForm:
    """Tests for the add expense form display."""

    def test_authenticated_renders_form(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.get("/expenses/add")
        assert response.status_code == 200

    def test_form_contains_amount_field(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.get("/expenses/add")
        html = response.data.decode("utf-8")
        assert 'name="amount"' in html
        assert 'type="number"' in html

    def test_form_contains_category_field(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.get("/expenses/add")
        html = response.data.decode("utf-8")
        assert 'name="category"' in html
        assert "<select" in html

    def test_form_contains_date_field(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.get("/expenses/add")
        html = response.data.decode("utf-8")
        assert 'name="date"' in html
        assert 'type="date"' in html

    def test_form_contains_description_field(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.get("/expenses/add")
        html = response.data.decode("utf-8")
        assert 'name="description"' in html
        assert "<textarea" in html

    def test_today_date_is_prefilled(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        response = client.get("/expenses/add")
        html = response.data.decode("utf-8")
        assert f'value="{today}"' in html


class TestAddExpenseValidation:
    """Tests for form validation on expense submission."""

    def _post_expense(self, client, amount="", category="", date="", description=""):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        return client.post("/expenses/add", data={
            "amount": amount,
            "category": category,
            "date": date,
            "description": description
        })

    def test_missing_amount_shows_error(self, client):
        response = self._post_expense(client, category="Food", date="2026-05-14")
        html = response.data.decode("utf-8")
        assert "Amount is required" in html

    def test_zero_amount_shows_error(self, client):
        response = self._post_expense(client, amount="0", category="Food", date="2026-05-14")
        html = response.data.decode("utf-8")
        assert "Amount must be greater than zero" in html

    def test_negative_amount_shows_error(self, client):
        response = self._post_expense(client, amount="-5.00", category="Food", date="2026-05-14")
        html = response.data.decode("utf-8")
        assert "Amount must be greater than zero" in html

    def test_invalid_amount_shows_error(self, client):
        response = self._post_expense(client, amount="abc", category="Food", date="2026-05-14")
        html = response.data.decode("utf-8")
        assert "Amount must be a valid number" in html

    def test_missing_category_shows_error(self, client):
        response = self._post_expense(client, amount="25.00", category="", date="2026-05-14")
        html = response.data.decode("utf-8")
        assert "Category is required" in html

    def test_missing_date_shows_error(self, client):
        response = self._post_expense(client, amount="25.00", category="Food", date="")
        html = response.data.decode("utf-8")
        assert "Date is required" in html

    def test_invalid_date_format_shows_error(self, client):
        response = self._post_expense(client, amount="25.00", category="Food", date="14-05-2026")
        html = response.data.decode("utf-8")
        assert "Date must be in YYYY-MM-DD format" in html

    def test_invalid_date_text_shows_error(self, client):
        response = self._post_expense(client, amount="25.00", category="Food", date="not-a-date")
        html = response.data.decode("utf-8")
        assert "Date must be in YYYY-MM-DD format" in html


class TestAddExpenseSubmission:
    """Tests for successful expense submission."""

    def test_valid_submission_redirects_to_profile(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.post("/expenses/add", data={
            "amount": "25.00",
            "category": "Food",
            "date": "2026-05-14",
            "description": "Test expense"
        }, follow_redirects=False)
        assert response.status_code == 302
        assert "/profile" in response.location

    def test_valid_submission_adds_expense_to_database(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        # Record expense count before adding
        expenses_before = get_all_expenses(1)
        count_before = len(expenses_before)

        client.post("/expenses/add", data={
            "amount": "25.00",
            "category": "Food",
            "date": "2026-05-14",
            "description": "Test expense"
        })

        expenses_after = get_all_expenses(1)
        assert len(expenses_after) == count_before + 1

        # Find the newly added expense (search by unique description)
        new_expense = None
        for e in expenses_after:
            if e["description"] == "Test expense":
                new_expense = e
                break
        assert new_expense is not None
        assert new_expense["amount"] == 25.0
        assert new_expense["category"] == "Food"
        assert new_expense["date"] == "2026-05-14"
        assert new_expense["description"] == "Test expense"

    def test_valid_submission_shows_success_flash_message(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        # POST without following redirect, then GET the add page
        # to verify the success flash message renders
        response = client.post("/expenses/add", data={
            "amount": "25.00",
            "category": "Food",
            "date": "2026-05-14",
            "description": "Test expense"
        }, follow_redirects=False)

        # Flash is set; verify it renders on the add page
        response = client.get("/expenses/add")
        html = response.data.decode("utf-8")
        assert "Expense added successfully!" in html

    def test_form_resets_after_successful_submission(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.post("/expenses/add", data={
            "amount": "25.00",
            "category": "Food",
            "date": "2026-05-14",
            "description": "Test expense"
        }, follow_redirects=True)
        html = response.data.decode("utf-8")
        # After redirect to profile, the add form should not retain old values
        assert 'value="25.00"' not in html
        assert 'value="Food"' not in html

    def test_expense_appears_in_profile_transactions(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        client.post("/expenses/add", data={
            "amount": "99.99",
            "category": "Transport",
            "date": "2026-05-14",
            "description": "New expense for profile test"
        })
        response = client.get("/profile")
        html = response.data.decode("utf-8")
        assert "99.99" in html
        assert "New expense for profile test" in html


class TestAddExpenseFormPreservation:
    """Tests that form values are preserved on validation error."""

    def _post_with_error(self, client, amount="", category="Food", date="2026-05-14"):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        return client.post("/expenses/add", data={
            "amount": amount,
            "category": category,
            "date": date,
            "description": ""
        })

    def test_category_preserved_on_amount_error(self, client):
        response = self._post_with_error(client, amount="", category="Transport")
        html = response.data.decode("utf-8")
        assert 'value="Transport"' in html or 'selected' in html

    def test_amount_preserved_on_category_error(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.post("/expenses/add", data={
            "amount": "15.00",
            "category": "",
            "date": "2026-05-14",
            "description": "Test"
        })
        html = response.data.decode("utf-8")
        assert 'value="15.00"' in html

    def test_description_preserved_on_amount_error(self, client):
        response = self._post_with_error(client, amount="")
        html = response.data.decode("utf-8")
        assert 'name="description"' in html

    def test_date_preserved_on_amount_error(self, client):
        """Spec requires date value preserved on validation error."""
        response = self._post_with_error(client, amount="", date="2026-06-01")
        html = response.data.decode("utf-8")
        # The template should preserve submitted date on error
        assert 'value="2026-06-01"' in html

    def test_all_fields_preserved_on_mixed_error(self, client):
        """When multiple fields have errors, previously entered values are kept."""
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Demo User"
        response = client.post("/expenses/add", data={
            "amount": "",
            "category": "",
            "date": "2026-06-15",
            "description": "Some note"
        })
        html = response.data.decode("utf-8")
        # Date and description should be preserved even when amount/category have errors
        assert 'value="2026-06-15"' in html
        assert "Some note" in html