"""Create a FitAI administrator account from the terminal. No public admin signup exists."""
import getpass
import re

from werkzeug.security import generate_password_hash
from database import init_db, query_db, execute_db


def main():
    init_db()
    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip().lower()
    full_name = input("Admin full name: ").strip()
    password = getpass.getpass("Admin password (12+ characters): ")
    confirm = getpass.getpass("Confirm password: ")

    if not username or not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise SystemExit("Enter a username and valid email address.")
    if len(password) < 12:
        raise SystemExit("Use at least 12 characters for the administrator password.")
    if password != confirm:
        raise SystemExit("Passwords do not match.")
    if query_db("SELECT id FROM users WHERE LOWER(username)=LOWER(?) OR LOWER(email)=LOWER(?)", (username, email), one=True):
        raise SystemExit("That username or email already exists. Admin accounts must be created separately from normal registration.")

    execute_db("INSERT INTO users (username, email, password_hash, full_name, role, is_active) VALUES (?, ?, ?, ?, 'admin', 1)",
               (username, email, generate_password_hash(password), full_name))
    print("Administrator created. Sign in at /admin/login. Keep this account's credentials private.")


if __name__ == "__main__":
    main()
