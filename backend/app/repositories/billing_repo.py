# backend/app/repositories/billing_repo.py
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.bill_adjustment import BillAdjustment
from app.models.order import Order
from app.models.order_item import OrderItem


def get_items_total(db: Session, table_group_id: UUID) -> Decimal:
    stmt = (
        select(func.coalesce(func.sum(OrderItem.unit_price_snap), 0))
        .select_from(OrderItem)
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.table_group_id == table_group_id)
        .where(OrderItem.status == "ACTIVE")
    )
    value = db.scalar(stmt)
    return Decimal(value or 0)


def get_adjustments_total(db: Session, table_group_id: UUID) -> Decimal:
    stmt = select(func.coalesce(func.sum(BillAdjustment.amount), 0)).where(
        BillAdjustment.table_group_id == table_group_id
    )
    value = db.scalar(stmt)
    return Decimal(value or 0)


def create_bill_adjustment(
    db: Session,
    *,
    table_group_id: UUID,
    amount: Decimal,
    description: str,
    reason: str | None,
    created_by: str,
    reference_order_item_id: UUID | None = None,
    category: str | None = None,
) -> BillAdjustment:
    adjustment = BillAdjustment(
        table_group_id=table_group_id,
        amount=amount,
        description=description,
        reason=reason,
        created_by=created_by,
        reference_order_item_id=reference_order_item_id,
        category=category,
    )
    db.add(adjustment)
    db.flush()
    return adjustment
