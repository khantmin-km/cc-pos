# backend/app/repositories/order_repo.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_item_print_event import OrderItemPrintEvent


def get_order_by_idempotency_key(db: Session, idempotency_key: str) -> Order | None:
    stmt = select(Order).where(Order.idempotency_key == idempotency_key)
    return db.scalar(stmt)


def create_order(db: Session, table_group_id: UUID, idempotency_key: str, state: str) -> Order:
    order = Order(table_group_id=table_group_id, idempotency_key=idempotency_key, state=state)
    db.add(order)
    db.flush()
    return order


def create_order_item(
    db: Session,
    order_id: UUID,
    physical_table_id: UUID,
    menu_item_id: UUID,
    menu_item_name_snap: str,
    unit_price_snap: Decimal,
    note_snap: str | None,
    status: str,
) -> OrderItem:
    item = OrderItem(
        order_id=order_id,
        physical_table_id=physical_table_id,
        menu_item_id=menu_item_id,
        menu_item_name_snap=menu_item_name_snap,
        unit_price_snap=unit_price_snap,
        note_snap=note_snap,
        status=status,
    )
    db.add(item)
    db.flush()
    return item


def list_order_item_ids(db: Session, order_id: UUID) -> list[UUID]:
    stmt = select(OrderItem.id).where(OrderItem.order_id == order_id).order_by(OrderItem.created_at, OrderItem.id)
    return [row[0] for row in db.execute(stmt).all()]


def create_original_print_events(
    db: Session,
    order_item_ids: list[UUID],
    printed_at: datetime,
    printed_by: str = "system",
) -> None:
    for item_id in order_item_ids:
        db.add(
            OrderItemPrintEvent(
                order_item_id=item_id,
                printed_at=printed_at,
                printed_by=printed_by,
                print_type="ORIGINAL",
            )
        )
