from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.base import User


def get_user_by_email(db: Session, email: str) -> User | None:
    # Case-insensitive on both sides, so "Owner@x.com" finds "owner@x.com".
    # The users table has one row, so skipping the index on email is fine.
    return (
        db.query(User).filter(func.lower(User.email) == email.strip().lower()).first()
    )


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)
