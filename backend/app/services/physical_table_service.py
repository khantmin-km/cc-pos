# backend/app/services/physical_table_service.py
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import physical_table_repo


def list_tables(db: Session) -> list[tuple[UUID, str, UUID | None]]:
    rows = physical_table_repo.list_tables_with_group(db)
    return [(table.id, table.table_code, group_id) for table, group_id in rows]
