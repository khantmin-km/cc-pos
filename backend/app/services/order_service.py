# backend/app/services/order_service.py
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.printing import KitchenTicketItem, print_kitchen_ticket
from app.repositories import menu_item_repo, order_repo, physical_table_repo, table_group_repo
from app.schemas.order import OrderConfirmItemRequest
from app.services import audit_service
from app.services.errors import ConflictError, InvalidStateError, NotFoundError
from app.services.transaction import transactional


OPEN = "OPEN"
CONFIRMED = "CONFIRMED"
ACTIVE = "ACTIVE"
AVAILABLE = "AVAILABLE"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _load_existing_confirmation(
    db: Session, idempotency_key: str
) -> tuple[UUID, UUID, list[UUID]] | None:
    existing = order_repo.get_order_by_idempotency_key(db, idempotency_key)
    if not existing:
        return None
    item_ids = order_repo.list_order_item_ids(db, existing.id)
    return existing.id, existing.table_group_id, item_ids


def _validate_menu_items(
    db: Session, item_lines: list[OrderConfirmItemRequest]
) -> dict[UUID, tuple[str, object]]:
    requested_ids = sorted({line.menu_item_id for line in item_lines})
    menu_items = menu_item_repo.get_menu_items_for_update(db, requested_ids)
    by_id = {item.id: item for item in menu_items}

    missing_ids = [item_id for item_id in requested_ids if item_id not in by_id]
    if missing_ids:
        raise ConflictError("One or more MenuItems do not exist")

    unavailable_ids = [item.id for item in menu_items if item.status != AVAILABLE]
    if unavailable_ids:
        raise ConflictError("One or more MenuItems are not AVAILABLE")

    # Keep only snapshot fields required for OrderItem creation.
    return {item.id: (item.name, item.price) for item in menu_items}


def confirm_order(
    db: Session,
    physical_table_id: UUID,
    idempotency_key: str,
    items: list[OrderConfirmItemRequest],
    *,
    actor=None,
) -> tuple[UUID, UUID, list[UUID]]:
    existing = _load_existing_confirmation(db, idempotency_key)
    if existing:
        return existing

    try:
        with transactional(db):
            # Re-check inside the transaction to handle concurrent duplicate confirms.
            existing_in_tx = _load_existing_confirmation(db, idempotency_key)
            if existing_in_tx:
                return existing_in_tx

            physical_table_repo.lock_tables(db, [physical_table_id])
            table = physical_table_repo.get_table(db, physical_table_id)
            if not table:
                raise NotFoundError("PhysicalTable not found")

            table_group_id = table_group_repo.get_any_group_id_for_table(db, physical_table_id)
            if table_group_id is None:
                raise ConflictError("Cannot confirm order for FREE PhysicalTable")

            group = table_group_repo.get_table_group(db, table_group_id)
            if not group:
                raise NotFoundError("TableGroup not found")
            if group.state != OPEN:
                raise InvalidStateError("TableGroup must be OPEN to confirm order")

            snapshots = _validate_menu_items(db, items)

            order = order_repo.create_order(
                db=db,
                table_group_id=table_group_id,
                idempotency_key=idempotency_key,
                state=CONFIRMED,
            )

            created_item_ids: list[UUID] = []
            ticket_items: list[KitchenTicketItem] = []
            for line in items:
                name_snap, price_snap = snapshots[line.menu_item_id]
                for _ in range(line.quantity):
                    created_item = order_repo.create_order_item(
                        db=db,
                        order_id=order.id,
                        physical_table_id=physical_table_id,
                        menu_item_id=line.menu_item_id,
                        menu_item_name_snap=name_snap,
                        unit_price_snap=price_snap,
                        note_snap=line.note,
                        status=ACTIVE,
                    )
                    created_item_ids.append(created_item.id)
                    ticket_items.append(
                        KitchenTicketItem(
                            order_item_id=created_item.id,
                            table_code=table.table_code,
                            menu_item_name=name_snap,
                            note=line.note,
                        )
                    )

            if print_kitchen_ticket(ticket_items):
                order_repo.create_original_print_events(
                    db=db,
                    order_item_ids=created_item_ids,
                    printed_at=_now_utc(),
                )

            stable_item_ids = order_repo.list_order_item_ids(db, order.id)
            audit_service.record_event(
                db,
                actor=actor,
                event_type=audit_service.EVENT_ORDER_CONFIRMED,
                entity_type=audit_service.ENTITY_ORDER,
                entity_id=order.id,
                metadata={
                    "table_group_id": str(table_group_id),
                    "physical_table_id": str(physical_table_id),
                    "table_code": table.table_code,
                    "order_item_count": len(stable_item_ids),
                    "idempotency_key": idempotency_key,
                },
            )
            return order.id, table_group_id, stable_item_ids
    except IntegrityError:
        db.rollback()
        existing_after_conflict = _load_existing_confirmation(db, idempotency_key)
        if existing_after_conflict:
            return existing_after_conflict
        raise
