# backend/app/services/billing_service.py
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import billing_repo, table_group_repo
from app.services import audit_service
from app.services.errors import ConflictError, InvalidStateError, NotFoundError
from app.services.transaction import transactional


BILL_REQUESTED = "BILL_REQUESTED"

TAX_RATE = Decimal("0.07")
CENT = Decimal("0.01")


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def get_bill_breakdown(db: Session, table_group_id: UUID) -> dict:
    group = table_group_repo.get_table_group(db, table_group_id)
    if not group:
        raise NotFoundError("TableGroup not found")

    items_total = billing_repo.get_items_total(db, table_group_id)
    adjustments_total = billing_repo.get_adjustments_total(db, table_group_id)
    subtotal = items_total + adjustments_total
    tax_total = _round_money(subtotal * TAX_RATE)
    final_total = subtotal + tax_total

    return {
        "table_group_id": group.id,
        "table_group_state": group.state,
        "items_total": _round_money(items_total),
        "adjustments_total": _round_money(adjustments_total),
        "subtotal": _round_money(subtotal),
        "tax_total": tax_total,
        "final_total": _round_money(final_total),
    }


def create_bill_adjustment(
    db: Session,
    table_group_id: UUID,
    *,
    amount: Decimal,
    description: str,
    reason: str | None,
    actor,
    reference_order_item_id: UUID | None = None,
    category: str | None = None,
) -> object:
    with transactional(db):
        group = table_group_repo.get_table_group(db, table_group_id)
        if not group:
            raise NotFoundError("TableGroup not found")
        if group.state != BILL_REQUESTED:
            raise InvalidStateError("TableGroup must be BILL_REQUESTED for bill adjustments")
        if amount < 0 and not reason:
            raise ConflictError("Negative adjustments require a reason")

        items_total = billing_repo.get_items_total(db, table_group_id)
        adjustments_total = billing_repo.get_adjustments_total(db, table_group_id)
        proposed_subtotal = items_total + adjustments_total + amount
        if proposed_subtotal < 0:
            raise ConflictError("Adjustment would make bill subtotal negative")

        adjustment = billing_repo.create_bill_adjustment(
            db,
            table_group_id=table_group_id,
            amount=amount,
            description=description,
            reason=reason,
            created_by=actor.username,
            reference_order_item_id=reference_order_item_id,
            category=category,
        )
        audit_service.record_event(
            db,
            actor=actor,
            event_type=audit_service.EVENT_BILL_ADJUSTMENT_CREATED,
            entity_type=audit_service.ENTITY_BILL_ADJUSTMENT,
            entity_id=adjustment.id,
            metadata={
                "table_group_id": str(table_group_id),
                "amount": str(amount),
                "description": description,
                "reason": reason,
                "category": category,
            },
        )
        return adjustment
