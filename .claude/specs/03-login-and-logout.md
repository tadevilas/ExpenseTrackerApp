# Spec: Login and Logout

## Overview
Add the POST handler for `/login` so existing users can authenticate, and implement the `/logout` route so sessions can be terminated. The login form already exists and POSTs to `/login`; this step wires up the server-side logic to look up the user by email, verify the password with `werkzeug`, start a session, and redirect to the dashboard (or back with an error on failure). The logout route clears the session and redirects to the landing page. Together these steps complete the core authentication loop begun in Step 2.

## Depends on
- Step 1 — Database setup (`database/db.py` must be complete with `get_db()`)
- Step 2 — Registration (session keys `user_id` and `user_name` must be set by the register handler as this step reuses the same session shape)

## Routes
- `POST /login` — handle login form submission — public (adds `methods=["GET", "POST"]` to the existing `login` view function)
- `GET /logout` — clear session and redirect to landing page — logged-in (replace the placeholder string in the existing `logout` view function)

## Database changes
No database changes — the `users` table already has all required columns (`id`, `name`, `email`, `password_hash`).

## Templates
- **Modify:** `templates/login.html` — no structural changes needed; the `{% if error %}` block is already present
- **Modify:** `templates/base.html` — update the navbar so the Logout link points to `/logout` and is only shown when the user is logged in; show Login/Register links when not logged in (use `session.get('user_id')` in the template)

## Files to change
- `app.py` — add `check_password_hash` to the werkzeug import, add POST logic to the `login` view function, replace the `logout` placeholder with a working implementation

## Files to create
No new files.

## New dependencies
No new dependencies — `werkzeug.security` is already installed.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use string formatting in SQL
- Passwords verified with `werkzeug.security.check_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- On login, look up user by email with a parameterised query; if no row is found OR `check_password_hash` returns False, re-render `login.html` with `error="Invalid email or password."` (same message for both cases — do not reveal which field was wrong)
- Validate server-side: email and password fields must be non-empty; return a clear `error=` string if either is missing
- After successful login, store `user_id` and `user_name` in `session` (same keys used by registration), then `redirect(url_for('dashboard'))`
- `logout` must call `session.clear()` then `redirect(url_for('landing'))`
- Do not leave any placeholder strings — replace the entire `logout` function body

## Definition of done
- [ ] Submitting the login form with a valid email and correct password starts a session and redirects to `/dashboard`
- [ ] The dashboard shows the logged-in user's name after login
- [ ] Submitting with an incorrect password re-renders the form with `"Invalid email or password."` (no crash)
- [ ] Submitting with an email that does not exist re-renders the form with the same error (no crash)
- [ ] Submitting with an empty email or password field re-renders the form with an error
- [ ] Visiting `/logout` while logged in clears the session and redirects to the landing page
- [ ] Visiting `/dashboard` after logout redirects to `/login` (existing guard already handles this)
- [ ] The demo user (`demo@spendly.com` / `demo123`) can log in successfully
- [ ] The app starts without errors after changes
