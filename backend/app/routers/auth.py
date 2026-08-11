from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt

from app.dependencies import get_db, get_current_user
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, AccessTokenResponse, RefreshRequest
from app.crud.user import get_user_by_email, get_user_by_id
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.db.base import User
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, credentials.email)

    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=AccessTokenResponse)
def get_new_access_token(
        body: RefreshRequest,
        db: Session = Depends(get_db),
        ) -> AccessTokenResponse:

    try:
        payload = jwt.decode(body.refresh_token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate credentails")

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

