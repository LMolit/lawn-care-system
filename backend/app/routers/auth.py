import jwt
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import (
    email_change_limit,
    login_failures,
    login_limit,
    password_change_limit,
    refresh_limit,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.crud.user import get_user_by_email, get_user_by_id
from app.db.base import User
from app.dependencies import get_current_user, get_db
from app.schemas.auth import (
    AccessTokenResponse,
    ChangeEmailRequest,
    ChangePasswordRequest,
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
    # Same normalization as the lookup, so "Owner@X.com" and "owner@x.com" share a count.
    email_key = credentials.email.strip().lower()

    # Checked before any password work. A locked email never reaches bcrypt,
    # so an attacker can't burn our CPU on it either.
    login_failures.check(email_key)

    user = get_user_by_email(db, credentials.email)

    if (
        user is None
        or not user.active
        or not verify_password(credentials.password, user.password_hash)
    ):
        # Recorded for unknown emails too, so lockout reveals nothing about accounts.
        login_failures.record_failure(email_key)
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    login_failures.clear(email_key)

    access_token = create_access_token(user.id, user.token_version)
    refresh_token = create_refresh_token(user.id, user.token_version)

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

    if payload.get("ver") != user.token_version:
        raise HTTPException(status_code=401, detail="Token has been revoked")

    new_token = create_access_token(user_id, user.token_version)

    return AccessTokenResponse(access_token=new_token)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/change-password",
    response_model=TokenResponse,
    dependencies=[Depends(password_change_limit)],
)
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TokenResponse:
    # Even with a valid token we ask for the current password: a stolen
    # short-lived token must not be enough to lock the owner out.
    # 400, not 401: the web app treats 401 as "session expired".
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.password_hash = hash_password(body.new_password)
    # Bumping the version invalidates every token issued so far, on every device.
    current_user.token_version += 1
    db.commit()
    db.refresh(current_user)

    # The person who just changed it stays logged in, with fresh tokens.
    return TokenResponse(
        access_token=create_access_token(current_user.id, current_user.token_version),
        refresh_token=create_refresh_token(current_user.id, current_user.token_version),
    )


@router.post(
    "/change-email",
    response_model=TokenResponse,
    dependencies=[Depends(email_change_limit)],
)
def change_email(
    body: ChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TokenResponse:
    # Password first, so a stolen token can't be used to probe which
    # addresses are registered.
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    new_email = body.new_email.strip().lower()
    existing = get_user_by_email(db, new_email)
    if existing is not None:
        if existing.id == current_user.id:
            raise HTTPException(
                status_code=400, detail="That is already your email address"
            )
        raise HTTPException(
            status_code=409, detail="That email address is already in use"
        )

    current_user.email = new_email
    current_user.token_version += 1
    db.commit()
    db.refresh(current_user)

    return TokenResponse(
        access_token=create_access_token(current_user.id, current_user.token_version),
        refresh_token=create_refresh_token(current_user.id, current_user.token_version),
    )


@router.post("/logout-everywhere", status_code=204)
def logout_everywhere(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    # Every token issued so far carries the old version, so all of them die,
    # including the one used for this request. No new tokens are returned on
    # purpose: a stolen access token must not be convertible into a 30-day
    # refresh token. The caller has to log in again.
    current_user.token_version += 1
    db.commit()
    return Response(status_code=204)
