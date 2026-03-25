# backend/tests/test_auth_api.py
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.repositories import user_repo
from app.services import auth_service


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


def _seed_user(db: Session, *, role: str, active: bool = True) -> tuple[str, str]:
    username = f"user-{uuid4()}"
    pin = "1234"
    user = user_repo.create_user(
        db,
        username=username,
        pin_hash=auth_service.hash_pin(pin),
        role=role,
    )
    if not active:
        user.active = False
        db.commit()
    return username, pin


def test_login_success(client: TestClient, db_session: Session) -> None:
    username, pin = _seed_user(db_session, role=auth_service.ROLE_ADMIN)

    response = client.post("/auth/login", json={"username": username, "pin": pin})

    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {"token", "user_id", "username", "role", "expires_at"}
    UUID(payload["user_id"])
    assert payload["username"] == username
    assert payload["role"] == auth_service.ROLE_ADMIN
    assert payload["token"]


def test_login_invalid_credentials(client: TestClient, db_session: Session) -> None:
    username, _pin = _seed_user(db_session, role=auth_service.ROLE_WAITER)

    response = client.post("/auth/login", json={"username": username, "pin": "0000"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_inactive_user(client: TestClient, db_session: Session) -> None:
    username, pin = _seed_user(db_session, role=auth_service.ROLE_WAITER, active=False)

    response = client.post("/auth/login", json={"username": username, "pin": pin})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
