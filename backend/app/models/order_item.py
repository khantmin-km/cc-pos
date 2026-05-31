# backend/app/models/order_item.py

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'VOIDED')", name="order_item_state_check"),
        CheckConstraint("kind IN ('MAIN', 'MODIFIER')", name="order_item_kind_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    parent_order_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=True
    )
    physical_table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("physical_tables.id"), nullable=False
    )
    menu_item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    menu_item_name_snap: Mapped[str] = mapped_column(String(200), nullable=False)
    modifier_group_name_snap: Mapped[str | None] = mapped_column(String(200), nullable=True)
    modifier_option_label_snap: Mapped[str | None] = mapped_column(String(200), nullable=True)
    unit_price_snap: Mapped[Decimal] = mapped_column(Numeric(10, 2, asdecimal=True), nullable=False)
    note_snap: Mapped[str | None] = mapped_column(String(200), nullable=True)
    kind: Mapped[str] = mapped_column(String(20), nullable=False, server_default="MAIN")
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
