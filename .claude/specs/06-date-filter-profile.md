# Spec: Date Filter for Profile Page

## Overview
The profile page previously hardcoded all stats and charts to the current
calendar month. This step replaces that with a flexible period filter: five
preset pills (All Time, This Month, Last 3 Months, Last 6 Months, Custom) and
a custom start/end date range. The selected period is submitted as a GET query
parameter (`?filter=<mode>`) — keeping the URL shareable — and drives all
filtered queries. No database changes are required.

## Depends on
- Step 01 — Database setup (expenses table with `date` column)
- Step 04 — Profile page design (`profile.html` template exists)
- Step 05 — Backend route for profile page (`/profile` route with stats and charts)

## Routes
- `GET /profile?filter=<mode>` — profile page filtered to the chosen period —
  logged-in only. Valid `filter` values:

  | Value | Period covered |
  |---|---|
  | `all` | All recorded expenses |
  | `this_month` | First of the current month → today (default) |
  | `last_3` | First of the month 2 months ago → today |
  | `last_6` | First of the month 5 months ago → today |
  | `custom` | Requires `&start=YYYY-MM-DD&end=YYYY-MM-DD` |

  Missing or unrecognised `filter` values default to `this_month`.

## Database changes
No database changes.

## Templates
- **Modify:** `templates/profile.html`
  - Add a row of pill-shaped preset buttons inside a `<form method="GET"
    action="/profile">`. Each preset is a `<button type="submit">` with
    `name="filter"` and an appropriate value.
  - A "Custom" toggle button (type=button) shows/hides a hidden date-range row
    containing two `<input type="date">` fields (`name="start"`, `name="end"`)
    and an Apply button. The row is pre-populated and visible when
    `filter_mode == 'custom'`.
  - Active preset is styled with `.filter-btn.active` (dark background).
  - Replace the hardcoded "This Month" stat card label and "Daily Spending —
    This Month" chart heading with `{{ period_label }}`.

## Files changed
- `app.py` — replaced regex-based month parsing with a `filter_mode` branch
  that computes `start_date`/`end_date` for each preset; builds `date_sql` and
  `date_args` from Python literals only (never user input); passes
  `period_label`, `filter_mode`, `custom_start`, `custom_end` to the template.
- `templates/profile.html` — new filter form with preset pills + custom date
  row; `.filter-btn` / `.filter-btn.active` CSS; custom toggle JS; all
  `selected_month_label` references replaced with `period_label`.

## Files created
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`.
- Parameterised queries only — `date_sql` is a Python literal string, user input
  goes into bind parameters only. Never use f-strings with user-supplied values.
- Use `date.fromisoformat()` + `try/except` to validate custom dates; fall back
  to `this_month` on any error.
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`.
- Filtered queries: `total_this_month`, `top_category`, `categories_chart`,
  `daily_chart`, `recent_expenses`.
- Unfiltered (always all-time): `total_all_time`, `expense_count`.

## Definition of done
- [x] `/profile` (no param) shows current month data — no regression.
- [x] `?filter=all` shows all-time data; "All Time" pill is active.
- [x] `?filter=last_3` shows last 3 months; correct pill active.
- [x] `?filter=last_6` shows last 6 months; correct pill active.
- [x] `?filter=custom&start=2026-06-01&end=2026-08-28` shows that range;
      period label reads "01 Jun – 28 Aug 2026"; date inputs are pre-filled.
- [x] Invalid `?filter=xyz` falls back to this month without an error page.
- [x] All-time total and expense count are unchanged regardless of filter.
- [x] Custom date row is hidden by default and toggled by the Custom button.
