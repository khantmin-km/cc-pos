# backend/tests/test_printing_adapter.py
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.models.order_item_print_event import OrderItemPrintEvent
from app.models.physical_table import PhysicalTable
from app.services import order_service, table_group_service
from app.schemas.order import OrderConfirmItemRequest


def seed_table(db: Session, table_code: str) -> PhysicalTable:
    table = PhysicalTable(id=uuid4(), table_code=table_code)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def seed_menu_item(db: Session, name: str, price: str) -> MenuItem:
    item = MenuItem(id=uuid4(), name=name, price=Decimal(price), status="AVAILABLE")
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def test_confirm_order_skips_print_events_when_adapter_fails(db_session: Session, monkeypatch) -> None:
    table = seed_table(db_session, "P1")
    table_group_service.start_service(db_session, table.id)
    item = seed_menu_item(db_session, "Noodle", "10.00")

    monkeypatch.setattr(order_service, "print_kitchen_ticket", lambda items: False)

    order_id, _, order_item_ids = order_service.confirm_order(
        db=db_session,
        physical_table_id=table.id,
        idempotency_key="print-fail-1",
        items=[OrderConfirmItemRequest(menu_item_id=item.id, quantity=2)],
    )

    assert order_id is not None
    assert len(order_item_ids) == 2
    print_count = db_session.scalar(
        select(func.count(OrderItemPrintEvent.order_item_id)).where(
            OrderItemPrintEvent.order_item_id.in_(order_item_ids)
        )
    )
    assert int(print_count or 0) == 0
