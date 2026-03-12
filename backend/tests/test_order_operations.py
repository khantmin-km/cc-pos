# backend/tests/test_order_operations.py
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_item_print_event import OrderItemPrintEvent
from app.models.physical_table import PhysicalTable
from app.services import order_service, table_group_service
from app.services.errors import ConflictError, InvalidStateError
from app.schemas.order import OrderConfirmItemRequest


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


def test_confirm_order_creates_order_items_and_print_events(db_session: Session) -> None:
    table = seed_table(db_session, "O1")
    group_id = table_group_service.start_service(db_session, table.id)
    item_a = seed_menu_item(db_session, "Noodle", "12.50")
    item_b = seed_menu_item(db_session, "Tea", "3.00")
    note = "No chili"

    order_id, resolved_group_id, order_item_ids = order_service.confirm_order(
        db=db_session,
        physical_table_id=table.id,
        idempotency_key="order-key-1",
        items=[
            OrderConfirmItemRequest(menu_item_id=item_a.id, quantity=2, note=note),
            OrderConfirmItemRequest(menu_item_id=item_b.id, quantity=1),
        ],
    )

    assert resolved_group_id == group_id
    assert len(order_item_ids) == 3

    order = db_session.get(Order, order_id)
    assert order is not None
    assert order.state == "CONFIRMED"
    assert order.idempotency_key == "order-key-1"

    created_count = db_session.scalar(select(func.count(OrderItem.id)).where(OrderItem.order_id == order_id))
    note_count = db_session.scalar(
        select(func.count(OrderItem.id))
        .where(OrderItem.order_id == order_id)
        .where(OrderItem.note_snap == note)
    )
    print_count = db_session.scalar(
        select(func.count(OrderItemPrintEvent.order_item_id)).where(
            OrderItemPrintEvent.order_item_id.in_(order_item_ids)
        )
    )
    assert int(created_count or 0) == 3
    assert int(note_count or 0) == 2
    assert int(print_count or 0) == 3


def test_confirm_order_rejects_free_table(db_session: Session) -> None:
    table = seed_table(db_session, "O1")
    item = seed_menu_item(db_session, "Soup", "7.00")

    with pytest.raises(ConflictError):
        order_service.confirm_order(
            db=db_session,
            physical_table_id=table.id,
            idempotency_key="order-key-2",
            items=[OrderConfirmItemRequest(menu_item_id=item.id, quantity=1)],
        )


def test_confirm_order_rejects_non_open_group(db_session: Session) -> None:
    table = seed_table(db_session, "O1")
    group_id = table_group_service.start_service(db_session, table.id)
    table_group_service.request_bill(db_session, group_id)
    item = seed_menu_item(db_session, "Soup", "7.00")

    with pytest.raises(InvalidStateError):
        order_service.confirm_order(
            db=db_session,
            physical_table_id=table.id,
            idempotency_key="order-key-3",
            items=[OrderConfirmItemRequest(menu_item_id=item.id, quantity=1)],
        )


def test_confirm_order_rejects_missing_menu_items(db_session: Session) -> None:
    table = seed_table(db_session, "O1")
    table_group_service.start_service(db_session, table.id)

    with pytest.raises(ConflictError):
        order_service.confirm_order(
            db=db_session,
            physical_table_id=table.id,
            idempotency_key="order-key-4",
            items=[OrderConfirmItemRequest(menu_item_id=uuid4(), quantity=1)],
        )


def test_confirm_order_rejects_unavailable_menu_items(db_session: Session) -> None:
    table = seed_table(db_session, "O1")
    table_group_service.start_service(db_session, table.id)
    item = seed_menu_item(db_session, "Soup", "7.00", status="UNAVAILABLE")

    with pytest.raises(ConflictError):
        order_service.confirm_order(
            db=db_session,
            physical_table_id=table.id,
            idempotency_key="order-key-5",
            items=[OrderConfirmItemRequest(menu_item_id=item.id, quantity=1)],
        )


def test_confirm_order_idempotency_returns_same_result(db_session: Session) -> None:
    table = seed_table(db_session, "O1")
    table_group_service.start_service(db_session, table.id)
    item = seed_menu_item(db_session, "Soup", "7.00")

    first = order_service.confirm_order(
        db=db_session,
        physical_table_id=table.id,
        idempotency_key="same-key",
        items=[OrderConfirmItemRequest(menu_item_id=item.id, quantity=2)],
    )
    second = order_service.confirm_order(
        db=db_session,
        physical_table_id=table.id,
        idempotency_key="same-key",
        items=[OrderConfirmItemRequest(menu_item_id=item.id, quantity=2)],
    )

    assert first == second
    order_count = db_session.scalar(select(func.count(Order.id)).where(Order.idempotency_key == "same-key"))
    assert int(order_count or 0) == 1
