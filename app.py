import sqlite3
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-me"


@app.template_filter('rupee')
def rupee_format(value):
    return f"₹{value:,.0f}"


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
def register():
    if request.method == "GET":
        return render_template("register.html")

    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name or not email:
        return render_template("register.html", error="Name and email are required.")
    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")

    password_hash = generate_password_hash(password)

    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return render_template("register.html", error="An account with that email already exists.")
    finally:
        conn.close()

    session["user_id"]   = user_id
    session["user_name"] = name
    return redirect(url_for("profile"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", error="Email and password are required.")

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"]   = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("profile"))


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
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        if user is None:
            session.clear()
            return redirect(url_for("login"))

        total_this_month = conn.execute(
            """SELECT COALESCE(SUM(amount), 0) FROM expenses
               WHERE user_id = ?
               AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')""",
            (session["user_id"],)
        ).fetchone()[0]

        total_all_time = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?",
            (session["user_id"],)
        ).fetchone()[0]

        expense_count = conn.execute(
            "SELECT COUNT(*) FROM expenses WHERE user_id = ?",
            (session["user_id"],)
        ).fetchone()[0]

        top_row = conn.execute(
            """SELECT category FROM expenses WHERE user_id = ?
               GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1""",
            (session["user_id"],)
        ).fetchone()
        top_category = top_row["category"] if top_row else None

        category_rows = conn.execute(
            """SELECT category, SUM(amount) AS total FROM expenses
               WHERE user_id = ?
               GROUP BY category ORDER BY total DESC""",
            (session["user_id"],)
        ).fetchall()
        categories_chart = [{"category": r["category"], "total": r["total"]} for r in category_rows]

        daily_rows = conn.execute(
            """SELECT date, SUM(amount) AS total FROM expenses
               WHERE user_id = ?
               AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
               GROUP BY date ORDER BY date""",
            (session["user_id"],)
        ).fetchall()
        daily_chart = [{"date": r["date"], "total": r["total"]} for r in daily_rows]
        max_daily = max((r["total"] for r in daily_rows), default=0)

    finally:
        conn.close()

    member_since = datetime.strptime(
        user["created_at"][:10], "%Y-%m-%d"
    ).strftime("%B %Y")

    return render_template(
        "profile.html",
        user=user,
        member_since=member_since,
        total_this_month=total_this_month,
        total_all_time=total_all_time,
        expense_count=expense_count,
        top_category=top_category,
        categories_chart=categories_chart,
        daily_chart=daily_chart,
        max_daily=max_daily,
    )


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
