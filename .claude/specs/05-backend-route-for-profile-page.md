# Spec: Backend Route for Profile Page

## Overview
Extend the `/profile` route to fetch and render the user's most recent expense records as a formatted list below the spending charts. The current implementation (step 04) shows aggregate statistics and visualisations, but gives users no way to see their individual transactions. This step adds that data to the route and a "Recent Expenses" table to the template, completing the profile page as a personal home base before expense CRUD is introduced in Steps 7–9.

## Depends on
- Step 1 — Database setup (`get_db()` complete; `users` and `expenses` tables must exist)
- Step 2 — Registration (user record exists in `users`)
- Step 3 — Login and Logout (session contains `user_id`; auth guard in `/profile` is in place)
- Step 4 — Profile page design (`profile.html` exists; stat cards and charts already rendered)

## Routes
No new routes — extends the existing `GET /profile` route only.

## Database changes
No database changes — `expenses` table already has all required columns (`id`, `user_id`, `amount`, `category`, `date`, `description`).

## Templates
- **Modify:** `templates/profile.html` — add a "Recent Expenses" section below the daily chart; render a table/list of the fetched expense rows, with an empty-state message when there are none

## Files to change
- `app.py` — add a `recent_expenses` query inside the existing `profile` view function, and pass the result to `render_template`
- `templates/profile.html` — add the Recent Expenses section using the new template variable

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use string formatting in SQL
- Passwords hashed with werkzeug (no password changes in this step)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Fetch the 10 most recent expenses for the logged-in user:
  `SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 10`
- Pass the result as `recent_expenses` to `render_template`; it may be an empty list — handle that in the template with an `{% if recent_expenses %}` guard
- Render each row with: date, category, description (or an em-dash if `None`), and amount formatted with `| rupee`
- Follow the existing DB lifecycle pattern: run the query inside the same `try` block as the other queries in the `profile` function, before `conn.close()` in `finally`
- Do not change any of the existing queries or variables in the `profile` route — only add the new query and pass its result
- Style the section consistently with the existing profile cards (use the `.profile-card` class shell); no new CSS custom properties needed

## Definition of done
- [ ] Visiting `/profile` while logged in shows a "Recent Expenses" section below the charts
- [ ] The section lists up to 10 expenses, each showing date, category, description, and ₹ amount
- [ ] If the user has no expenses, the section shows an appropriate empty-state message instead of a broken table
- [ ] The demo user (`demo@spendly.com` / `demo123`) sees all 8 seeded expenses listed
- [ ] Expenses are ordered most-recent first (by date, then by id)
- [ ] All existing profile stats and charts continue to render correctly (no regressions)
- [ ] The page starts without errors and no placeholder text remains in the route
