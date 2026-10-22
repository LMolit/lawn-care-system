import os

import pytest

os.environ["DATABASE_URL"] = (
    "postgresql://lawncare:localdevpassword@localhost:5432/lawn_care_test"
)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token
from app.db.base import User
from app.dependencies import get_db
from app.main import app

engine = create_engine(
    "postgresql://lawncare:localdevpassword@localhost:5432/lawn_care_test"
)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.fixture()
def db_session():
    connection = engine.connect()
    # One outer transaction per test, always rolled back at the end, so no test
    # leaves anything behind.
    transaction = connection.begin()
    # create_savepoint: the session's own commit() and rollback() work on a SAVEPOINT
    # inside that outer transaction. A rollback in the app code undoes only the app's
    # unfinished work, exactly like production, and never the test's own setup.
    session = TestSessionLocal(
        bind=connection, join_transaction_mode="create_savepoint"
    )

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db_session):
    user = User(email="test@lawncare.local", password_hash="unused", name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def authed_client(client, test_user):
    token = create_access_token(test_user.id, test_user.token_version)
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture(autouse=True)
def reset_rate_limits():
    from app.core.rate_limit import reset_all

    reset_all()
