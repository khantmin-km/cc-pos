# backend/app/models/bill_print_event.py
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BillPrintEvent(Base):
    __tablename__ = "bill_print_events"

    table_group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("table_groups.id"), primary_key=True
    )
    printed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    printed_by: Mapped[str] = mapped_column(String(50), nullable=False)
