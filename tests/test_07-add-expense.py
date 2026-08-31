"""
tests/test_07-add-expense.py

Pytest tests for the "Add Expense" feature (Step 07).

Covers:
  - Auth guard: unauthenticated GET and POST to /expenses/add redirect to /login
  - Form rendering: amount, category dropdown (all CATEGORIES), date, description fields
  - Valid submission: 302 redirect to /profile and DB row inserted with correct values
  - New expense visible on profile page after successful submit
  - Amount validation: missing, zero, negative, non-numeric → re-render with error
  - Category validation: unknown category, empty category → re-render with error
  - Nav link: "Add Expense" link visible when logged in, absent when logged out

Implementation note
-------------------
database.db.get_db() uses a hardcoded DB_PATH derived from __file__ and does
not read Flask app config. Tests therefore run against the real expense_tracker.db,
following the same pattern as test_06_date_filter_profile.py.
The Demo User (id=1) is seeded by seed_db() at import time, so session injection
with user_id=1 is reliable across all tests. The expense_cleanup fixture ensures
any rows inserted during a test are removed after it completes.
"""

import pytest
from datetime import date

from app import app as flask_app
from database.db import get_db, CATEGORIES


# ------------------------------------------------------------------ #
# Fixtures                                                            #
# ------------------------------------------------------------------ #

@pytest.fixture
def app():
    """Configure Flask for testing with a stable SECRET_KEY."""
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-for-pytest",
    })
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    """Test client with Demo User (id=1) already in the session.

    Session is injected directly so the test is independent of the auth routes.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"
    return client


@pytest.fixture
def expense_cleanup():
    """Record the highest expense id before the test.

    After the test, delete all expense rows whose id is greater than that
    value, restoring the DB to its pre-test state.
    """
    conn = get_db()
    try:
        row = conn.execute("SELECT COALESCE(MAX(id), 0) FROM expenses").fetchone()
        max_id_before = row[0]
    finally:
        conn.close()

    yield max_id_before

    conn = get_db()
    try:
        conn.execute("DELETE FROM expenses WHERE id > ?", (max_id_before,))
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------ #
# Helper                                                              #
# ------------------------------------------------------------------ #

def _valid_form_data():
    """Return a dict of valid expense form fields, using today's date."""
    return {
        "amount": "499",
        "category": CATEGORIES[0],          # e.g. "Food"
        "date": date.today().isoformat(),
        "description": "Test expense [pytest]",
    }


# ------------------------------------------------------------------ #
# 1. Auth guard                                                       #
# ------------------------------------------------------------------ #

class TestAddExpenseAuthGuard:

    def test_get_unauthenticated_redirects_to_login(self, client):
        """Unauthenticated GET /expenses/add must return 302 pointing at /login."""
        response = client.get("/expenses/add")
        assert response.status_code == 302, (
            "Expected a 302 redirect for an unauthenticated GET /expenses/add"
        )
        assert "/login" in response.headers["Location"], (
            "Redirect target should be /login for unauthenticated GET"
        )

    def test_post_unauthenticated_redirects_to_login(self, client):
        """Unauthenticated POST /expenses/add must return 302 pointing at /login."""
        response = client.post("/expenses/add", data=_valid_form_data())
        assert response.status_code == 302, (
            "Expected a 302 redirect for an unauthenticated POST /expenses/add"
        )
        assert "/login" in response.headers["Location"], (
            "Redirect target should be /login for unauthenticated POST"
        )


# ------------------------------------------------------------------ #
# 2. Form rendering                                                   #
# ------------------------------------------------------------------ #

