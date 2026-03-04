# backend/app/models/table_group.py

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


table_group_tables = Table(
    "table_group_tables",
    Base.metadata,
    mapped_column("table_group_id", UUID(as_uuid=True), ForeignKey("table_groups.id"), primary_key=True),
    mapped_column("physical_table_id", UUID(as_uuid=True), ForeignKey("physical_tables.id"), primary_key=True),
)


class TableGroup(Base):
    __tablename__ = "table_groups"
    __table_args__ = (
        CheckConstraint(
            "state IN ('OPEN', 'BILL_REQUESTED', 'PAID', 'CLOSED')",
            name="table_group_state_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state: Mapped[str] = mapped_column(String(20), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
