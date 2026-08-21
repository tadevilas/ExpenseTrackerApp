# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

This is a **teaching/lab skeleton** for building an expense-tracker web app called **Spendly**. It is intentionally incomplete — most functionality is stubbed out and students implement it in numbered steps (visible in `app.py` as "coming in Step N" placeholders). When adding features, follow the step numbering already in place rather than reordering it.

The app is Indian-rupee themed (₹) and the templates use "Spendly" branding.

## Commands

All commands assume the venv is active (`.\venv\Scripts\Activate.ps1` in PowerShell, `source venv/Scripts/activate` in Git Bash). If unsure whether the venv is active, invoke Python explicitly as `.\venv\Scripts\python.exe`.

- **Run the dev server:** `python app.py` — Flask starts on **port 5001** with `debug=True` (auto-reloads on save). No `flask run` / `FLASK_APP` setup is used.
- **Install deps:** `pip install -r requirements.txt`
- **Tests:** `pytest` — no tests exist yet, but `pytest` and `pytest-flask` are already pinned. Run a single test with `pytest path/to/test_file.py::test_name`.

## Project structure

```
Lab 1/
├── app.py                  # Flask app + all routes (single-module, no blueprints)
├── requirements.txt        # flask 3.1.3, werkzeug 3.1.6, pytest 8.3.5, pytest-flask 1.3.0
├── expense_tracker.db      # SQLite file (gitignored, created by init_db())
├── database/
│   ├── __init__.py         # empty — package marker only
│   └── db.py               # Step 1: get_db() / init_db() / seed_db() (currently stub)
├── templates/              # Jinja2 templates — all extend base.html
│   ├── base.html           # navbar, footer, Spendly brand, font imports, {% block content %}
│   ├── landing.html        # marketing landing page (redesigned hero + "See how it works" modal)
│   ├── register.html       # POSTs to /register, renders {% if error %} block
│   ├── login.html          # POSTs to /login, renders {% if error %} block
│   ├── terms.html
│   └── privacy.html
├── static/
│   ├── css/
│   │   ├── style.css       # shared styles used by base.html
│   │   └── landing.css     # landing-page-specific styles
│   └── js/
│       └── main.js
└── venv/                   # local virtualenv (gitignored)
```

## Routes

Defined in `app.py`. All are GET unless noted — POST handlers for auth are added in a later step.

| Method | Path                        | View function      | Status                          |
|--------|-----------------------------|--------------------|---------------------------------|
| GET    | `/`                         | `landing`          | implemented (renders landing)   |
| GET    | `/register`                 | `register`         | implemented (form only, GET)    |
| GET    | `/login`                    | `login`            | implemented (form only, GET)    |
| GET    | `/terms`                    | `terms`            | implemented                     |
| GET    | `/privacy`                  | `privacy`          | implemented                     |
| GET    | `/logout`                   | `logout`           | placeholder — Step 3            |
| GET    | `/profile`                  | `profile`          | placeholder — Step 4            |
| GET    | `/expenses/add`             | `add_expense`      | placeholder — Step 7            |
| GET    | `/expenses/<int:id>/edit`   | `edit_expense`     | placeholder — Step 8            |
| GET    | `/expenses/<int:id>/delete` | `delete_expense`   | placeholder — Step 9            |

Note: `templates/login.html` and `templates/register.html` already `method="POST"` to `/login` and `/register`, so the auth step needs to add `methods=["GET", "POST"]` to those existing view functions rather than create new ones.

## Architecture

**Single-module Flask app**, not blueprints. All routes live in `app.py` against the top-level `app = Flask(__name__)`. Do not restructure into blueprints unless a step explicitly calls for it.

**Database layer (`database/db.py`) is deliberately empty** — the file's comment header specifies the exact API students must implement:
- `get_db()` — SQLite connection with `row_factory` set and foreign keys enabled
- `init_db()` — schema creation via `CREATE TABLE IF NOT EXISTS`
- `seed_db()` — dev sample data

The SQLite file is `expense_tracker.db` at the repo root (gitignored). `database/__init__.py` is empty; the package is only there to hold `db.py`.

**Templates use Jinja2 inheritance from `templates/base.html`**, which provides the navbar, footer, brand identity (Spendly, ◈ icon), font imports (DM Serif Display + DM Sans from Google Fonts), and the `{% block content %}` slot. New pages should extend `base.html` and only override `title`, `content`, `head`, and `scripts` blocks — the shell stays consistent.

**Auth forms already POST** — `templates/login.html` and `register.html` both submit to `/login` and `/register`. The current routes only handle GET (via `render_template`); adding POST handlers is part of the auth step. Both templates already render an `{% if error %}` block, so pass `error=` into `render_template` on failure rather than inventing a new pattern.

**Route placeholders in `app.py` return plain strings** like `"Logout — coming in Step 3"`. When a step implements one of these, replace the whole function body — do not leave the placeholder text behind.

## Step ordering (from placeholders in `app.py` and `database/db.py`)

- Step 1 — Database setup (`database/db.py`)
- Step 3 — Logout
- Step 4 — Profile
- Step 7 — Add expense
- Step 8 — Edit expense
- Step 9 — Delete expense

Steps 2, 5, 6 are not referenced in the current placeholders — they likely cover auth logic (register/login POST handlers), session management, and the expense list/dashboard view. Confirm with the user before assuming what these steps contain.
