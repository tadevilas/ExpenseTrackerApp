"""
tests/test_06_date_filter_profile.py

Pytest tests for the /profile date-filter feature.

Covers:
  - Auth guard: unauthenticated requests redirect to /login
  - Preset filter buttons: all, this_month, last_3, last_6
  - Custom date range: valid, swapped dates, invalid dates
  - Invalid/unknown filter fallback to this_month
  - Always-rendered stat cards: All Time total and Expenses count
  - custom-row div visibility when filter=custom is active

Implementation note
-------------------
database.db.get_db() uses a hardcoded DB_PATH derived from __file__ and does
not read Flask app config. Tests therefore run against the real expense_tracker.db.
The Demo User (id=1) is seeded by seed_db() when app.py is first imported, so
session injection with user_id=1 is reliable as long as that seed has run.
"""

import pytest
from app import app as flask_app


# ------------------------------------------------------------------ #
# Fixtures                                                            #
# ------------------------------------------------------------------ #

@pytest.fixture
def app():
    """Configure the Flask app for testing. SECRET_KEY must be stable so that
    session_transaction() and subsequent request sessions match."""
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-for-pytest",
    })
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Return a test client whose session already contains the Demo User (id=1).

    The Demo User is inserted by seed_db() at import time (see database/db.py).
    We inject the session directly rather than posting to /login so that each
    test is independent of the auth routes.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"
    return client


# ------------------------------------------------------------------ #
# 1. Auth guard                                                       #
# ------------------------------------------------------------------ #

class TestProfileAuthGuard:

    def test_profile_requires_login(self, client):
        """Unauthenticated GET /profile must redirect to /login (302)."""
        response = client.get("/profile")
        assert response.status_code == 302, (
            "Expected a 302 redirect for an unauthenticated request to /profile"
        )
        assert "/login" in response.headers["Location"], (
            "Redirect location should point to /login"
        )


# ------------------------------------------------------------------ #
# 2. Default filter (no ?filter param)                               #
# ------------------------------------------------------------------ #

class TestProfileDefaultFilter:

    def test_default_filter_is_this_month(self, auth_client):
        """GET /profile with no ?filter param defaults to 'This Month' (active button)."""
        response = auth_client.get("/profile")
        assert response.status_code == 200, (
            "Expected 200 for authenticated GET /profile"
        )
        assert b'filter-btn active">This Month' in response.data, (
            "Expected the 'This Month' button to carry the 'active' CSS class "
            "when no filter query parameter is provided"
        )


# ------------------------------------------------------------------ #
# 3–5. Preset filter buttons                                         #
# ------------------------------------------------------------------ #

class TestProfilePresetFilters:

    def test_filter_all_time(self, auth_client):
        """?filter=all → 'All Time' button active; 'All Time' text in response as period label."""
        response = auth_client.get("/profile?filter=all")
        assert response.status_code == 200, "Expected 200 for ?filter=all"
        assert b'filter-btn active">All Time' in response.data, (
            "Expected the 'All Time' button to carry the 'active' CSS class"
        )
        assert b"All Time" in response.data, (
            "Expected 'All Time' to appear as the period label text in the response"
        )

    def test_filter_last_3_months(self, auth_client):
        """?filter=last_3 → 'Last 3 Months' button active, response is 200."""
        response = auth_client.get("/profile?filter=last_3")
        assert response.status_code == 200, "Expected 200 for ?filter=last_3"
        assert b'filter-btn active">Last 3 Months' in response.data, (
            "Expected the 'Last 3 Months' button to carry the 'active' CSS class"
        )

    def test_filter_last_6_months(self, auth_client):
        """?filter=last_6 → 'Last 6 Months' button active, response is 200."""
        response = auth_client.get("/profile?filter=last_6")
        assert response.status_code == 200, "Expected 200 for ?filter=last_6"
        assert b'filter-btn active">Last 6 Months' in response.data, (
            "Expected the 'Last 6 Months' button to carry the 'active' CSS class"
        )


# ------------------------------------------------------------------ #
# 6–9. Custom date filter                                            #
# ------------------------------------------------------------------ #

