import os

os.environ["DATABASE_URL"] = "postgresql://lawncare:localdevpassword@localhost:5432/lawn_care_test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.dependencies import get_db
from app.core.security import create_access_token
from app.db.base import User

engine = create_engine("postgresql://lawncare:localdevpassword@localhost:5432/lawn_care_test")
TestSessionLocal = sessionmaker(bind=engine)


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

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
    token = create_access_token(test_user.id)
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