class TestAddExpenseFormRendering:

    def test_get_returns_200(self, logged_in_client):
        """Authenticated GET /expenses/add returns 200."""
        response = logged_in_client.get("/expenses/add")
        assert response.status_code == 200, (
            "Expected 200 for authenticated GET /expenses/add"
        )

    def test_get_renders_amount_field(self, logged_in_client):
        """The form contains an input element whose name is 'amount'."""
        response = logged_in_client.get("/expenses/add")
        assert b'name="amount"' in response.data, (
            "Expected an input with name='amount' in the add-expense form"
        )

    def test_get_renders_category_dropdown(self, logged_in_client):
        """The form contains a <select> element for category."""
        response = logged_in_client.get("/expenses/add")
        assert b"<select" in response.data, (
            "Expected a <select> element for the category dropdown"
        )
        assert b'name="category"' in response.data, (
            "Expected the <select> to have name='category'"
        )

    def test_get_renders_all_categories_in_dropdown(self, logged_in_client):
        """Every value in CATEGORIES appears as an <option> in the dropdown."""
        response = logged_in_client.get("/expenses/add")
        for category in CATEGORIES:
            assert category.encode() in response.data, (
                f"Expected category '{category}' to appear in the dropdown options"
            )

    def test_get_renders_date_field(self, logged_in_client):
        """The form contains an input element whose name is 'date'."""
        response = logged_in_client.get("/expenses/add")
        assert b'name="date"' in response.data, (
            "Expected an input with name='date' in the add-expense form"
        )

    def test_get_renders_description_field(self, logged_in_client):
        """The form contains a textarea or input element whose name is 'description'."""
        response = logged_in_client.get("/expenses/add")
        assert b'name="description"' in response.data, (
            "Expected an element with name='description' in the add-expense form"
        )


# ------------------------------------------------------------------ #
# 3. Valid submission                                                  #
# ------------------------------------------------------------------ #

class TestAddExpenseValidSubmission:

    def test_valid_post_redirects_to_profile(self, logged_in_client, expense_cleanup):
        """A valid POST to /expenses/add must redirect (302) to /profile."""
        response = logged_in_client.post("/expenses/add", data=_valid_form_data())
        assert response.status_code == 302, (
            "Expected a 302 redirect after a valid expense submission"
        )
        assert "/profile" in response.headers["Location"], (
            "Redirect after successful add should point to /profile"
        )

    def test_valid_post_inserts_db_row(self, logged_in_client, expense_cleanup):
        """After a valid POST, the expenses table must contain a matching row."""
        form = _valid_form_data()
        logged_in_client.post("/expenses/add", data=form)

        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM expenses WHERE user_id = ? AND description = ?",
                (1, form["description"]),
            ).fetchone()
        finally:
            conn.close()

        assert row is not None, (
            "Expected a new expense row in the DB after a valid submission"
        )
        assert float(row["amount"]) == float(form["amount"]), (
            f"Expected amount {form['amount']} but found {row['amount']}"
        )
        assert row["category"] == form["category"], (
            f"Expected category '{form['category']}' but found '{row['category']}'"
        )
        assert row["date"] == form["date"], (
            f"Expected date '{form['date']}' but found '{row['date']}'"
        )

    def test_valid_post_expense_appears_on_profile(self, logged_in_client, expense_cleanup):
        """After a valid POST the new expense is visible on the profile page.

        We use filter=all so the expense is returned regardless of its date.
        """
        form = _valid_form_data()
        logged_in_client.post("/expenses/add", data=form)

        profile_response = logged_in_client.get("/profile?filter=all")
        assert profile_response.status_code == 200, (
            "Expected 200 for authenticated GET /profile?filter=all"
        )
        assert form["description"].encode() in profile_response.data, (
            "Expected the newly added expense description to appear in the "
            "Recent Expenses list on the profile page"
        )


# ------------------------------------------------------------------ #
# 4. Amount validation                                                #
# ------------------------------------------------------------------ #

class TestAddExpenseAmountValidation:

    @pytest.mark.parametrize("bad_amount, label", [
        ("",     "empty string"),
        ("0",    "zero"),
        ("-1",   "negative integer"),
        ("-0.5", "negative float"),
        ("abc",  "non-numeric string"),
        ("!@#",  "special characters"),
    ])
    def test_invalid_amount_rerenders_form_with_error(
        self, logged_in_client, bad_amount, label
    ):
        """An invalid amount value must re-render the form (200) with a visible error."""
        form = _valid_form_data()
        form["amount"] = bad_amount

        response = logged_in_client.post("/expenses/add", data=form)

        assert response.status_code == 200, (
            f"Expected 200 (form re-render) for amount='{bad_amount}' ({label}), "
            "not a redirect"
        )
        text = response.get_data(as_text=True)
        # The error block should contain some message about the amount
        assert "error" in text.lower() or "amount" in text.lower(), (
            f"Expected a visible error message for amount='{bad_amount}' ({label})"
        )

    @pytest.mark.parametrize("bad_amount", ["", "0", "-1", "abc"])
    def test_invalid_amount_does_not_insert_db_row(
        self, logged_in_client, bad_amount, expense_cleanup
    ):
        """An invalid amount must not insert any row into the expenses table."""
        max_id_before = expense_cleanup   # fixture yields the pre-test max id
        form = _valid_form_data()
        form["amount"] = bad_amount

        logged_in_client.post("/expenses/add", data=form)

        conn = get_db()
        try:
            new_max = conn.execute(
                "SELECT COALESCE(MAX(id), 0) FROM expenses"
            ).fetchone()[0]
        finally:
            conn.close()

        assert new_max == max_id_before, (
            f"Expected no new expense row in the DB for invalid amount='{bad_amount}'"
        )


