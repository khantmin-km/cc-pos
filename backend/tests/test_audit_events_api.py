# backend/tests/test_audit_events_api.py
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
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


def test_audit_event_recorded_for_start_service(
    client: TestClient,
    db_session: Session,
    waiter_auth_header: dict[str, str],
    admin_auth_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "AUDIT_T1")
    start = client.post(f"/tables/{table.id}/start-service", headers=waiter_auth_header)
    group_id = start.json()["id"]

    response = client.get(
        "/audit-events?event_type=TABLE_START_SERVICE",
        headers=admin_auth_header,
    )

    assert response.status_code == 200
    payload = response.json()
    assert any(event["entity_id"] == group_id for event in payload)
    event = next(event for event in payload if event["entity_id"] == group_id)
    assert event["entity_type"] == "TABLE_GROUP"
    assert event["actor_role"] == "WAITER"
    assert event["metadata"]["physical_table_id"] == str(table.id)


def test_audit_event_recorded_for_void(
    client: TestClient,
    db_session: Session,
    waiter_auth_header: dict[str, str],
    admin_auth_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "AUDIT_T2")
    client.post(f"/tables/{table.id}/start-service", headers=waiter_auth_header)

    menu_item = client.post(
        "/menu-items",
        json={"name": "Soup", "price": "7.50", "category": "Food"},
        headers=admin_auth_header,
    ).json()

    order = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "audit-order-1",
            "items": [{"menu_item_id": menu_item["id"], "quantity": 1}],
        },
        headers=waiter_auth_header,
    ).json()
    order_item_id = order["order_item_ids"][0]

    void_resp = client.post(f"/order-items/{order_item_id}/void", headers=admin_auth_header)
    assert void_resp.status_code == 204

    response = client.get(
        f"/audit-events?event_type=ORDER_ITEM_VOIDED&entity_id={order_item_id}",
        headers=admin_auth_header,
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    event = payload[0]
    assert event["entity_id"] == order_item_id
    assert event["actor_role"] == "ADMIN"
    assert event["metadata"]["menu_item_name"] == "Soup"
