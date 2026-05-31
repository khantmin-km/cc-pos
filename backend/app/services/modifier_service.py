from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import modifier_repo
from app.services.errors import ConflictError, NotFoundError
from app.services.transaction import transactional


def list_modifier_groups(db: Session):
    return modifier_repo.list_modifier_groups(db)


def get_modifier_group(db: Session, modifier_group_id: UUID):
    group = modifier_repo.get_modifier_group(db, modifier_group_id)
    if not group:
        raise NotFoundError("ModifierGroup not found")
    return group


def create_modifier_group(db: Session, *, code: str, name: str):
    try:
        with transactional(db):
            return modifier_repo.create_modifier_group(db, code=code, name=name)
    except IntegrityError as exc:
        raise ConflictError("ModifierGroup code already exists") from exc


def update_modifier_group(
    db: Session,
    modifier_group_id: UUID,
    *,
    name: str | None = None,
    is_active: bool | None = None,
):
    with transactional(db):
        group = modifier_repo.get_modifier_group(db, modifier_group_id)
        if not group:
            raise NotFoundError("ModifierGroup not found")
        if name is not None:
            group.name = name
        if is_active is not None:
            group.is_active = is_active
        db.flush()
        return group


def list_modifier_options_by_group(db: Session, modifier_group_id: UUID):
    group = modifier_repo.get_modifier_group(db, modifier_group_id)
    if not group:
        raise NotFoundError("ModifierGroup not found")
    return modifier_repo.list_modifier_options_by_group(db, modifier_group_id)


def get_modifier_option(db: Session, modifier_option_id: UUID):
    option = modifier_repo.get_modifier_option(db, modifier_option_id)
    if not option:
        raise NotFoundError("ModifierOption not found")
    return option


def create_modifier_option(
    db: Session,
    *,
    modifier_group_id: UUID,
    code: str,
    label: str,
    price_delta: Decimal,
):
    group = modifier_repo.get_modifier_group(db, modifier_group_id)
    if not group:
        raise NotFoundError("ModifierGroup not found")

    try:
        with transactional(db):
            return modifier_repo.create_modifier_option(
                db,
                modifier_group_id=modifier_group_id,
                code=code,
                label=label,
                price_delta=price_delta,
            )
    except IntegrityError as exc:
        raise ConflictError("ModifierOption code already exists in this group") from exc


def update_modifier_option(
    db: Session,
    modifier_option_id: UUID,
    *,
    label: str | None = None,
    price_delta: Decimal | None = None,
    is_active: bool | None = None,
):
    with transactional(db):
        option = modifier_repo.get_modifier_option(db, modifier_option_id)
        if not option:
            raise NotFoundError("ModifierOption not found")
        if label is not None:
            option.label = label
        if price_delta is not None:
            option.price_delta = price_delta
        if is_active is not None:
            option.is_active = is_active
        db.flush()
        return option


def _validate_menu_item_modifier_groups(groups: list) -> None:
    group_ids = [entry.modifier_group_id for entry in groups]
    if len(group_ids) != len(set(group_ids)):
        raise ConflictError("Duplicate modifier_group_id in groups payload")

    for entry in groups:
        if len(entry.option_ids) != len(set(entry.option_ids)):
            raise ConflictError("Duplicate option id in one modifier group payload")


def _validate_group_and_option_existence(db: Session, groups: list) -> tuple[dict[UUID, object], dict[UUID, object]]:
    group_ids = [entry.modifier_group_id for entry in groups]
    option_ids = sorted({option_id for entry in groups for option_id in entry.option_ids})

    modifier_groups = modifier_repo.get_modifier_groups_by_ids(db, group_ids)
    by_group_id = {group.id: group for group in modifier_groups}
    missing_group_ids = [gid for gid in group_ids if gid not in by_group_id]
    if missing_group_ids:
        raise ConflictError("One or more ModifierGroups do not exist")
    inactive_groups = [group.id for group in modifier_groups if not group.is_active]
    if inactive_groups:
        raise ConflictError("One or more ModifierGroups are inactive")

    modifier_options = modifier_repo.get_modifier_options_by_ids(db, option_ids)
    by_option_id = {option.id: option for option in modifier_options}
    missing_option_ids = [oid for oid in option_ids if oid not in by_option_id]
    if missing_option_ids:
        raise ConflictError("One or more ModifierOptions do not exist")
    inactive_options = [option.id for option in modifier_options if not option.is_active]
    if inactive_options:
        raise ConflictError("One or more ModifierOptions are inactive")

    return by_group_id, by_option_id


def _validate_option_membership(groups: list, by_option_id: dict[UUID, object]) -> None:
    for entry in groups:
        for option_id in entry.option_ids:
            option = by_option_id[option_id]
            if option.modifier_group_id != entry.modifier_group_id:
                raise ConflictError("ModifierOption does not belong to requested ModifierGroup")


def _render_menu_item_modifier_config(db: Session, menu_item_id: UUID) -> list[dict]:
    group_rows = modifier_repo.list_menu_item_modifier_groups(db, menu_item_id)
    if not group_rows:
        return []

    menu_group_ids = [group_row.id for group_row, _ in group_rows]
    option_links = modifier_repo.list_menu_item_modifier_option_links(db, menu_group_ids)
    options_by_menu_group_id: dict[UUID, list[UUID]] = defaultdict(list)
    for link in option_links:
        options_by_menu_group_id[link.menu_item_modifier_group_id].append(link.modifier_option_id)

    groups: list[dict] = []
    for menu_group, group in group_rows:
        groups.append(
            {
                "modifier_group_id": group.id,
                "group_name": group.name,
                "min_select": menu_group.min_select,
                "max_select": menu_group.max_select,
                "option_ids": sorted(options_by_menu_group_id.get(menu_group.id, []), key=str),
            }
        )
    return groups


def get_menu_item_modifier_config(db: Session, menu_item_id: UUID) -> list[dict]:
    item = modifier_repo.get_menu_item(db, menu_item_id)
    if not item:
        raise NotFoundError("MenuItem not found")
    return _render_menu_item_modifier_config(db, menu_item_id)


def replace_menu_item_modifier_config(db: Session, menu_item_id: UUID, groups: list) -> list[dict]:
    item = modifier_repo.get_menu_item(db, menu_item_id)
    if not item:
        raise NotFoundError("MenuItem not found")

    _validate_menu_item_modifier_groups(groups)
    _, by_option_id = _validate_group_and_option_existence(db, groups)
    _validate_option_membership(groups, by_option_id)

    with transactional(db):
        modifier_repo.clear_menu_item_modifier_config(db, menu_item_id)
        for group_entry in groups:
            menu_group = modifier_repo.create_menu_item_modifier_group(
                db,
                menu_item_id=menu_item_id,
                modifier_group_id=group_entry.modifier_group_id,
                min_select=group_entry.min_select,
                max_select=group_entry.max_select,
            )
            for option_id in group_entry.option_ids:
                modifier_repo.create_menu_item_modifier_group_option(
                    db,
                    menu_item_modifier_group_id=menu_group.id,
                    modifier_option_id=option_id,
                )
        return _render_menu_item_modifier_config(db, menu_item_id)