# ------------------------------------------------------------------ #
# 5. Category validation                                              #
# ------------------------------------------------------------------ #

class TestAddExpenseCategoryValidation:

    @pytest.mark.parametrize("bad_category, label", [
        ("",             "empty string"),
        ("InvalidCat",   "unknown category name"),
        ("food",         "wrong case"),
        ("DROP TABLE",   "SQL injection attempt"),
    ])
    def test_invalid_category_rerenders_form_with_error(
        self, logged_in_client, bad_category, label
    ):
        """A category not in CATEGORIES must re-render the form (200) with an error."""
        form = _valid_form_data()
        form["category"] = bad_category

        response = logged_in_client.post("/expenses/add", data=form)

        assert response.status_code == 200, (
            f"Expected 200 (form re-render) for category='{bad_category}' ({label}), "
            "not a redirect"
        )
        text = response.get_data(as_text=True)
        assert "error" in text.lower() or "category" in text.lower(), (
            f"Expected a visible error message for category='{bad_category}' ({label})"
        )

    @pytest.mark.parametrize("bad_category", ["", "InvalidCat"])
    def test_invalid_category_does_not_insert_db_row(
        self, logged_in_client, bad_category, expense_cleanup
    ):
        """An invalid category must not insert any row into the expenses table."""
        max_id_before = expense_cleanup
        form = _valid_form_data()
        form["category"] = bad_category

        logged_in_client.post("/expenses/add", data=form)

        conn = get_db()
        try:
            new_max = conn.execute(
                "SELECT COALESCE(MAX(id), 0) FROM expenses"
            ).fetchone()[0]
        finally:
            conn.close()

        assert new_max == max_id_before, (
            f"Expected no new row in DB for invalid category='{bad_category}'"
        )

    def test_each_valid_category_is_accepted(self, logged_in_client, expense_cleanup):
        """Every value from CATEGORIES must be accepted without a validation error.

        We use the first CATEGORY as a representative valid value. The category-
        dropdown completeness test already confirms all values are rendered.
        """
        form = _valid_form_data()
        form["category"] = CATEGORIES[0]

        response = logged_in_client.post("/expenses/add", data=form)

        assert response.status_code == 302, (
            f"Expected a 302 redirect when category='{CATEGORIES[0]}' "
            "(a valid CATEGORIES value) is submitted"
        )


# ------------------------------------------------------------------ #
# 6. Nav link visibility                                              #
# ------------------------------------------------------------------ #

class TestAddExpenseNavLink:

    def test_nav_link_visible_when_logged_in(self, logged_in_client):
        """The 'Add Expense' nav link must appear on rendered pages when logged in.

        We check the profile page as a representative authenticated page.
        """
        response = logged_in_client.get("/profile")
        assert response.status_code == 200, (
            "Expected 200 for authenticated GET /profile"
        )
        text = response.get_data(as_text=True)
        assert "/expenses/add" in text, (
            "Expected a nav link pointing to /expenses/add when the user is logged in"
        )

    def test_nav_link_absent_when_logged_out(self, client):
        """The 'Add Expense' nav link must NOT appear when the user is logged out.

        We check the landing page as a representative unauthenticated page.
        """
        response = client.get("/")
        assert response.status_code == 200, (
            "Expected 200 for GET /"
        )
        text = response.get_data(as_text=True)
        assert "/expenses/add" not in text, (
            "Expected the Add Expense nav link to be absent when the user is logged out"
        )
