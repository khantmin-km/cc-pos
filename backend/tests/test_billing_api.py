# backend/tests/test_billing_api.py
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.physical_table import PhysicalTable
from app.services import table_group_service


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


def seed_order_item(db: Session, table_group_id, physical_table_id, price: str) -> OrderItem:
    order = Order(table_group_id=table_group_id, idempotency_key=str(uuid4()), state="CONFIRMED")
    db.add(order)
    db.flush()
    item = OrderItem(
        order_id=order.id,
        physical_table_id=physical_table_id,
        menu_item_id=None,
        menu_item_name_snap="Bill API Item",
        unit_price_snap=Decimal(price),
        status="ACTIVE",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def test_get_bill_returns_breakdown(
    client: TestClient,
    db_session: Session,
    admin_auth_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "BA1")
    group_id = table_group_service.start_service(db_session, table.id)
    seed_order_item(db_session, group_id, table.id, "10.00")

    response = client.get(
        f"/table-groups/{group_id}/bill",
        headers=admin_auth_header,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["table_group_state"] == "OPEN"
    assert payload["items_total"] == "10.00"
    assert payload["adjustments_total"] == "0.00"
    assert payload["subtotal"] == "10.00"
    assert payload["tax_total"] == "0.70"
    assert payload["final_total"] == "10.70"


def test_post_bill_adjustment_requires_bill_requested(
    client: TestClient,
    db_session: Session,
    admin_auth_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "BA2")
    group_id = table_group_service.start_service(db_session, table.id)

    response = client.post(
        f"/table-groups/{group_id}/bill-adjustments",
        json={
            "amount": "1.00",
            "description": "Manual charge",
            "created_by": "staff_123",
        },
        headers=admin_auth_header,
    )

    assert response.status_code == 400


def test_post_bill_adjustment_rejects_negative_without_reason(
    client: TestClient,
    db_session: Session,
    admin_auth_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "BA3")
    group_id = table_group_service.start_service(db_session, table.id)
    table_group_service.request_bill(db_session, group_id)

    response = client.post(
        f"/table-groups/{group_id}/bill-adjustments",
        json={
            "amount": "-1.00",
            "description": "Discount",
            "created_by": "staff_123",
        },
        headers=admin_auth_header,
    )

    assert response.status_code == 422


def test_post_bill_adjustment_rejects_negative_subtotal(
    client: TestClient,
    db_session: Session,
    admin_auth_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "BA4")
    group_id = table_group_service.start_service(db_session, table.id)
    seed_order_item(db_session, group_id, table.id, "5.00")
    table_group_service.request_bill(db_session, group_id)

    response = client.post(
        f"/table-groups/{group_id}/bill-adjustments",
        json={
            "amount": "-6.00",
            "description": "Waiver",
            "reason": "Mistake",
            "created_by": "staff_123",
        },
        headers=admin_auth_header,
    )

    assert response.status_code == 409


def test_get_bill_requires_admin_auth(client: TestClient, db_session: Session) -> None:
    table = seed_table(db_session, "BA5")
    group_id = table_group_service.start_service(db_session, table.id)
    seed_order_item(db_session, group_id, table.id, "10.00")

    response = client.get(f"/table-groups/{group_id}/bill")

    assert response.status_code == 401
