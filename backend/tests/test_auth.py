from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.db.base import User

EMAIL = "owner@lawncare.local"
PASSWORD = "correct-horse-battery"
NEW_PASSWORD = "a-brand-new-passphrase"
# bcrypt is deliberately slow, so hash once for the whole file
PASSWORD_HASH = hash_password(PASSWORD)


@pytest.fixture()
def owner(db_session):
    user = User(email=EMAIL, password_hash=PASSWORD_HASH, name="Owner")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _login(client, email=EMAIL, password=PASSWORD):
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


def _change_password(client, token, current=PASSWORD, new=NEW_PASSWORD):
    return client.post(
        "/api/v1/auth/change-password",
        headers=_bearer(token),
        json={"current_password": current, "new_password": new},
    )


# --- login, me, refresh (existing behavior) ---


def test_login_returns_both_tokens(client, owner):
    response = _login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


def test_login_wrong_password_is_401(client, owner):
    assert _login(client, password="not-the-password").status_code == 401


def test_login_unknown_email_looks_the_same_as_wrong_password(client, owner):
    wrong_password = _login(client, password="not-the-password")
    unknown_email = _login(client, email="nobody@lawncare.local")
    assert unknown_email.status_code == 401
    assert unknown_email.json() == wrong_password.json()


def test_login_overlong_password_is_401_not_a_crash(client, owner):
    assert _login(client, password="x" * 100).status_code == 401


def test_me_returns_the_logged_in_user(client, owner):
    token = _login(client).json()["access_token"]
    response = client.get("/api/v1/auth/me", headers=_bearer(token))
    assert response.status_code == 200
    assert response.json()["email"] == EMAIL


def test_me_without_a_token_is_401(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_rejects_a_refresh_token(client, owner):
    refresh = create_refresh_token(owner.id, owner.token_version)
    assert client.get("/api/v1/auth/me", headers=_bearer(refresh)).status_code == 401


def test_refresh_issues_a_new_access_token(client, owner):
    refresh = create_refresh_token(owner.id, owner.token_version)
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_refresh_rejects_an_access_token(client, owner):
    access = create_access_token(owner.id, owner.token_version)
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": access})
    assert response.status_code == 401


# --- token versioning ---


def test_token_with_an_old_version_is_rejected_by_me(client, owner, db_session):
    token = _login(client).json()["access_token"]
    owner.token_version += 1  # what a password change does
    db_session.commit()
    assert client.get("/api/v1/auth/me", headers=_bearer(token)).status_code == 401


def test_refresh_token_with_an_old_version_is_rejected(client, owner, db_session):
    refresh = _login(client).json()["refresh_token"]
    owner.token_version += 1
    db_session.commit()
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 401


def test_token_issued_before_versioning_is_rejected(client, owner):
    # Hand-built to look like the tokens that exist today: no "ver" claim.
    payload = {
        "sub": str(owner.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "type": "access",
    }
    legacy = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    assert client.get("/api/v1/auth/me", headers=_bearer(legacy)).status_code == 401


def test_access_token_from_refresh_still_works(client, owner):
    refresh = _login(client).json()["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    new_access = response.json()["access_token"]
    assert client.get("/api/v1/auth/me", headers=_bearer(new_access)).status_code == 200


def test_inactive_user_cannot_log_in(client, owner, db_session):
    owner.active = False
    db_session.commit()
    assert _login(client).status_code == 401


# --- change password ---


def test_change_password_returns_working_new_tokens(client, owner):
    token = _login(client).json()["access_token"]
    response = _change_password(client, token)
    assert response.status_code == 200
    body = response.json()
    assert (
        client.get("/api/v1/auth/me", headers=_bearer(body["access_token"])).status_code
        == 200
    )
    refreshed = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": body["refresh_token"]}
    )
    assert refreshed.status_code == 200


def test_change_password_switches_which_password_logs_in(client, owner):
    token = _login(client).json()["access_token"]
    _change_password(client, token)
    assert _login(client, password=NEW_PASSWORD).status_code == 200
    assert _login(client, password=PASSWORD).status_code == 401


def test_change_password_revokes_the_old_tokens(client, owner):
    tokens = _login(client).json()
    _change_password(client, tokens["access_token"])
    me = client.get("/api/v1/auth/me", headers=_bearer(tokens["access_token"]))
    assert me.status_code == 401
    refresh = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh.status_code == 401


def test_change_password_stores_a_hash(client, owner, db_session):
    token = _login(client).json()["access_token"]
    _change_password(client, token)
    db_session.refresh(owner)
    assert owner.password_hash != NEW_PASSWORD
    assert verify_password(NEW_PASSWORD, owner.password_hash)


def test_change_password_with_wrong_current_password_is_400(client, owner):
    token = _login(client).json()["access_token"]
    # 400, not 401: the web app treats 401 as "session expired"
    assert (
        _change_password(client, token, current="not-the-password").status_code == 400
    )


def test_wrong_current_password_changes_nothing(client, owner):
    token = _login(client).json()["access_token"]
    _change_password(client, token, current="not-the-password")
    assert _login(client).status_code == 200  # old password still works
    assert (
        client.get("/api/v1/auth/me", headers=_bearer(token)).status_code == 200
    )  # not logged out


def test_change_password_rejects_a_short_password(client, owner):
    token = _login(client).json()["access_token"]
    assert _change_password(client, token, new="short").status_code == 422


def test_change_password_rejects_more_than_72_bytes(client, owner):
    token = _login(client).json()["access_token"]
    # 37 characters, but 74 bytes in UTF-8
    assert _change_password(client, token, new="é" * 37).status_code == 422


def test_change_password_rejects_the_same_password(client, owner):
    token = _login(client).json()["access_token"]
    assert _change_password(client, token, new=PASSWORD).status_code == 422


def test_change_password_requires_auth(client, owner):
    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": PASSWORD, "new_password": NEW_PASSWORD},
    )
    assert response.status_code == 401


def test_change_password_rejects_a_refresh_token(client, owner):
    refresh = create_refresh_token(owner.id, owner.token_version)
    assert _change_password(client, refresh).status_code == 401


def test_change_password_is_rate_limited(client, owner):
    token = _login(client).json()["access_token"]
    for _ in range(5):
        assert (
            _change_password(client, token, current="not-the-password").status_code
            == 400
        )
    assert (
        _change_password(client, token, current="not-the-password").status_code == 429
    )
