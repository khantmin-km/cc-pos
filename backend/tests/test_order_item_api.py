# backend/tests/test_order_item_api.py
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_item_print_event import OrderItemPrintEvent
from app.models.order_item_serving import OrderItemServing
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


def seed_active_order_item(
    db: Session,
    *,
    table_code: str = "OIA_T1",
) -> tuple[str, str]:
    table = PhysicalTable(id=uuid4(), table_code=table_code)
    db.add(table)
    db.commit()
    db.refresh(table)

    group_id = table_group_service.start_service(db, table.id)
    order = Order(table_group_id=group_id, idempotency_key=str(uuid4()), state="CONFIRMED")
    db.add(order)
    db.flush()

    item = OrderItem(
        order_id=order.id,
        physical_table_id=table.id,
        menu_item_id=None,
        menu_item_name_snap="Tea",
        unit_price_snap=Decimal("2.50"),
        status="ACTIVE",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return str(group_id), str(item.id)


def test_void_order_item_api_success_and_retry(client: TestClient, db_session: Session) -> None:
    _, order_item_id = seed_active_order_item(db_session)

    first = client.post(f"/order-items/{order_item_id}/void")
    second = client.post(f"/order-items/{order_item_id}/void")

    assert first.status_code == 204
    assert second.status_code == 204
    item = db_session.get(OrderItem, UUID(order_item_id))
    assert item is not None
    assert item.status == "VOIDED"


def test_void_order_item_api_rejects_served(client: TestClient, db_session: Session) -> None:
    _, order_item_id = seed_active_order_item(db_session)
    served = client.post(f"/order-items/{order_item_id}/mark-served")
    assert served.status_code == 204

    response = client.post(f"/order-items/{order_item_id}/void")
    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot void a served OrderItem"


def test_mark_served_api_success_and_retry(client: TestClient, db_session: Session) -> None:
    _, order_item_id = seed_active_order_item(db_session)

    first = client.post(f"/order-items/{order_item_id}/mark-served")
    second = client.post(f"/order-items/{order_item_id}/mark-served")

    assert first.status_code == 204
    assert second.status_code == 204
    serving_count = db_session.scalar(
        select(func.count(OrderItemServing.order_item_id)).where(
            OrderItemServing.order_item_id == UUID(order_item_id)
        )
    )
    assert int(serving_count or 0) == 1


def test_mark_served_api_rejects_voided(client: TestClient, db_session: Session) -> None:
    _, order_item_id = seed_active_order_item(db_session)
    client.post(f"/order-items/{order_item_id}/void")

    response = client.post(f"/order-items/{order_item_id}/mark-served")
    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot mark VOIDED OrderItem as served"


def test_mark_served_api_rejects_non_open_group(client: TestClient, db_session: Session) -> None:
    group_id, order_item_id = seed_active_order_item(db_session)
    client.post(f"/table-groups/{group_id}/request-bill")

    response = client.post(f"/order-items/{order_item_id}/mark-served")
    assert response.status_code == 400
    assert response.json()["detail"] == "TableGroup must be OPEN to mark OrderItem as served"


def test_reprint_api_success(client: TestClient, db_session: Session) -> None:
    _, order_item_id = seed_active_order_item(db_session)

    response = client.post(f"/order-items/{order_item_id}/reprint")
    assert response.status_code == 204
    duplicate_count = db_session.scalar(
        select(func.count(OrderItemPrintEvent.order_item_id))
        .where(OrderItemPrintEvent.order_item_id == UUID(order_item_id))
        .where(OrderItemPrintEvent.print_type == "DUPLICATE")
    )
    assert int(duplicate_count or 0) == 1


def test_reprint_api_rejects_voided(client: TestClient, db_session: Session) -> None:
    _, order_item_id = seed_active_order_item(db_session)
    client.post(f"/order-items/{order_item_id}/void")

    response = client.post(f"/order-items/{order_item_id}/reprint")
    assert response.status_code == 409
    assert response.json()["detail"] == "Only ACTIVE OrderItems can be reprinted"


def test_order_item_api_not_found(client: TestClient) -> None:
    missing = str(uuid4())

    void_resp = client.post(f"/order-items/{missing}/void")
    served_resp = client.post(f"/order-items/{missing}/mark-served")
    reprint_resp = client.post(f"/order-items/{missing}/reprint")

    assert void_resp.status_code == 404
    assert served_resp.status_code == 404
    assert reprint_resp.status_code == 404
