# backend/app/services/order_item_service.py
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.printing import KitchenTicketItem, print_kitchen_ticket
from app.repositories import order_item_repo
from app.services.errors import ConflictError, InvalidStateError, NotFoundError
from app.services.transaction import transactional


OPEN = "OPEN"
ACTIVE = "ACTIVE"
VOIDED = "VOIDED"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def void_order_item(db: Session, order_item_id: UUID) -> None:
    with transactional(db):
        context = order_item_repo.get_order_item_operation_context(db, order_item_id, for_update=True)
        if not context:
            raise NotFoundError("OrderItem not found")

        status, group_state, served_at = context
        if group_state != OPEN:
            raise InvalidStateError("TableGroup must be OPEN to void OrderItem")
        if served_at is not None:
            raise ConflictError("Cannot void a served OrderItem")
        if status == VOIDED:
            return
        if status != ACTIVE:
            raise ConflictError("Only ACTIVE OrderItems can be voided")

        order_item_repo.mark_order_item_voided_if_active(db, order_item_id, voided_at=_now_utc())


def mark_order_item_served(db: Session, order_item_id: UUID) -> None:
    with transactional(db):
        context = order_item_repo.get_order_item_operation_context(db, order_item_id, for_update=True)
        if not context:
            raise NotFoundError("OrderItem not found")

        status, group_state, served_at = context
        if group_state != OPEN:
            raise InvalidStateError("TableGroup must be OPEN to mark OrderItem as served")
        if status != ACTIVE:
            raise ConflictError("Cannot mark VOIDED OrderItem as served")
        if served_at is not None:
            return

        order_item_repo.mark_order_item_served_once(db, order_item_id, served_at=_now_utc())


def reprint_order_item(db: Session, order_item_id: UUID) -> None:
    with transactional(db):
        context = order_item_repo.get_order_item_operation_context(db, order_item_id, for_update=True)
        if not context:
            raise NotFoundError("OrderItem not found")

        status, _, _ = context
        if status != ACTIVE:
            raise ConflictError("Only ACTIVE OrderItems can be reprinted")

        payload = order_item_repo.get_order_item_print_payload(db, order_item_id)
        if not payload:
            raise NotFoundError("OrderItem not found")
        menu_item_name, note, table_code = payload
        if print_kitchen_ticket(
            [
                KitchenTicketItem(
                    order_item_id=order_item_id,
                    table_code=table_code,
                    menu_item_name=menu_item_name,
                    note=note,
                )
            ]
        ):
            order_item_repo.create_duplicate_print_event(db, order_item_id, printed_at=_now_utc())
        else:
            raise ConflictError("Print failed")
