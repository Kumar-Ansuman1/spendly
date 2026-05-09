from flask import Flask, render_template, request, redirect, url_for, session
from database.db import init_db, seed_db, get_db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = "dev-key-change-in-production"


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def redirect_if_logged_in(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("profile"))
        return f(*args, **kwargs)
    return decorated

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
@redirect_if_logged_in
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required")

        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters")

        conn = get_db()
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Email already registered")
        finally:
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@redirect_if_logged_in
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template("login.html", error="Email and password are required")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("profile"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
@login_required
def profile():
    user = {
        "name": session.get("user_name", "User"),
        "email": "demo@spendly.com",
        "member_since": "April 2026"
    }

    stats = {
        "total_spent": 565.50,
        "transaction_count": 8,
        "top_category": "Shopping"
    }

    transactions = [
        {"date": "May 15", "description": "New clothes", "category": "Shopping", "amount": 150.00},
        {"date": "May 12", "description": "Dinner out", "category": "Food", "amount": 35.00},
        {"date": "May 10", "description": "Miscellaneous", "category": "Other", "amount": 50.00},
        {"date": "May 8", "description": "Movie tickets", "category": "Entertainment", "amount": 60.00},
        {"date": "May 5", "description": "Pharmacy", "category": "Health", "amount": 80.00},
    ]

    categories = [
        {"name": "Food", "amount": 60.50, "percentage": 11},
        {"name": "Transport", "amount": 45.00, "percentage": 8},
        {"name": "Bills", "amount": 120.00, "percentage": 21},
        {"name": "Health", "amount": 80.00, "percentage": 14},
        {"name": "Entertainment", "amount": 60.00, "percentage": 11},
        {"name": "Shopping", "amount": 150.00, "percentage": 27},
        {"name": "Other", "amount": 50.00, "percentage": 9},
    ]

    return render_template("profile.html", user=user, stats=stats, transactions=transactions, categories=categories)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