class TestProfileCustomFilter:

    def test_filter_custom_valid(self, auth_client):
        """Valid custom range → 200, formatted period label, 'Custom' button active."""
        response = auth_client.get(
            "/profile?filter=custom&start=2026-06-01&end=2026-08-28"
        )
        assert response.status_code == 200, (
            "Expected 200 for a valid custom date range"
        )
        text = response.get_data(as_text=True)
        assert "01 Jun" in text, (
            "Expected the formatted start date '01 Jun' to appear in the period label"
        )
        assert "28 Aug 2026" in text, (
            "Expected the formatted end date '28 Aug 2026' to appear in the period label"
        )
        assert 'filter-btn active">Custom' in text, (
            "Expected the 'Custom' button to carry the 'active' CSS class"
        )

    def test_filter_custom_swapped_dates(self, auth_client):
        """start > end → dates are silently normalised; response is still 200."""
        response = auth_client.get(
            "/profile?filter=custom&start=2026-08-28&end=2026-06-01"
        )
        assert response.status_code == 200, (
            "Expected 200 even when start date is later than end date — "
            "the route should swap them rather than returning an error"
        )

    def test_filter_custom_invalid_dates_fall_back(self, auth_client):
        """?filter=custom with unparseable dates → fallback to 'This Month' (200)."""
        response = auth_client.get(
            "/profile?filter=custom&start=bad&end=also_bad"
        )
        assert response.status_code == 200, (
            "Expected 200 even when custom date values cannot be parsed"
        )
        assert b'filter-btn active">This Month' in response.data, (
            "Expected fallback to 'This Month' when custom date strings are invalid"
        )

    def test_custom_row_visible_when_active(self, auth_client):
        """?filter=custom with valid dates → custom-row div rendered with display:flex.

        The custom-row div is the only element on the page that uses gap: 10px in its
        inline style (template line: display: flex/none; ... gap: 10px; flex-wrap: wrap).
        Checking for 'display: flex; align-items: center; gap: 10px' is therefore a
        narrow, unique assertion that confirms specifically the custom-row is visible
        rather than matching one of the many other flex elements on the page.
        """
        response = auth_client.get(
            "/profile?filter=custom&start=2026-06-01&end=2026-07-31"
        )
        assert response.status_code == 200, (
            "Expected 200 for custom filter with valid dates"
        )
        assert b"display: flex; align-items: center; gap: 10px" in response.data, (
            "Expected the custom-row div to have 'display: flex' in its inline style "
            "when filter=custom is active. The gap: 10px is unique to the custom-row "
            "element and distinguishes it from other flex containers on the page."
        )


# ------------------------------------------------------------------ #
# 8. Invalid / unknown filter value fallback                         #
# ------------------------------------------------------------------ #

class TestProfileInvalidFilterFallback:

    def test_filter_invalid_falls_back(self, auth_client):
        """?filter=xyz (unrecognised value) → 200, fallback to 'This Month' active."""
        response = auth_client.get("/profile?filter=xyz")
        assert response.status_code == 200, (
            "Expected 200 for an unknown filter value"
        )
        assert b'filter-btn active">This Month' in response.data, (
            "Expected fallback to 'This Month' for an unrecognised ?filter value"
        )


# ------------------------------------------------------------------ #
# 10–11. Always-rendered stat card elements                          #
# ------------------------------------------------------------------ #

class TestProfileAlwaysRenderedStatCards:

    def test_all_time_total_always_rendered(self, auth_client):
        """The 'All Time' stat card label is always present, regardless of filter."""
        response = auth_client.get("/profile?filter=this_month")
        assert response.status_code == 200, "Expected 200 for ?filter=this_month"
        assert b"All Time" in response.data, (
            "Expected the 'All Time' stat card to be rendered even when filter=this_month"
        )

    def test_expense_count_always_rendered(self, auth_client):
        """The 'Expenses' stat card label is always present, regardless of filter."""
        response = auth_client.get("/profile?filter=last_3")
        assert response.status_code == 200, "Expected 200 for ?filter=last_3"
        assert b"Expenses" in response.data, (
            "Expected the 'Expenses' stat card to be rendered even when filter=last_3"
        )
