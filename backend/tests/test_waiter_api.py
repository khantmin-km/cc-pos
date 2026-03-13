# backend/tests/test_waiter_api.py
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.models.actor_session import ActorSession
from app.models.waiter import Waiter
from app.services import actor_session_service, waiter_service


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


def seed_waiter(db: Session, name: str, active: bool = True) -> Waiter:
    waiter = waiter_service.create_waiter(db, name=name)
    if not active:
        waiter = waiter_service.update_waiter(db, waiter.id, name=None, active=False)
    return waiter


def test_list_waiters_returns_active_only(client: TestClient, db_session: Session) -> None:
    active_waiter = seed_waiter(db_session, "Active Waiter")
    seed_waiter(db_session, "Inactive Waiter", active=False)

    response = client.get("/waiters")

    assert response.status_code == 200
    payload = response.json()
    ids = {row["id"] for row in payload}
    assert str(active_waiter.id) in ids
    assert all(row["active"] is True for row in payload)


def test_list_waiters_include_inactive_requires_admin(client: TestClient) -> None:
    response = client.get("/waiters?include_inactive=true")
    assert response.status_code == 401


def test_list_waiters_include_inactive_returns_all(
    client: TestClient,
    db_session: Session,
    admin_session_header: dict[str, str],
) -> None:
    active_waiter = seed_waiter(db_session, "Active Waiter 2")
    inactive_waiter = seed_waiter(db_session, "Inactive Waiter 2", active=False)

    response = client.get("/waiters?include_inactive=true", headers=admin_session_header)

    assert response.status_code == 200
    payload = response.json()
    ids = {row["id"] for row in payload}
    assert str(active_waiter.id) in ids
    assert str(inactive_waiter.id) in ids


def test_create_waiter_requires_admin_token(client: TestClient) -> None:
    response = client.post("/waiters", json={"name": "Waiter A"})
    assert response.status_code == 401


def test_create_waiter_success(
    client: TestClient,
    admin_session_header: dict[str, str],
) -> None:
    response = client.post("/waiters", json={"name": "Waiter A"}, headers=admin_session_header)

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Waiter A"
    assert payload["active"] is True


def test_update_waiter_deactivates_sessions(
    client: TestClient,
    db_session: Session,
    admin_session_header: dict[str, str],
) -> None:
    waiter = seed_waiter(db_session, f"Waiter-{uuid4()}")
    session = actor_session_service.create_waiter_session(db_session, waiter.id)

    response = client.patch(
        f"/waiters/{waiter.id}",
        json={"active": False},
        headers=admin_session_header,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["active"] is False

    ended_at = db_session.scalar(
        select(ActorSession.ended_at).where(ActorSession.id == session.id)
    )
    assert ended_at is not None
