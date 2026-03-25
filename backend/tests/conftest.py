# backend/tests/conftest.py
from collections.abc import Generator
import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app import models  # noqa: F401
from app.repositories import user_repo
from app.services import auth_service


@pytest.fixture(scope="session")
def engine() -> Generator:
    database_url = os.environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is not set")
    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session_local = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture()
def waiter_auth_header(db_session: Session) -> dict[str, str]:
    username = f"waiter-{uuid4()}"
    pin = "1234"
    user_repo.create_user(
        db_session,
        username=username,
        pin_hash=auth_service.hash_pin(pin),
        role=auth_service.ROLE_WAITER,
    )
    _, session = auth_service.login(db_session, username=username, pin=pin)
    return {"Authorization": f"Bearer {session.token}"}


@pytest.fixture()
def admin_auth_header(db_session: Session) -> dict[str, str]:
    username = f"admin-{uuid4()}"
    pin = "9999"
    user_repo.create_user(
        db_session,
        username=username,
        pin_hash=auth_service.hash_pin(pin),
        role=auth_service.ROLE_ADMIN,
    )
    _, session = auth_service.login(db_session, username=username, pin=pin)
    return {"Authorization": f"Bearer {session.token}"}
