# backend/app/services/order_item_service.py
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.printing import KitchenTicketItem, KitchenTicketModifierGroup, print_kitchen_ticket
from app.repositories import order_item_repo
from app.services import audit_service
from app.services.errors import ConflictError, InvalidStateError, NotFoundError
from app.services.transaction import transactional


OPEN = "OPEN"
ACTIVE = "ACTIVE"
VOIDED = "VOIDED"
MAIN = "MAIN"
MODIFIER = "MODIFIER"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def void_order_item(db: Session, order_item_id: UUID, *, actor=None) -> None:
    with transactional(db):
        context = order_item_repo.get_order_item_operation_context(db, order_item_id, for_update=True)
        if not context:
            raise NotFoundError("OrderItem not found")

        status, group_state, served_at, kind, _ = context
        if group_state != OPEN:
            raise InvalidStateError("TableGroup must be OPEN to void OrderItem")
        if kind == MODIFIER:
            raise ConflictError("Cannot void MODIFIER OrderItem directly")
        if served_at is not None:
            raise ConflictError("Cannot void a served OrderItem")
        if status == VOIDED:
            return
        if status != ACTIVE:
            raise ConflictError("Only ACTIVE OrderItems can be voided")

        voided_at = _now_utc()
        order_item_repo.mark_order_item_voided_if_active(db, order_item_id, voided_at=voided_at)
        if kind == MAIN:
            order_item_repo.mark_child_modifiers_voided_if_active(
                db,
                order_item_id,
                voided_at=voided_at,
            )
        payload = order_item_repo.get_order_item_audit_payload(db, order_item_id)
        metadata = {}
        if payload:
            name, unit_price, table_code = payload
            metadata = {
                "menu_item_name": name,
                "unit_price": str(unit_price),
                "table_code": table_code,
            }
        audit_service.record_event(
            db,
            actor=actor,
            event_type=audit_service.EVENT_ORDER_ITEM_VOIDED,
            entity_type=audit_service.ENTITY_ORDER_ITEM,
            entity_id=order_item_id,
            metadata=metadata,
        )


def mark_order_item_served(db: Session, order_item_id: UUID, *, actor=None) -> None:
    with transactional(db):
        context = order_item_repo.get_order_item_operation_context(db, order_item_id, for_update=True)
        if not context:
            raise NotFoundError("OrderItem not found")

        status, group_state, served_at, _, _ = context
        if group_state != OPEN:
            raise InvalidStateError("TableGroup must be OPEN to mark OrderItem as served")
        if status != ACTIVE:
            raise ConflictError("Cannot mark VOIDED OrderItem as served")
        if served_at is not None:
            return

        order_item_repo.mark_order_item_served_once(db, order_item_id, served_at=_now_utc())
        payload = order_item_repo.get_order_item_audit_payload(db, order_item_id)
        metadata = {}
        if payload:
            name, unit_price, table_code = payload
            metadata = {
                "menu_item_name": name,
                "unit_price": str(unit_price),
                "table_code": table_code,
            }
        audit_service.record_event(
            db,
            actor=actor,
            event_type=audit_service.EVENT_ORDER_ITEM_SERVED,
            entity_type=audit_service.ENTITY_ORDER_ITEM,
            entity_id=order_item_id,
            metadata=metadata,
        )


def reprint_order_item(db: Session, order_item_id: UUID, *, actor=None) -> None:
    with transactional(db):
        context = order_item_repo.get_order_item_operation_context(db, order_item_id, for_update=True)
        if not context:
            raise NotFoundError("OrderItem not found")

        status, _, _, _, _ = context
        if status != ACTIVE:
            raise ConflictError("Only ACTIVE OrderItems can be reprinted")

        payload = order_item_repo.get_order_item_print_payload(db, order_item_id)
        if not payload:
            raise NotFoundError("OrderItem not found")
        modifier_groups = tuple(
            KitchenTicketModifierGroup(
                group_name=group["group_name"],
                option_labels=group["option_labels"],
            )
            for group in payload["modifier_groups"]
        )
        if print_kitchen_ticket(
            [
                KitchenTicketItem(
                    order_item_id=order_item_id,
                    table_code=payload["table_code"],
                    menu_item_name=payload["menu_item_name"],
                    note=payload["note"],
                    modifier_groups=modifier_groups,
                )
            ]
        ):
            order_item_repo.create_duplicate_print_event(db, order_item_id, printed_at=_now_utc())
            payload = order_item_repo.get_order_item_audit_payload(db, order_item_id)
            metadata = {}
            if payload:
                name, unit_price, table_code = payload
                metadata = {
                    "menu_item_name": name,
                    "unit_price": str(unit_price),
                    "table_code": table_code,
                }
            audit_service.record_event(
                db,
                actor=actor,
                event_type=audit_service.EVENT_ORDER_ITEM_REPRINTED,
                entity_type=audit_service.ENTITY_ORDER_ITEM,
                entity_id=order_item_id,
                metadata=metadata,
            )
        else:
            raise ConflictError("Print failed")
