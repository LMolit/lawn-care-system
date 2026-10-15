from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

MAX_PASSWORD_BYTES = 72  # bcrypt cannot handle more than this


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode("utf-8")
    if len(plain_bytes) > MAX_PASSWORD_BYTES:
        # No password this long could ever have been stored, so it can't match.
        return False
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_access_token(user_id: int, token_version: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "ver": token_version,
        "exp": expires_at,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_refresh_token(user_id: int, token_version: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_expire_days
    )
    payload = {
        "sub": str(user_id),
        "ver": token_version,
        "exp": expires_at,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
