# backend/tests/test_actor_sessions_api.py
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.models.actor_session import ActorSession
from app.models.physical_table import PhysicalTable
from app.repositories import actor_session_repo
from app.services import waiter_service


@pytest.fixture()
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_create_waiter_session_success(client: TestClient, db_session: Session) -> None:
    waiter = waiter_service.create_waiter(db_session, name=f"Waiter-{uuid4()}")

    response = client.post(
        "/sessions",
        json={"role": "WAITER", "waiter_id": str(waiter.id)},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["role"] == "WAITER"
    assert payload["waiter_id"] == str(waiter.id)
    assert payload["actor_name"] == waiter.name


def test_create_admin_session_requires_token(client: TestClient) -> None:
    response = client.post("/sessions", json={"role": "ADMIN", "actor_name": "admin"})
    assert response.status_code == 401


def test_create_admin_session_success(client: TestClient, admin_session_header: dict[str, str]) -> None:
    response = client.post(
        "/sessions",
        json={"role": "ADMIN", "actor_name": "admin"},
        headers={"X-Admin-Token": admin_session_header["X-Admin-Token"]},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["role"] == "ADMIN"
    assert payload["actor_name"] == "admin"


def test_end_session_marks_ended_at(client: TestClient, db_session: Session) -> None:
    session = actor_session_repo.create_session(
        db_session,
        role="ADMIN",
        actor_name="admin",
        waiter_id=None,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    response = client.post(
        f"/sessions/{session.id}/end",
        headers={"X-Actor-Session": str(session.id)},
    )

    assert response.status_code == 204
    refreshed = db_session.get(ActorSession, session.id)
    assert refreshed is not None
    assert refreshed.ended_at is not None


def test_expired_session_rejected(client: TestClient, db_session: Session) -> None:
    expired_session = actor_session_repo.create_session(
        db_session,
        role="ADMIN",
        actor_name="admin",
        waiter_id=None,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    table = PhysicalTable(id=uuid4(), table_code="AS_EXP")
    db_session.add(table)
    db_session.commit()

    response = client.get(
        "/tables",
        headers={"X-Actor-Session": str(expired_session.id)},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Session expired"
