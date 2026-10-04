"""One-time script: create the single admin user.

Run inside the backend container:
    docker compose exec backend python -m scripts.create_admin
"""

import getpass
import sys

from sqlalchemy import func, select

from app.core.security import hash_password
from app.db.base import User
from app.db.session import SessionLocal


def main() -> None:
    columns = {c.key for c in User.__table__.columns}
    password_columns = [c for c in columns if "password" in c]
    if len(password_columns) != 1:
        sys.exit(f"Expected one password column, found: {password_columns}")

    with SessionLocal() as db:
        existing = db.scalar(select(func.count()).select_from(User))
        if existing:
            sys.exit(f"Aborting: users table already has {existing} row(s).")

        email = input("Admin email: ").strip()
        name = input("Your name: ").strip()
        if not name:
            sys.exit("Name is required.")
        password = getpass.getpass("Password (min 12 characters): ")
        if len(password) < 12:
            sys.exit("Password too short.")
        if password != getpass.getpass("Confirm password: "):
            sys.exit("Passwords did not match.")

        values = {
            "email": email,
            "name": name,
            password_columns[0]: hash_password(password),
        }
        if "active" in columns:
            values["active"] = True

        db.add(User(**values))
        db.commit()
        print(f"Created admin user {email}")


if __name__ == "__main__":
    main()
