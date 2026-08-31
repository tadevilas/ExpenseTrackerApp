# Spec: Add Expense

## Overview
This step implements the "Add Expense" feature, allowing a logged-in user to record a new expense via a form. The form collects amount, category, date, and an optional description, then inserts the record into the `expenses` table. On success the user is redirected to the profile page where the new expense will appear in the recent list. This is the first write path for expense data and is a prerequisite for the edit and delete steps.

## Depends on
- Step 01 — Database setup (`database/db.py`, `expenses` table must exist)
- Step 02 — Registration (users table and session)
- Step 03 — Login / Logout (session-protected routes pattern)
- Step 04/05 — Profile page (redirect target after successful add)

## Routes
- `GET /expenses/add` — Render the blank add-expense form — logged-in only
- `POST /expenses/add` — Validate and insert the new expense, redirect to `/profile` on success — logged-in only

## Database changes
No new tables or columns. The existing `expenses` table in `database/db.py` already has all required columns:
- `user_id` (FK → users)
- `amount` (REAL)
- `category` (TEXT)
- `date` (TEXT, ISO-8601)
- `description` (TEXT, nullable)

## Templates
- **Create:** `templates/add_expense.html` — form with fields: amount, category (dropdown), date, description (optional textarea). Renders `{% if error %}` block on validation failure.
- **Modify:** `templates/base.html` — add an "Add Expense" nav link visible only when the user is logged in (`session.user_id`).

## Files to change
- `app.py` — replace the `add_expense` stub with GET+POST handler; add `methods=["GET", "POST"]`
- `templates/base.html` — add nav link for Add Expense

## Files to create
- `templates/add_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only
- Parameterised queries only — never f-string user input into SQL
- Passwords hashed with werkzeug (not relevant here, but keep the pattern in mind)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Redirect unauthenticated users to `/login` (check `session.get("user_id")` at the top of both GET and POST handlers)
- `amount` must be a positive number — validate server-side and return the form with an `error=` message on failure
- `category` must be one of the values in `CATEGORIES` (imported from `database/db.py`) — validate server-side
- `date` defaults to today (`date.today().isoformat()`) in the form but is editable
- After a successful INSERT, redirect to `url_for("profile")`
- The category dropdown should be populated from the `CATEGORIES` list passed from the route, not hardcoded in the template

## Definition of done
- [ ] Visiting `/expenses/add` while logged out redirects to `/login`
- [ ] Visiting `/expenses/add` while logged in renders a form with amount, category dropdown, date, and description fields
- [ ] Submitting the form with a valid amount, category, and date inserts a row into `expenses` and redirects to `/profile`
- [ ] The newly added expense appears in the "Recent Expenses" list on the profile page
- [ ] Submitting with a missing or non-positive amount re-renders the form with a visible error message
- [ ] Submitting with an invalid category re-renders the form with a visible error message
- [ ] The "Add Expense" link is visible in the navbar when the user is logged in and absent when logged out
