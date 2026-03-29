# backend/app/repositories/physical_table_repo.py
from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.models.physical_table import PhysicalTable
from app.models.table_group import TableGroup, table_group_tables


def list_tables_with_group(db: Session) -> list[tuple[PhysicalTable, UUID | None]]:
    stmt = (
        select(PhysicalTable, table_group_tables.c.table_group_id)
        .select_from(PhysicalTable)
        .outerjoin(table_group_tables, PhysicalTable.id == table_group_tables.c.physical_table_id)
        .order_by(PhysicalTable.table_code)
    )
    return db.execute(stmt).all()


def list_tables_overview(db: Session) -> list[tuple[PhysicalTable, UUID | None, str | None]]:
    stmt = (
        select(PhysicalTable, table_group_tables.c.table_group_id, TableGroup.state)
        .select_from(PhysicalTable)
        .outerjoin(table_group_tables, PhysicalTable.id == table_group_tables.c.physical_table_id)
        .outerjoin(TableGroup, table_group_tables.c.table_group_id == TableGroup.id)
        .order_by(PhysicalTable.table_code)
    )
    return db.execute(stmt).all()


def get_table(db: Session, table_id: UUID) -> PhysicalTable | None:
    return db.get(PhysicalTable, table_id)


def lock_tables(db: Session, table_ids: list[UUID]) -> list[PhysicalTable]:
    if not table_ids:
        return []
    stmt = select(PhysicalTable).where(PhysicalTable.id.in_(table_ids)).with_for_update()
    return list(db.scalars(stmt))


def attach_table(db: Session, table_group_id: UUID, physical_table_id: UUID) -> None:
    stmt = insert(table_group_tables).values(
        table_group_id=table_group_id,
        physical_table_id=physical_table_id,
    )
    db.execute(stmt)


def detach_table(db: Session, table_group_id: UUID, physical_table_id: UUID) -> None:
    stmt = (
        delete(table_group_tables)
        .where(table_group_tables.c.table_group_id == table_group_id)
        .where(table_group_tables.c.physical_table_id == physical_table_id)
    )
    db.execute(stmt)
