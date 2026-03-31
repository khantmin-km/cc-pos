# backend/app/repositories/order_item_repo.py
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_item_print_event import OrderItemPrintEvent
from app.models.order_item_serving import OrderItemServing
from app.models.physical_table import PhysicalTable
from app.models.table_group import TableGroup


def get_order_item_operation_context(
    db: Session, order_item_id: UUID, *, for_update: bool = False
) -> tuple[str, str, datetime | None] | None:
    served_at_subquery = (
        select(OrderItemServing.served_at)
        .where(OrderItemServing.order_item_id == OrderItem.id)
        .scalar_subquery()
    )
    stmt = (
        select(OrderItem.status, TableGroup.state, served_at_subquery)
        .select_from(OrderItem)
        .join(Order, OrderItem.order_id == Order.id)
        .join(TableGroup, Order.table_group_id == TableGroup.id)
        .where(OrderItem.id == order_item_id)
    )
    if for_update:
        stmt = stmt.with_for_update(of=OrderItem)
    row = db.execute(stmt).one_or_none()
    if not row:
        return None
    return row[0], row[1], row[2]


def mark_order_item_voided_if_active(db: Session, order_item_id: UUID, *, voided_at: datetime) -> bool:
    stmt = (
        update(OrderItem)
        .where(OrderItem.id == order_item_id)
        .where(OrderItem.status == "ACTIVE")
        .values(status="VOIDED", voided_at=voided_at)
    )
    result = db.execute(stmt)
    db.flush()
    return result.rowcount == 1


def mark_order_item_served_once(db: Session, order_item_id: UUID, *, served_at: datetime) -> bool:
    stmt = (
        insert(OrderItemServing)
        .values(order_item_id=order_item_id, served_at=served_at)
        .on_conflict_do_nothing(index_elements=[OrderItemServing.order_item_id])
    )
    result = db.execute(stmt)
    db.flush()
    return result.rowcount == 1


def create_duplicate_print_event(
    db: Session,
    order_item_id: UUID,
    *,
    printed_at: datetime,
    printed_by: str = "admin",
) -> None:
    db.add(
        OrderItemPrintEvent(
            order_item_id=order_item_id,
            printed_at=printed_at,
            printed_by=printed_by,
            print_type="DUPLICATE",
        )
    )
    db.flush()


def get_order_item_print_payload(db: Session, order_item_id: UUID) -> tuple[str, str | None, str] | None:
    stmt = (
        select(OrderItem.menu_item_name_snap, OrderItem.note_snap, PhysicalTable.table_code)
        .select_from(OrderItem)
        .join(PhysicalTable, OrderItem.physical_table_id == PhysicalTable.id)
        .where(OrderItem.id == order_item_id)
    )
    row = db.execute(stmt).one_or_none()
    if not row:
        return None
    return row[0], row[1], row[2]


def get_order_item_audit_payload(
    db: Session, order_item_id: UUID
) -> tuple[str, object, str] | None:
    stmt = (
        select(OrderItem.menu_item_name_snap, OrderItem.unit_price_snap, PhysicalTable.table_code)
        .select_from(OrderItem)
        .join(PhysicalTable, OrderItem.physical_table_id == PhysicalTable.id)
        .where(OrderItem.id == order_item_id)
    )
    row = db.execute(stmt).one_or_none()
    if not row:
        return None
    return row[0], row[1], row[2]
