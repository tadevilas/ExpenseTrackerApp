import random
from datetime import datetime

from werkzeug.security import generate_password_hash

from database.db import get_db


FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Krishna", "Ishaan",
    "Rahul", "Rohan", "Rohit", "Karan", "Kabir", "Aryan", "Dev", "Siddharth",
    "Nikhil", "Manish", "Sanjay", "Rajesh", "Amit", "Suresh", "Ramesh", "Vikram",
    "Ananya", "Aadhya", "Diya", "Isha", "Kavya", "Priya", "Riya", "Sanya",
    "Aishwarya", "Divya", "Meera", "Neha", "Pooja", "Sneha", "Shreya", "Anjali",
    "Kiran", "Nisha", "Deepa", "Swati", "Preeti", "Ritu", "Sunita", "Anita",
    "Arjun", "Harsh", "Yash", "Aditi", "Tanvi", "Simran", "Nandini", "Ishita",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Agarwal", "Singh", "Kumar", "Patel", "Shah",
    "Mehta", "Joshi", "Trivedi", "Chopra", "Kapoor", "Malhotra", "Bhatia",
    "Reddy", "Rao", "Naidu", "Iyer", "Iyengar", "Menon", "Nair", "Pillai",
    "Chatterjee", "Banerjee", "Mukherjee", "Ghosh", "Bose", "Dutta", "Sen",
    "Desai", "Patil", "Deshmukh", "Kulkarni", "Jadhav", "Bhosale", "Gaikwad",
    "Khanna", "Chauhan", "Yadav", "Mishra", "Tiwari", "Pandey", "Dubey", "Shukla",
    "Saxena", "Srivastava", "Bhattacharya", "Krishnan", "Subramanian",
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]


def generate_user():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    suffix = random.randint(10, 999)
    domain = random.choice(EMAIL_DOMAINS)
    email = f"{first.lower()}.{last.lower()}{suffix}@{domain}"
    return name, email


def email_exists(conn, email):
    row = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
    return row is not None


def main():
    conn = get_db()
    try:
        while True:
            name, email = generate_user()
            if not email_exists(conn, email):
                break

        password_hash = generate_password_hash("password123")
        created_at = datetime.now().isoformat(sep=" ", timespec="seconds")

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, created_at),
        )
        conn.commit()
        user_id = cursor.lastrowid

        print(f"id: {user_id}")
        print(f"name: {name}")
        print(f"email: {email}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
