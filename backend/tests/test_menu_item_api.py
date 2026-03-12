# backend/tests/test_menu_item_api.py
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.models.menu_item import MenuItem
from app.services import menu_item_service


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


def seed_menu_item(db: Session, name: str, price: str, status: str = "AVAILABLE") -> MenuItem:
    item = MenuItem(id=uuid4(), name=name, price=Decimal(price), status=status)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def assert_menu_item_response(payload: dict) -> None:
    assert set(payload.keys()) == {"id", "name", "price", "status", "image_url", "created_at"}
    UUID(payload["id"])
    assert isinstance(payload["name"], str)
    assert payload["status"] in {"AVAILABLE", "UNAVAILABLE", "RETIRED"}
    assert payload["created_at"] is not None


def test_create_menu_item_api(client: TestClient) -> None:
    response = client.post("/menu-items", json={"name": "Soup", "price": "7.50"})
    assert response.status_code == 201
    payload = response.json()
    assert_menu_item_response(payload)
    assert payload["name"] == "Soup"
    assert payload["status"] == "AVAILABLE"


def test_list_menu_items_api(client: TestClient, db_session: Session) -> None:
    item = seed_menu_item(db_session, "Tea", "2.00")

    response = client.get("/menu-items")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert any(row["id"] == str(item.id) for row in payload)


def test_update_menu_item_api(client: TestClient, db_session: Session) -> None:
    item = seed_menu_item(db_session, "Soup", "7.50")

    response = client.patch(
        f"/menu-items/{item.id}",
        json={"name": "Hot Soup", "price": "8.00", "status": "UNAVAILABLE"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert_menu_item_response(payload)
    assert payload["name"] == "Hot Soup"
    assert payload["price"] == "8.00"
    assert payload["status"] == "UNAVAILABLE"


def test_retire_menu_item_api(client: TestClient, db_session: Session) -> None:
    item = seed_menu_item(db_session, "Soup", "7.50")

    response = client.post(f"/menu-items/{item.id}/retire")
    assert response.status_code == 200
    payload = response.json()
    assert_menu_item_response(payload)
    assert payload["status"] == "RETIRED"


def test_retired_menu_item_cannot_be_unretired_api(client: TestClient, db_session: Session) -> None:
    item = seed_menu_item(db_session, "Soup", "7.50", status="RETIRED")

    response = client.patch(f"/menu-items/{item.id}", json={"status": "AVAILABLE"})
    assert response.status_code == 400
    assert response.json()["detail"] == "RETIRED MenuItem cannot transition to AVAILABLE or UNAVAILABLE"


def test_menu_item_api_not_found(client: TestClient) -> None:
    response = client.patch(f"/menu-items/{uuid4()}", json={"name": "X"})
    assert response.status_code == 404
    assert response.json()["detail"] == "MenuItem not found"


def test_menu_item_api_validation_errors(client: TestClient) -> None:
    bad_create = client.post("/menu-items", json={"name": "", "price": "0"})
    bad_update_empty = client.patch(f"/menu-items/{uuid4()}", json={})
    bad_update_status = client.patch(f"/menu-items/{uuid4()}", json={"status": "ARCHIVED"})

    assert bad_create.status_code == 422
    assert bad_update_empty.status_code == 422
    assert bad_update_status.status_code == 422


def test_upload_menu_item_image_api(
    client: TestClient, db_session: Session, tmp_path, monkeypatch
) -> None:
    item = seed_menu_item(db_session, "Soup", "7.50")
    menu_dir = tmp_path / "menu"
    menu_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(menu_item_service, "MENU_DIR", menu_dir)

    response = client.post(
        f"/menu-items/{item.id}/image",
        files={"file": ("soup.png", b"fake-image", "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["image_url"] == f"/static/menu/{item.id}.png"
    assert (menu_dir / f"{item.id}.png").exists()
