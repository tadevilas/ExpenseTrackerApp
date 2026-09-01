# Spendly — Expense Tracker

A step-by-step Flask lab project for building a personal expense tracker themed around Indian Rupees (₹).

## Overview

Spendly is a teaching skeleton where students implement features in numbered steps. The app provides user registration/login, a profile dashboard with spending charts and filters, and expense management.

## Features

- User registration and login with hashed passwords
- Session-based authentication
- Profile dashboard with:
  - Spending summary cards (period total, all-time total, top category)
  - Bar chart of spending by category
  - Daily spending trend chart
  - Recent expenses table
  - Date filter (this month, last 3 months, last 6 months, custom range)
- Add expense form with category selection and validation
- SQLite database with `users` and `expenses` tables

## Tech Stack

| Layer    | Technology                    |
|----------|-------------------------------|
| Backend  | Python 3 / Flask 3.1.3        |
| Auth     | Werkzeug password hashing     |
| Database | SQLite (via `sqlite3`)        |
| Frontend | Jinja2 templates, vanilla JS  |
| Fonts    | DM Serif Display + DM Sans    |
| Tests    | pytest 8.3.5 + pytest-flask   |

## Project Structure

```
Lab 1/
├── app.py                  # Flask app + all routes
├── requirements.txt
├── expense_tracker.db      # SQLite file (gitignored, auto-created)
├── database/
│   └── db.py               # get_db / init_db / seed_db / create_expense
├── templates/
│   ├── base.html           # shared shell (navbar, footer, brand)
│   ├── landing.html
│   ├── register.html
│   ├── login.html
│   ├── profile.html
│   ├── add_expense.html
│   ├── terms.html
│   └── privacy.html
└── static/
    ├── css/
    │   ├── style.css
    │   └── landing.css
    └── js/
        └── main.js
```

## Getting Started

### Prerequisites

- Python 3.10+

### Setup

```bash
# Clone the repo
git clone <repo-url>
cd "Lab 1"

# Create and activate virtualenv
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the dev server

```bash
python app.py
```

The app starts on **http://localhost:5001** with auto-reload enabled.

A demo account is seeded automatically on first run:

| Field    | Value             |
|----------|-------------------|
| Email    | demo@spendly.com  |
| Password | demo123           |

### Run tests

```bash
pytest
```

## Routes

| Method     | Path                        | Description                  |
|------------|-----------------------------|------------------------------|
| GET        | `/`                         | Landing page                 |
| GET / POST | `/register`                 | User registration            |
| GET / POST | `/login`                    | User login                   |
| GET        | `/logout`                   | Clear session, redirect home |
| GET        | `/profile`                  | Dashboard (auth required)    |
| GET / POST | `/expenses/add`             | Add a new expense            |
| GET        | `/expenses/<id>/edit`       | Edit expense (Step 8)        |
| GET        | `/expenses/<id>/delete`     | Delete expense (Step 9)      |
| GET        | `/terms`                    | Terms of service             |
| GET        | `/privacy`                  | Privacy policy               |

## Implementation Steps

Steps still to be implemented by students:

- **Step 8** — Edit expense
- **Step 9** — Delete expense

## License

MIT
