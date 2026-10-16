import time

import pytest

from app.core.rate_limit import FailureLimiter, RateLimitError, login_failures
from app.core.security import hash_password
from app.db.base import User

EMAIL = "owner@example.com"
PASSWORD = "correct-horse-battery"
WRONG = "not-the-password"
# bcrypt is deliberately slow, so hash once for the whole file
PASSWORD_HASH = hash_password(PASSWORD)
LIMIT = login_failures.max_failures


@pytest.fixture()
def owner(db_session):
    user = User(email=EMAIL, password_hash=PASSWORD_HASH, name="Owner")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _ip(n):
    # A different address for every request, so the per-IP limit never interferes.
    return f"10.1.{n // 250}.{n % 250 + 1}"


def _login(client, n, email=EMAIL, password=PASSWORD):
    return client.post(
        "/api/v1/auth/login",
        headers={"cf-connecting-ip": _ip(n)},
        json={"email": email, "password": password},
    )


def _fail_many(client, count, start=0, email=EMAIL):
    for i in range(count):
        assert _login(client, start + i, email=email, password=WRONG).status_code == 401


def test_a_few_failures_do_not_lock_the_account(client, owner):
    _fail_many(client, 5)
    assert _login(client, 100).status_code == 200


def test_account_locks_after_too_many_failures_from_many_addresses(client, owner):
    _fail_many(client, LIMIT)
    response = _login(client, 100, password=WRONG)
    assert response.status_code == 429
    assert "retry-after" in response.headers


def test_correct_password_is_refused_while_locked(client, owner):
    # The unavoidable cost of any lockout. Documented here on purpose.
    _fail_many(client, LIMIT)
    assert _login(client, 100).status_code == 429


def test_lockout_ignores_case_and_only_affects_that_email(client, owner, db_session):
    db_session.add(
        User(email="other@example.com", password_hash=PASSWORD_HASH, name="Other")
    )
    db_session.commit()
    _fail_many(client, LIMIT)
    assert _login(client, 100, email="OWNER@Example.com").status_code == 429
    assert _login(client, 101, email="other@example.com").status_code == 200


def test_unknown_emails_lock_too(client, owner):
    # Otherwise the lockout would reveal which addresses have accounts.
    _fail_many(client, LIMIT, email="nobody@example.com")
    response = _login(client, 100, email="nobody@example.com", password=WRONG)
    assert response.status_code == 429


def test_success_clears_the_failure_count(client, owner):
    _fail_many(client, LIMIT - 1)
    assert _login(client, 100).status_code == 200
    # Without clearing, these would add up to more than LIMIT and lock the account.
    _fail_many(client, LIMIT - 1, start=200)
    assert _login(client, 300).status_code == 200


def test_login_rejects_an_absurdly_long_email(client, owner):
    # Each distinct email becomes a key in memory, so its length must be capped.
    response = _login(client, 0, email="a" * 300 + "@example.com")
    assert response.status_code == 422


def test_failure_limiter_unlocks_when_the_window_passes():
    limiter = FailureLimiter(max_failures=2, window_seconds=0.2)
    limiter.record_failure("a")
    limiter.record_failure("a")
    with pytest.raises(RateLimitError):
        limiter.check("a")
    time.sleep(0.3)
    limiter.check("a")  # raises nothing: the window has passed
