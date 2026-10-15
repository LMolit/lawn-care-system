import pytest

from app.core.security import create_refresh_token, hash_password
from app.db.base import User

EMAIL = "owner@example.com"
NEW_EMAIL = "new.owner@example.com"
PASSWORD = "correct-horse-battery"
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


def _change_email(client, token, current=PASSWORD, new=NEW_EMAIL):
    return client.post(
        "/api/v1/auth/change-email",
        headers=_bearer(token),
        json={"current_password": current, "new_email": new},
    )


def test_login_ignores_email_capitalization(client, owner):
    # phone keyboards capitalize the first letter
    assert _login(client, email="Owner@Example.COM").status_code == 200


def test_change_email_returns_working_new_tokens(client, owner):
    token = _login(client).json()["access_token"]
    response = _change_email(client, token)
    assert response.status_code == 200
    body = response.json()
    me = client.get("/api/v1/auth/me", headers=_bearer(body["access_token"]))
    assert me.status_code == 200
    assert me.json()["email"] == NEW_EMAIL
    refreshed = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": body["refresh_token"]}
    )
    assert refreshed.status_code == 200


def test_new_email_logs_in_and_old_email_does_not(client, owner):
    token = _login(client).json()["access_token"]
    _change_email(client, token)
    assert _login(client, email=NEW_EMAIL).status_code == 200
    assert _login(client, email=EMAIL).status_code == 401


def test_change_email_revokes_the_old_tokens(client, owner):
    tokens = _login(client).json()
    _change_email(client, tokens["access_token"])
    me = client.get("/api/v1/auth/me", headers=_bearer(tokens["access_token"]))
    assert me.status_code == 401
    refresh = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh.status_code == 401


def test_change_email_is_stored_lowercase(client, owner, db_session):
    token = _login(client).json()["access_token"]
    _change_email(client, token, new="New.Owner@Example.COM")
    db_session.refresh(owner)
    assert owner.email == NEW_EMAIL


def test_change_email_with_wrong_password_is_400(client, owner):
    token = _login(client).json()["access_token"]
    # 400, not 401: the web app treats 401 as "session expired"
    assert _change_email(client, token, current="not-the-password").status_code == 400


def test_wrong_password_changes_nothing(client, owner):
    token = _login(client).json()["access_token"]
    _change_email(client, token, current="not-the-password")
    assert _login(client, email=EMAIL).status_code == 200
    assert client.get("/api/v1/auth/me", headers=_bearer(token)).status_code == 200


def test_change_email_rejects_an_invalid_address(client, owner):
    token = _login(client).json()["access_token"]
    assert _change_email(client, token, new="not-an-email").status_code == 422


def test_change_email_rejects_an_address_another_account_uses(
    client, owner, db_session
):
    db_session.add(
        User(email="other@example.com", password_hash=PASSWORD_HASH, name="Other")
    )
    db_session.commit()
    token = _login(client).json()["access_token"]
    assert _change_email(client, token, new="Other@Example.com").status_code == 409


def test_change_email_to_the_current_address_is_400(client, owner):
    token = _login(client).json()["access_token"]
    assert _change_email(client, token, new=EMAIL).status_code == 400


def test_change_email_requires_auth(client, owner):
    response = client.post(
        "/api/v1/auth/change-email",
        json={"current_password": PASSWORD, "new_email": NEW_EMAIL},
    )
    assert response.status_code == 401


def test_change_email_rejects_a_refresh_token(client, owner):
    refresh = create_refresh_token(owner.id, owner.token_version)
    assert _change_email(client, refresh).status_code == 401


def test_change_email_is_rate_limited(client, owner):
    token = _login(client).json()["access_token"]
    for _ in range(5):
        assert (
            _change_email(client, token, current="not-the-password").status_code == 400
        )
    assert _change_email(client, token, current="not-the-password").status_code == 429
