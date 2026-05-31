# backend/app/services/order_service.py
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.printing import KitchenTicketItem, print_kitchen_ticket
from app.repositories import menu_item_repo, modifier_repo, order_repo, physical_table_repo, table_group_repo
from app.schemas.order import OrderConfirmItemRequest
from app.services import audit_service
from app.services.errors import ConflictError, InvalidStateError, ModifierValidationError, NotFoundError
from app.services.transaction import transactional


OPEN = "OPEN"
CONFIRMED = "CONFIRMED"
ACTIVE = "ACTIVE"
AVAILABLE = "AVAILABLE"
MAIN = "MAIN"
MODIFIER = "MODIFIER"

REASON_MISSING_REQUIRED_SELECTION = "MISSING_REQUIRED_SELECTION"
REASON_TOO_MANY_SELECTIONS = "TOO_MANY_SELECTIONS"
REASON_OPTION_NOT_ALLOWED = "OPTION_NOT_ALLOWED"
REASON_OPTION_NOT_AVAILABLE = "OPTION_NOT_AVAILABLE"
REASON_GROUP_NOT_CONFIGURED = "GROUP_NOT_CONFIGURED"
REASON_DUPLICATE_SELECTION = "DUPLICATE_SELECTION"
REASON_DUPLICATE_GROUP_SELECTION = "DUPLICATE_GROUP_SELECTION"


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


def _load_modifier_config_for_menu_item(
    db: Session, menu_item_id: UUID
) -> dict[UUID, dict]:
    group_rows = modifier_repo.list_menu_item_modifier_groups(db, menu_item_id)
    if not group_rows:
        return {}

    menu_group_ids = [menu_group.id for menu_group, _ in group_rows]
    option_links = modifier_repo.list_menu_item_modifier_option_links(db, menu_group_ids)
    option_ids_by_menu_group_id: dict[UUID, set[UUID]] = {}
    for link in option_links:
        option_ids_by_menu_group_id.setdefault(link.menu_item_modifier_group_id, set()).add(link.modifier_option_id)

    config: dict[UUID, dict] = {}
    for menu_group, group in group_rows:
        config[group.id] = {
            "group_active": bool(group.is_active),
            "group_name": group.name,
            "min_select": menu_group.min_select,
            "max_select": menu_group.max_select,
            "allowed_option_ids": option_ids_by_menu_group_id.get(menu_group.id, set()),
        }
    return config


def _collect_modifier_validation_errors(db: Session, items: list[OrderConfirmItemRequest]) -> tuple[list[dict], dict]:
    errors: list[dict] = []

    menu_item_ids = sorted({line.menu_item_id for line in items})
    configs_by_menu_item_id = {
        menu_item_id: _load_modifier_config_for_menu_item(db, menu_item_id) for menu_item_id in menu_item_ids
    }

    all_selected_option_ids = sorted(
        {
            option_id
            for line in items
            for selection in line.modifier_selections
            for option_id in selection.selected_option_ids
        }
    )
    option_rows = modifier_repo.get_modifier_options_by_ids(db, all_selected_option_ids)
    option_by_id = {row.id: row for row in option_rows}

    resolved_lines: dict[str, list[dict]] = {}

    for line in items:
        line_config = configs_by_menu_item_id.get(line.menu_item_id, {})
        active_line_config = {
            group_id: cfg for group_id, cfg in line_config.items() if cfg["group_active"]
        }

        seen_groups: set[UUID] = set()
        line_group_selection_counts: dict[UUID, int] = {}
        line_resolved_modifiers: list[dict] = []

        for selection in line.modifier_selections:
            group_id = selection.modifier_group_id

            if group_id in seen_groups:
                errors.append(
                    {
                        "client_line_id": line.client_line_id,
                        "modifier_group_id": str(group_id),
                        "reason": REASON_DUPLICATE_GROUP_SELECTION,
                    }
                )
                continue
            seen_groups.add(group_id)

            group_cfg = active_line_config.get(group_id)
            if not group_cfg:
                errors.append(
                    {
                        "client_line_id": line.client_line_id,
                        "modifier_group_id": str(group_id),
                        "reason": REASON_GROUP_NOT_CONFIGURED,
                    }
                )
                continue

            selected_ids = selection.selected_option_ids
            if len(selected_ids) != len(set(selected_ids)):
                errors.append(
                    {
                        "client_line_id": line.client_line_id,
                        "modifier_group_id": str(group_id),
                        "reason": REASON_DUPLICATE_SELECTION,
                    }
                )
                continue

            line_group_selection_counts[group_id] = len(selected_ids)
            if len(selected_ids) > group_cfg["max_select"]:
                errors.append(
                    {
                        "client_line_id": line.client_line_id,
                        "modifier_group_id": str(group_id),
                        "reason": REASON_TOO_MANY_SELECTIONS,
                    }
                )
                continue

            for option_id in selected_ids:
                if option_id not in group_cfg["allowed_option_ids"]:
                    errors.append(
                        {
                            "client_line_id": line.client_line_id,
                            "modifier_group_id": str(group_id),
                            "reason": REASON_OPTION_NOT_ALLOWED,
                        }
                    )
                    continue
                option = option_by_id.get(option_id)
                if not option or not option.is_active:
                    errors.append(
                        {
                            "client_line_id": line.client_line_id,
                            "modifier_group_id": str(group_id),
                            "reason": REASON_OPTION_NOT_AVAILABLE,
                        }
                    )
                    continue
                line_resolved_modifiers.append(
                    {
                        "modifier_group_id": group_id,
                        "modifier_group_name": group_cfg["group_name"],
                        "option_id": option_id,
                        "option_label": option.label,
                        "price_delta": option.price_delta,
                    }
                )

        for group_id, group_cfg in active_line_config.items():
            selected_count = line_group_selection_counts.get(group_id, 0)
            if selected_count < group_cfg["min_select"]:
                errors.append(
                    {
                        "client_line_id": line.client_line_id,
                        "modifier_group_id": str(group_id),
                        "reason": REASON_MISSING_REQUIRED_SELECTION,
                    }
                )

        resolved_lines[line.client_line_id] = line_resolved_modifiers

    return errors, resolved_lines


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
            modifier_errors, resolved_line_modifiers = _collect_modifier_validation_errors(db, items)
            if modifier_errors:
                raise ModifierValidationError(modifier_errors)

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
                created_item = order_repo.create_order_item(
                    db=db,
                    order_id=order.id,
                    physical_table_id=physical_table_id,
                    menu_item_id=line.menu_item_id,
                    menu_item_name_snap=name_snap,
                    unit_price_snap=price_snap,
                    note_snap=line.note,
                    status=ACTIVE,
                    kind=MAIN,
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

                for modifier in resolved_line_modifiers.get(line.client_line_id, []):
                    modifier_item = order_repo.create_order_item(
                        db=db,
                        order_id=order.id,
                        physical_table_id=physical_table_id,
                        menu_item_id=None,
                        menu_item_name_snap=modifier["option_label"],
                        unit_price_snap=modifier["price_delta"],
                        note_snap=None,
                        status=ACTIVE,
                        kind=MODIFIER,
                        parent_order_item_id=created_item.id,
                        modifier_group_name_snap=modifier["modifier_group_name"],
                        modifier_option_label_snap=modifier["option_label"],
                    )
                    created_item_ids.append(modifier_item.id)
                    ticket_items.append(
                        KitchenTicketItem(
                            order_item_id=modifier_item.id,
                            table_code=table.table_code,
                            menu_item_name=modifier["option_label"],
                            note=None,
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
