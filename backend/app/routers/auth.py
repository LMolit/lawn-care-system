import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import login_limit, refresh_limit
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.crud.user import get_user_by_email, get_user_by_id
from app.db.base import User
from app.dependencies import get_current_user, get_db
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/login", response_model=TokenResponse, dependencies=[Depends(login_limit)]
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = get_user_by_email(db, credentials.email)

    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    dependencies=[Depends(refresh_limit)],
)
def get_new_access_token(
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> AccessTokenResponse:

    try:
        payload = jwt.decode(
            body.refresh_token, settings.jwt_secret, algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(payload.get("sub"))
    user = get_user_by_id(db, user_id)

    if user is None or not user.active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    new_token = create_access_token(user_id)

    return AccessTokenResponse(access_token=new_token)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
