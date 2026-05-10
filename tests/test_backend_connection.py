import pytest
import sys
sys.path.insert(0, '.')
from database.queries import get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown


class TestGetUserById:
    def test_valid_user(self):
        result = get_user_by_id(1)
        assert result is not None
        assert result["name"] == "Demo User"
        assert result["email"] == "demo@spendly.com"
        assert "member_since" in result

    def test_nonexistent_user(self):
        result = get_user_by_id(99999)
        assert result is None


class TestGetSummaryStats:
    def test_user_with_expenses(self):
        result = get_summary_stats(1)
        assert result["total_spent"] == 565.5
        assert result["transaction_count"] == 8
        assert result["top_category"] == "Shopping"

    def test_user_no_expenses(self):
        result = get_summary_stats(99999)
        assert result["total_spent"] == 0
        assert result["transaction_count"] == 0
        assert result["top_category"] == "—"


class TestGetRecentTransactions:
    def test_user_with_expenses(self):
        result = get_recent_transactions(1, limit=10)
        assert len(result) == 8
        assert result[0].keys() == {"date", "description", "category", "amount"}
        assert result[0]["date"] == "May 15"

    def test_user_no_expenses(self):
        result = get_recent_transactions(99999)
        assert result == []


class TestGetCategoryBreakdown:
    def test_user_with_expenses(self):
        result = get_category_breakdown(1)
        assert len(result) == 7
        assert sum(c["percentage"] for c in result) == 100
        assert result[0].keys() == {"name", "amount", "percentage"}

    def test_user_no_expenses(self):
        result = get_category_breakdown(99999)
        assert result == []