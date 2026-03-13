# backend/tests/conftest.py
from collections.abc import Generator
import os

import pytest
from sqlalchemy import create_engine
from uuid import uuid4
from sqlalchemy.orm import Session, sessionmaker

os.environ.setdefault("ADMIN_TOKEN", "test-admin-token")

from app.db.base import Base
from app import models  # noqa: F401
from app.services import actor_session_service, waiter_service


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
def waiter_session_header(db_session: Session) -> dict[str, str]:
    waiter = waiter_service.create_waiter(db_session, name=f"Waiter-{uuid4()}")
    session = actor_session_service.create_waiter_session(db_session, waiter.id)
    return {"X-Actor-Session": str(session.id)}


@pytest.fixture()
def admin_session_header(db_session: Session) -> dict[str, str]:
    session = actor_session_service.create_admin_session(db_session, actor_name="admin")
    return {"X-Actor-Session": str(session.id), "X-Admin-Token": os.environ["ADMIN_TOKEN"]}
