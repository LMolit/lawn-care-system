import getpass

from app.db.session import SessionLocal
from app.db.base import User
from app.core.security import hash_password

def main():
    email = input("User email: ")
    password = getpass.getpass("New password: ")

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        print(f"No user found with email {email}")
        return

    user.password_hash = hash_password(password)
    db.commit()
    print(f"Password update for {email}")

if __name__ == "__main__":
    main()
