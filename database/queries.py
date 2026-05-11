from database.db import get_db
from datetime import datetime


def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    conn.close()
    if not user_row:
        return None
    member_since = datetime.strptime(user_row["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%B %Y")
    return {
        "name": user_row["name"],
        "email": user_row["email"],
        "member_since": member_since
    }


def get_all_expenses(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    )
    expenses = cursor.fetchall()
    conn.close()
    return expenses


def get_summary_stats(user_id, start_date=None, end_date=None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [user_id]
    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    query += " ORDER BY date DESC"
    cursor.execute(query, params)
    expenses = cursor.fetchall()
    conn.close()
    if not expenses:
        return {"total_spent": 0, "transaction_count": 0, "top_category": "—"}

    total_spent = sum(e["amount"] for e in expenses)
    transaction_count = len(expenses)

    category_totals = {}
    for e in expenses:
        cat = e["category"]
        category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

    top_category = max(category_totals, key=category_totals.get) if category_totals else "—"

    return {
        "total_spent": round(total_spent, 2),
        "transaction_count": transaction_count,
        "top_category": top_category
    }


def get_recent_transactions(user_id, limit=10, start_date=None, end_date=None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [user_id]
    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    query += " ORDER BY date DESC LIMIT ?"
    params.append(limit)
    cursor.execute(query, params)
    expenses = cursor.fetchall()
    conn.close()
    transactions = []
    for e in expenses:
        date_obj = datetime.strptime(e["date"], "%Y-%m-%d")
        formatted_date = date_obj.strftime("%b %d").replace(" 0", " ")
        transactions.append({
            "date": formatted_date,
            "description": e["description"],
            "category": e["category"],
            "amount": e["amount"]
        })
    return transactions


def get_category_breakdown(user_id, start_date=None, end_date=None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [user_id]
    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    query += " ORDER BY date DESC"
    cursor.execute(query, params)
    expenses = cursor.fetchall()
    conn.close()
    if not expenses:
        return []

    total_spent = sum(e["amount"] for e in expenses)
    category_totals = {}
    for e in expenses:
        cat = e["category"]
        category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

    categories = []
    for cat, amt in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        categories.append({
            "name": cat,
            "amount": round(amt, 2),
            "percentage": 0
        })

    raw_total = sum(c["amount"] for c in categories)
    assigned = 0
    for i, c in enumerate(categories):
        pct = round((c["amount"] / raw_total) * 100)
        categories[i]["percentage"] = pct
        assigned += pct

    remainder = 100 - assigned
    if categories and remainder != 0:
        categories[0]["percentage"] += remainder

    return categories