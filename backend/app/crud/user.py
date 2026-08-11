from sqlalchemy.orm import Session

from app.db.base import User

def get_user_by_email(db:Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


