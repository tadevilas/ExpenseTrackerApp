import random
import sys
from datetime import date, timedelta

from database.db import get_db


USER_ID = 2
COUNT = 5
MONTHS = 4


CATEGORY_WEIGHTS = [
    ("Food", 30),
    ("Transport", 20),
    ("Bills", 15),
    ("Shopping", 12),
    ("Other", 10),
    ("Health", 7),
    ("Entertainment", 6),
]

AMOUNT_RANGES = {
    "Food": (50, 800),
    "Transport": (20, 500),
    "Bills": (200, 3000),
    "Health": (100, 2000),
    "Entertainment": (100, 1500),
    "Shopping": (200, 5000),
    "Other": (50, 1000),
}

DESCRIPTIONS = {
    "Food": [
        "Groceries at DMart", "Vegetables from local sabziwala", "Zomato dinner",
        "Swiggy lunch", "Chai and samosa", "Milk and bread", "Weekend brunch",
        "Biryani takeaway", "Office canteen lunch", "Paneer tikka dinner",
        "Dosa breakfast", "Fruits from market",
    ],
    "Transport": [
        "Ola cab to office", "Uber ride", "Metro card top-up", "Auto rickshaw",
        "Petrol refill", "Bus pass renewal", "IRCTC train ticket", "Rapido bike",
        "Parking fee", "Toll charges",
    ],
    "Bills": [
        "Electricity bill", "Water bill", "Airtel postpaid", "Jio recharge",
        "Broadband - ACT Fibernet", "DTH recharge - Tata Play", "Gas cylinder refill",
        "Society maintenance", "Netflix subscription", "Amazon Prime renewal",
    ],
    "Health": [
        "Apollo pharmacy", "Doctor consultation", "Diagnostic tests at Thyrocare",
        "Dental checkup", "Gym membership", "Multivitamins", "Eye checkup",
        "Physiotherapy session",
    ],
    "Entertainment": [
        "PVR movie tickets", "BookMyShow concert", "Spotify Premium",
        "Weekend at Snow World", "Cricket match tickets", "Board game night",
        "Amusement park entry",
    ],
    "Shopping": [
        "Myntra order", "Flipkart electronics", "Amazon shopping", "Ajio clothing",
        "Kurta from FabIndia", "Sneakers from Nike", "Reliance Trends shirts",
        "Home decor from IKEA", "Books from Crossword", "Nykaa cosmetics",
    ],
    "Other": [
        "Notebook and stationery", "Gift for friend", "Donation", "Salon visit",
        "Dry cleaning", "Photocopy and printing", "Puja items", "Miscellaneous",
    ],
}


def weighted_category():
    cats = [c for c, _ in CATEGORY_WEIGHTS]
    weights = [w for _, w in CATEGORY_WEIGHTS]
    return random.choices(cats, weights=weights, k=1)[0]


def random_date_within(months):
    today = date.today()
    days_back = months * 30
    delta = random.randint(0, days_back)
    return (today - timedelta(days=delta)).isoformat()


def user_exists(conn, user_id):
    row = conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
    return row is not None


def main():
    conn = get_db()
    try:
        if not user_exists(conn, USER_ID):
            print(f"No user found with id {USER_ID}.")
            sys.exit(1)

        rows = []
        for _ in range(COUNT):
            category = weighted_category()
            lo, hi = AMOUNT_RANGES[category]
            amount = round(random.uniform(lo, hi), 2)
            expense_date = random_date_within(MONTHS)
            description = random.choice(DESCRIPTIONS[category])
            rows.append((USER_ID, amount, category, expense_date, description))

        try:
            inserted_ids = []
            for row in rows:
                cur = conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) "
                    "VALUES (?, ?, ?, ?, ?)",
                    row,
                )
                inserted_ids.append(cur.lastrowid)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Insert failed, rolled back: {e}")
            sys.exit(1)

        placeholders = ",".join("?" for _ in inserted_ids)
        inserted = conn.execute(
            f"SELECT id, amount, category, date, description "
            f"FROM expenses WHERE id IN ({placeholders}) ORDER BY date",
            inserted_ids,
        ).fetchall()

        dates = [r["date"] for r in inserted]
        print(f"Inserted {len(inserted)} expenses for user_id={USER_ID}")
        print(f"Date range: {min(dates)} -> {max(dates)}")
        print()
        print("Sample records:")
        for r in inserted[:5]:
            print(f"  id={r['id']} | {r['date']} | {r['category']:<14} | "
                  f"Rs.{r['amount']:>8.2f} | {r['description']}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
