# backend/app/models/audit_event.py

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ("
            "'ORDER_ITEM_VOIDED',"
            "'ORDER_ITEM_SERVED',"
            "'ORDER_ITEM_REPRINTED',"
            "'ORDER_CONFIRMED',"
            "'BILL_REQUESTED',"
            "'BILL_MARKED_PAID',"
            "'TABLE_CLOSED',"
            "'BILL_ADJUSTMENT_CREATED',"
            "'TABLE_SWITCHED',"
            "'TABLE_MERGED',"
            "'TABLE_SPLIT',"
            "'TABLE_START_SERVICE'"
            ")",
            name="audit_event_type_check",
        ),
        CheckConstraint(
            "entity_type IN ("
            "'ORDER_ITEM',"
            "'ORDER',"
            "'TABLE_GROUP',"
            "'BILL_ADJUSTMENT',"
            "'PHYSICAL_TABLE'"
            ")",
            name="audit_entity_type_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    actor_username: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
