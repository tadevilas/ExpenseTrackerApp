import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "expense_tracker.db")

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        (existing,) = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        if existing > 0:
            return

        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cursor.lastrowid

        today = date.today()
        def d(day):
            return today.replace(day=day).isoformat()

        expenses = [
            (user_id, 250.00, "Food",          d(2),  "Groceries"),
            (user_id, 60.00,  "Transport",     d(5),  "Metro card top-up"),
            (user_id, 1499.00,"Bills",         d(8),  "Electricity bill"),
            (user_id, 350.00, "Health",        d(11), "Pharmacy"),
            (user_id, 499.00, "Entertainment", d(14), "Movie tickets"),
            (user_id, 799.00, "Shopping",      d(18), "T-shirt"),
            (user_id, 120.00, "Other",         d(22), "Notebook"),
            (user_id, 180.00, "Food",          d(26), "Lunch out"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
        conn.commit()
    finally:
        conn.close()
