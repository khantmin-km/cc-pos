# backend/app/models/order_item_print_event.py

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrderItemPrintEvent(Base):
    __tablename__ = "order_item_printing"
    __table_args__ = (
        CheckConstraint(
            "print_type IN ('ORIGINAL', 'DUPLICATE')",
            name="order_item_print_type_check",
        ),
    )

    order_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("order_items.id"), primary_key=True
    )
    printed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    printed_by: Mapped[str] = mapped_column(String(50), nullable=False)
    print_type: Mapped[str] = mapped_column(String(20), nullable=False)
