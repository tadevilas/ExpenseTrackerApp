import sqlite3
from datetime import date, datetime

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


def _months_ago_start(today, n):
    month = today.month - n
    year = today.year
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, 1)


def _default_this_month(today):
    return today.replace(day=1), today, today.strftime("%B %Y")


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    filter_mode = request.args.get("filter", "this_month")
    today = date.today()
    custom_start = custom_end = ""

    if filter_mode == "all":
        start_date = end_date = None
        period_label = "All Time"
    elif filter_mode == "last_3":
        start_date = _months_ago_start(today, 2)
        end_date = today
        period_label = "Last 3 Months"
    elif filter_mode == "last_6":
        start_date = _months_ago_start(today, 5)
        end_date = today
        period_label = "Last 6 Months"
    elif filter_mode == "custom":
        try:
            start_date = date.fromisoformat(request.args.get("start", ""))
            end_date   = date.fromisoformat(request.args.get("end", ""))
            if start_date > end_date:
                start_date, end_date = end_date, start_date
            period_label = f"{start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')}"
            custom_start = start_date.isoformat()
            custom_end   = end_date.isoformat()
        except (ValueError, TypeError):
            filter_mode = "this_month"
            start_date, end_date, period_label = _default_this_month(today)
    else:
        filter_mode = "this_month"
        start_date, end_date, period_label = _default_this_month(today)

    # date_sql is built from Python literals only — no user input interpolated
    if start_date is not None:
        date_sql  = "AND date >= ? AND date <= ?"
        date_args = (start_date.isoformat(), end_date.isoformat())
    else:
        date_sql  = ""
        date_args = ()

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        if user is None:
            session.clear()
            return redirect(url_for("login"))

        total_for_period = conn.execute(
            f"SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? {date_sql}",
            (session["user_id"],) + date_args
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
            f"""SELECT category FROM expenses WHERE user_id = ? {date_sql}
               GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1""",
            (session["user_id"],) + date_args
        ).fetchone()
        top_category = top_row["category"] if top_row else None

        category_rows = conn.execute(
            f"""SELECT category, SUM(amount) AS total FROM expenses
               WHERE user_id = ? {date_sql}
               GROUP BY category ORDER BY total DESC""",
            (session["user_id"],) + date_args
        ).fetchall()
        categories_chart = [{"category": r["category"], "total": r["total"]} for r in category_rows]

        daily_rows = conn.execute(
            f"""SELECT date, SUM(amount) AS total FROM expenses
               WHERE user_id = ? {date_sql}
               GROUP BY date ORDER BY date""",
            (session["user_id"],) + date_args
        ).fetchall()
        daily_chart = [{"date": r["date"], "total": r["total"]} for r in daily_rows]
        max_daily = max((r["total"] for r in daily_rows), default=0)

        recent_expenses = conn.execute(
            f"""SELECT * FROM expenses WHERE user_id = ? {date_sql}
               ORDER BY date DESC, id DESC LIMIT 10""",
            (session["user_id"],) + date_args
        ).fetchall()

    finally:
        conn.close()

    member_since = datetime.strptime(
        user["created_at"][:10], "%Y-%m-%d"
    ).strftime("%B %Y")

    return render_template(
        "profile.html",
        user=user,
        member_since=member_since,
        total_for_period=total_for_period,
        total_all_time=total_all_time,
        expense_count=expense_count,
        top_category=top_category,
        categories_chart=categories_chart,
        daily_chart=daily_chart,
        max_daily=max_daily,
        recent_expenses=recent_expenses,
        period_label=period_label,
        filter_mode=filter_mode,
        custom_start=custom_start,
        custom_end=custom_end,
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
