# Spec: Registration

## Overview
Add the POST handler for `/register` so new users can create a Spendly account. The form already exists and POSTs to `/register`; this step wires up the server-side logic to validate input, hash the password, insert the user into the `users` table, start a session, and redirect to the dashboard (or back with an error on failure). This is the first step that introduces Flask sessions to the app.

## Depends on
- Step 1 — Database setup (`database/db.py` must be complete with `get_db()`, `init_db()`, and `seed_db()`)

## Routes
- `POST /register` — handle registration form submission — public (adds `methods=["GET", "POST"]` to the existing `register` view function)

## Database changes
No database changes — the `users` table already exists with the correct schema (`id`, `name`, `email`, `password_hash`, `created_at`).

## Templates
- **Modify:** `templates/register.html` — no structural changes needed; the `{% if error %}` block is already present
- **Create:** `templates/dashboard.html` — placeholder dashboard page the user lands on after successful registration (stub is acceptable; will be fully built in a later step)

## Files to change
- `app.py` — add `session` to the Flask import, add `SECRET_KEY` config, add POST logic to the `register` view function

## Files to create
- `templates/dashboard.html` — minimal page extending `base.html`, showing "Welcome, {{ name }}!" and a placeholder message for the expense list

## New dependencies
No new dependencies — `werkzeug.security` is already installed.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use string formatting in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- `SECRET_KEY` must be set on `app.config` before sessions work; use a hard-coded dev string for now (e.g. `"dev-secret-change-me"`)
- On duplicate email (UNIQUE constraint violation), catch the `sqlite3.IntegrityError` and re-render the form with `error="An account with that email already exists."`
- Validate server-side: name and email must be non-empty, password must be at least 8 characters; return a clear `error=` string for each failure
- After successful insert, store `user_id` and `user_name` in `session`, then `redirect(url_for('dashboard'))`
- Do not leave the GET placeholder string — replace the entire function body

## Definition of done
- [ ] Submitting the form with valid data creates a new user row in `users` with a hashed password
- [ ] Successful registration redirects to `/dashboard` and the page shows the user's name
- [ ] Submitting with a duplicate email re-renders the form with an error message (no crash)
- [ ] Submitting with a short password (< 8 chars) re-renders the form with a validation error
- [ ] Submitting with an empty name or email re-renders the form with an error
- [ ] The plain-text password is never stored in the database
- [ ] The app starts without errors after changes
