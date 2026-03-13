# backend/tests/test_order_api.py
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.physical_table import PhysicalTable


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


def seed_table(db: Session, table_code: str) -> PhysicalTable:
    table = PhysicalTable(id=uuid4(), table_code=table_code)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def seed_menu_item(db: Session, name: str, price: str, status: str = "AVAILABLE") -> MenuItem:
    item = MenuItem(id=uuid4(), name=name, price=Decimal(price), status=status)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def assert_confirm_response(payload: dict) -> None:
    assert set(payload.keys()) == {"order_id", "table_group_id", "order_item_ids"}
    UUID(payload["order_id"])
    UUID(payload["table_group_id"])
    assert isinstance(payload["order_item_ids"], list)
    for item_id in payload["order_item_ids"]:
        UUID(item_id)


def test_confirm_order_api_success(
    client: TestClient,
    db_session: Session,
    waiter_session_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "OA1")
    client.post(f"/tables/{table.id}/start-service", headers=waiter_session_header)
    item_a = seed_menu_item(db_session, "Noodle", "11.00")
    item_b = seed_menu_item(db_session, "Tea", "2.50")
    note = "No onions"

    response = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "api-order-1",
            "items": [
                {"menu_item_id": str(item_a.id), "quantity": 2, "note": note},
                {"menu_item_id": str(item_b.id), "quantity": 1},
            ],
        },
        headers=waiter_session_header,
    )

    assert response.status_code == 200
    payload = response.json()
    assert_confirm_response(payload)
    assert len(payload["order_item_ids"]) == 3

    order_id = UUID(payload["order_id"])
    note_count = db_session.scalar(
        select(func.count(OrderItem.id))
        .where(OrderItem.order_id == order_id)
        .where(OrderItem.note_snap == note)
    )
    assert int(note_count or 0) == 2


def test_confirm_order_api_rejects_free_table(
    client: TestClient,
    db_session: Session,
    waiter_session_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "OA1")
    item = seed_menu_item(db_session, "Noodle", "11.00")

    response = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "api-order-2",
            "items": [{"menu_item_id": str(item.id), "quantity": 1}],
        },
        headers=waiter_session_header,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot confirm order for FREE PhysicalTable"


def test_confirm_order_api_rejects_non_open_group(
    client: TestClient,
    db_session: Session,
    waiter_session_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "OA1")
    started = client.post(f"/tables/{table.id}/start-service", headers=waiter_session_header)
    group_id = started.json()["id"]
    client.post(f"/table-groups/{group_id}/request-bill", headers=waiter_session_header)
    item = seed_menu_item(db_session, "Noodle", "11.00")

    response = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "api-order-3",
            "items": [{"menu_item_id": str(item.id), "quantity": 1}],
        },
        headers=waiter_session_header,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "TableGroup must be OPEN to confirm order"


def test_confirm_order_api_rejects_nonexistent_menu_item(
    client: TestClient,
    db_session: Session,
    waiter_session_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "OA1")
    client.post(f"/tables/{table.id}/start-service", headers=waiter_session_header)

    response = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "api-order-4",
            "items": [{"menu_item_id": str(uuid4()), "quantity": 1}],
        },
        headers=waiter_session_header,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "One or more MenuItems do not exist"


def test_confirm_order_api_rejects_unavailable_menu_item(
    client: TestClient,
    db_session: Session,
    waiter_session_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "OA1")
    client.post(f"/tables/{table.id}/start-service", headers=waiter_session_header)
    item = seed_menu_item(db_session, "Noodle", "11.00", status="UNAVAILABLE")

    response = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "api-order-5",
            "items": [{"menu_item_id": str(item.id), "quantity": 1}],
        },
        headers=waiter_session_header,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "One or more MenuItems are not AVAILABLE"


def test_confirm_order_api_idempotency_returns_same_order(
    client: TestClient,
    db_session: Session,
    waiter_session_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "OA1")
    client.post(f"/tables/{table.id}/start-service", headers=waiter_session_header)
    item = seed_menu_item(db_session, "Noodle", "11.00")

    request_payload = {
        "idempotency_key": "api-order-same-key",
        "items": [{"menu_item_id": str(item.id), "quantity": 2}],
    }
    first = client.post(
        f"/tables/{table.id}/orders/confirm",
        json=request_payload,
        headers=waiter_session_header,
    )
    second = client.post(
        f"/tables/{table.id}/orders/confirm",
        json=request_payload,
        headers=waiter_session_header,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()

    order_count = db_session.scalar(
        select(func.count(Order.id)).where(Order.idempotency_key == "api-order-same-key")
    )
    order_id = UUID(first.json()["order_id"])
    item_count = db_session.scalar(select(func.count(OrderItem.id)).where(OrderItem.order_id == order_id))
    assert int(order_count or 0) == 1
    assert int(item_count or 0) == 2


def test_confirm_order_api_validation_errors(
    client: TestClient,
    db_session: Session,
    waiter_session_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "OA1")
    long_note = "x" * 201

    missing_key = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={"items": [{"menu_item_id": str(uuid4()), "quantity": 1}]},
        headers=waiter_session_header,
    )
    empty_items = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={"idempotency_key": "api-order-6", "items": []},
        headers=waiter_session_header,
    )
    invalid_quantity = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "api-order-7",
            "items": [{"menu_item_id": str(uuid4()), "quantity": 0}],
        },
        headers=waiter_session_header,
    )
    invalid_note = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "api-order-8",
            "items": [{"menu_item_id": str(uuid4()), "quantity": 1, "note": long_note}],
        },
        headers=waiter_session_header,
    )

    assert missing_key.status_code == 422
    assert empty_items.status_code == 422
    assert invalid_quantity.status_code == 422
    assert invalid_note.status_code == 422
