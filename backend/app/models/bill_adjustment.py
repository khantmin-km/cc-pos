#backend/app/models/bill_adjustment.py

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BillAdjustment(Base):
    __tablename__ = "bill_adjustments"
    __table_args__ = (
        CheckConstraint("category IN ('WAIVER', 'MANUAL')", name="bill_adj_category_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("table_groups.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2, asdecimal=True), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reference_order_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_by: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
