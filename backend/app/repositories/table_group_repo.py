# backend/app/repositories/table_group_repo.py
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.models.order_item import OrderItem
from app.models.order import Order
from app.models.table_group import TableGroup, table_group_tables


def get_table_group(db: Session, table_group_id: UUID) -> TableGroup | None:
    return db.get(TableGroup, table_group_id)


def list_open_table_groups(db: Session) -> list[TableGroup]:
    stmt = (
        select(TableGroup)
        .where(TableGroup.state != "CLOSED")
        .order_by(TableGroup.opened_at.asc(), TableGroup.id.asc())
    )
    return list(db.scalars(stmt))


def create_table_group(db: Session, state: str = "OPEN") -> TableGroup:
    group = TableGroup(state=state)
    db.add(group)
    db.flush()
    return group


def update_state(db: Session, table_group_id: UUID, state: str) -> None:
    stmt = update(TableGroup).where(TableGroup.id == table_group_id).values(state=state)
    db.execute(stmt)


def list_physical_table_ids(db: Session, table_group_id: UUID) -> list[UUID]:
    stmt = select(table_group_tables.c.physical_table_id).where(
        table_group_tables.c.table_group_id == table_group_id
    )
    return [row[0] for row in db.execute(stmt).all()]


def get_open_group_id_for_table(db: Session, physical_table_id: UUID) -> UUID | None:
    stmt = (
        select(table_group_tables.c.table_group_id)
        .select_from(table_group_tables)
        .join(TableGroup, table_group_tables.c.table_group_id == TableGroup.id)
        .where(table_group_tables.c.physical_table_id == physical_table_id)
        .where(TableGroup.state == "OPEN")
    )
    return db.scalar(stmt)


def get_any_group_id_for_table(db: Session, physical_table_id: UUID) -> UUID | None:
    stmt = (
        select(table_group_tables.c.table_group_id)
        .select_from(table_group_tables)
        .where(table_group_tables.c.physical_table_id == physical_table_id)
    )
    return db.scalar(stmt)


def delete_group_tables(db: Session, table_group_id: UUID, table_ids: list[UUID]) -> None:
    if not table_ids:
        return
    stmt = (
        delete(table_group_tables)
        .where(table_group_tables.c.table_group_id == table_group_id)
        .where(table_group_tables.c.physical_table_id.in_(table_ids))
    )
    db.execute(stmt)


def move_tables(db: Session, source_group_id: UUID, target_group_id: UUID) -> None:
    stmt = (
        update(table_group_tables)
        .where(table_group_tables.c.table_group_id == source_group_id)
        .values(table_group_id=target_group_id)
    )
    db.execute(stmt)


def count_order_items(db: Session, table_group_id: UUID) -> int:
    stmt = (
        select(func.count(OrderItem.id))
        .select_from(OrderItem)
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.table_group_id == table_group_id)
    )
    return int(db.scalar(stmt) or 0)
