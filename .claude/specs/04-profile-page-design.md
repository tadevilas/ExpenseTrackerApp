# Spec: Profile Page Design

## Overview
Implement the `/profile` route so logged-in users can view their account information and a personalised spending summary. The page fetches the user record from the database and computes aggregate expense statistics (total spent this month, all-time total, number of expenses, top spending category), then renders a dedicated profile template. This replaces the Step 4 placeholder string and gives users a personal home base within the app before expense CRUD is introduced in Steps 7–9.

## Depends on
- Step 1 — Database setup (`get_db()` must be complete; `users` and `expenses` tables must exist)
- Step 2 — Registration (user record must exist in `users` table)
- Step 3 — Login and Logout (session must contain `user_id` and `user_name`; auth guard pattern established)

## Routes
- `GET /profile` — display the logged-in user's profile and expense summary — logged-in only (redirect to `/login` if no session)

## Database changes
No database changes — `users` and `expenses` tables already have all required columns.

## Templates
- **Create:** `templates/profile.html` — full profile page extending `base.html`; displays a user info card (name, email, member-since date) and a spending summary grid (this month, all time, count, top category)
- **Modify:** `templates/base.html` — add a "Profile" link to the logged-in nav block (between "Dashboard" and "Sign out")

## Files to change
- `app.py` — replace the `profile` placeholder with a working route; add a `rupee` Jinja2 template filter for ₹ formatting
- `templates/base.html` — add Profile nav link for authenticated users

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use string formatting in SQL
- Passwords hashed with werkzeug (no password changes in this step)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Guard the route: if `session.get("user_id")` is falsy, `redirect(url_for("login"))`
- Fetch the full user row: `SELECT * FROM users WHERE id = ?` using `session["user_id"]`; if row is missing, clear session and redirect to login
- Compute stats with parameterised queries:
  - `total_this_month` — `COALESCE(SUM(amount), 0)` where `strftime('%Y-%m', date) = strftime('%Y-%m', 'now')`
  - `total_all_time` — `COALESCE(SUM(amount), 0)` for the user
  - `expense_count` — `COUNT(*)` for the user
  - `top_category` — `category` with highest `SUM(amount)` via `GROUP BY … ORDER BY … LIMIT 1`; `None` if no expenses
- Add a `rupee` Jinja2 template filter: `f"₹{value:,.0f}"` — use `{{ value | rupee }}` in the template
- Format `member_since` from `users.created_at` (stored as `datetime('now')` → `"YYYY-MM-DD HH:MM:SS"`) using `datetime.strptime(created_at[:10], "%Y-%m-%d").strftime("%B %Y")`
- Follow the existing DB lifecycle pattern: `conn = get_db()` / `try` block / `conn.close()` in `finally`
- Do not leave any placeholder strings — replace the entire `profile` function body

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`
- [ ] Visiting `/profile` while logged in renders the profile page with no errors
- [ ] The page shows the logged-in user's name and email
- [ ] The page shows a member-since date derived from `users.created_at`
- [ ] The page shows total spent this month (₹ formatted), all-time total, expense count, and top category
- [ ] All four stats display correctly for the demo user (`demo@spendly.com` / `demo123`)
- [ ] The navbar includes a "Profile" link visible only to logged-in users
- [ ] The page is styled consistently with the rest of the app (extends `base.html`, CSS variables only, no hardcoded colours)
- [ ] The app starts without errors after all changes
