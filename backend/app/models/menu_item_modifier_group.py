import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MenuItemModifierGroup(Base):
    __tablename__ = "menu_item_modifier_groups"
    __table_args__ = (
        UniqueConstraint("menu_item_id", "modifier_group_id", name="uq_menu_item_modifier_groups_pair"),
        CheckConstraint("min_select >= 0", name="menu_item_modifier_groups_min_select_check"),
        CheckConstraint("max_select >= 1", name="menu_item_modifier_groups_max_select_positive_check"),
        CheckConstraint("max_select >= min_select", name="menu_item_modifier_groups_max_ge_min_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False)
    modifier_group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("modifier_groups.id"), nullable=False
    )
    min_select: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    max_select: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
