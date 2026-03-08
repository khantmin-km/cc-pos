# backend/app/models/order_item_serving.py

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrderItemServing(Base):
    __tablename__ = "order_item_serving"

    order_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("order_items.id"), primary_key=True
    )
    served_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
