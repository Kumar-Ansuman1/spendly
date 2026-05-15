from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db import init_db, seed_db, get_db
from database.queries import get_expense_by_id
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
from datetime import datetime

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


@app.route("/analytics")
@login_required
def analytics():
    return render_template("analytics.html")


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
    from database.queries import get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown
    from datetime import datetime

    user_id = session["user_id"]
    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for("login"))

    def validate_date(val):
        """Validate YYYY-MM-DD format, return the value or None."""
        if not val:
            return None
        try:
            datetime.strptime(val, "%Y-%m-%d")
            return val
        except (ValueError, TypeError):
            return None

    start_date = validate_date(request.args.get("start_date"))
    end_date = validate_date(request.args.get("end_date"))

    # Validate date range: if both dates are provided and start_date > end_date, swap them
    if start_date and end_date and start_date > end_date:
        start_date, end_date = end_date, start_date
        # Redirect to the same page with the swapped dates in the query string
        return redirect(url_for("profile", start_date=start_date, end_date=end_date))

    stats = get_summary_stats(user_id, start_date, end_date)
    transactions = get_recent_transactions(user_id, limit=10, start_date=start_date, end_date=end_date)
    categories = get_category_breakdown(user_id, start_date=start_date, end_date=end_date)

    return render_template("profile.html", user=user, stats=stats, transactions=transactions, categories=categories, start_date=start_date, end_date=end_date)


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


@app.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        # Get form data
        amount_str = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()

        # Validation
        error = None

        # Validate amount
        if not amount_str:
            error = "Amount is required"
        else:
            try:
                amount = float(amount_str)
                if amount <= 0:
                    error = "Amount must be greater than zero"
            except ValueError:
                error = "Amount must be a valid number"

        # Validate category
        if not error and not category:
            error = "Category is required"

        # Validate date
        if not error:
            if not date:
                error = "Date is required"
            else:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    error = "Date must be in YYYY-MM-DD format"

        # If validation failed, show error and re-render form
        if error:
            flash(error, "error")
            return render_template("expenses/add.html",
                                 today=today_str(),
                                 amount=amount_str,
                                 category=category,
                                 date=date,
                                 description=description)

        # If validation passed, insert expense into database
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (session["user_id"], amount, category, date, description)
            )
            conn.commit()
            flash("Expense added successfully!", "success")
        except Exception as e:
            flash("Something went wrong. Please try again.", "error")
            app.logger.error(f"Expense add failed: {e}")
        finally:
            conn.close()

        return redirect(url_for("profile"))

    # GET request — show the form
    return render_template("expenses/add.html", today=today_str())


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    user_id = session["user_id"]
    expense = get_expense_by_id(user_id, id)
    if not expense:
        flash("Expense not found", "error")
        return redirect(url_for("profile"))

    if request.method == "POST":
        amount_str = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()

        error = None

        if not amount_str:
            error = "Amount is required"
        else:
            try:
                amount = float(amount_str)
                if amount <= 0:
                    error = "Amount must be greater than zero"
            except ValueError:
                error = "Amount must be a valid number"

        if not error and not category:
            error = "Category is required"

        if not error:
            if not date:
                error = "Date is required"
            else:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    error = "Date must be in YYYY-MM-DD format"

        if error:
            flash(error, "error")
            return render_template("expenses/edit.html",
                                   expense=expense,
                                   amount=amount_str,
                                   category=category,
                                   date=date,
                                   description=description)

        conn = get_db()
        try:
            conn.execute(
                "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ? AND user_id = ?",
                (amount, category, date, description, id, user_id)
            )
            conn.commit()
            flash("Expense updated successfully!", "success")
        except Exception as e:
            flash("Something went wrong. Please try again.", "error")
            app.logger.error(f"Expense edit failed: {e}")
        finally:
            conn.close()

        return redirect(url_for("profile"))

    return render_template("expenses/edit.html", expense=expense)


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
