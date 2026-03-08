"""SQLite seed helpers for local development.

Creates the schema and inserts sample data when the backend is running with
the default SQLite database. This allows the frontend to work out of the box
without manual migrations or fixtures.
"""

from __future__ import annotations

from datetime import timedelta, timezone, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.physical_table import PhysicalTable
from app.models.table_group import TableGroup
from app.repositories import physical_table_repo


SAMPLE_TABLE_CODES = [
    "T-01",
    "T-02",
    "T-03",
    "T-04",
    "T-05",
    "T-06",
]

GROUP_SEEDS = [
    ("OPEN", ["T-01", "T-02"]),
    ("OPEN", ["T-03"]),
    ("BILL_REQUESTED", ["T-04"]),
    ("PAID", ["T-05"]),
]


def ensure_sqlite_seed_data() -> None:
    """Create tables and seed sample data when using SQLite."""

    if engine.url.get_backend_name() != "sqlite":
        return

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        table_count = db.scalar(select(func.count(PhysicalTable.id))) or 0
        if table_count:
            return

        _seed_tables(db)
        _seed_groups(db)
        db.commit()


def _seed_tables(db: Session) -> None:
    for code in SAMPLE_TABLE_CODES:
        db.add(PhysicalTable(table_code=code))
    db.flush()


def _seed_groups(db: Session) -> None:
    table_lookup = {
        table.table_code: table
        for table in db.scalars(select(PhysicalTable)).all()
    }

    now = datetime.now(timezone.utc)

    for index, (state, table_codes) in enumerate(GROUP_SEEDS):
        group = TableGroup(state=state)
        db.add(group)
        db.flush()

        # Spread opened_at timestamps for nicer ordering.
        group.opened_at = now - timedelta(hours=index)
        if state == "PAID":
            group.closed_at = group.opened_at + timedelta(minutes=30)

        for code in table_codes:
            table = table_lookup.get(code)
            if table:
                physical_table_repo.attach_table(db, group.id, table.id)
