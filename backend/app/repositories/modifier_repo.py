from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.models.menu_item_modifier_group import MenuItemModifierGroup
from app.models.menu_item_modifier_group_option import MenuItemModifierGroupOption
from app.models.modifier_group import ModifierGroup
from app.models.modifier_option import ModifierOption


def list_modifier_groups(db: Session) -> list[ModifierGroup]:
    stmt = select(ModifierGroup).order_by(ModifierGroup.created_at.asc(), ModifierGroup.id.asc())
    return list(db.scalars(stmt))


def get_modifier_group(db: Session, modifier_group_id: UUID) -> ModifierGroup | None:
    return db.get(ModifierGroup, modifier_group_id)


def create_modifier_group(db: Session, *, code: str, name: str) -> ModifierGroup:
    group = ModifierGroup(code=code, name=name, is_active=True)
    db.add(group)
    db.flush()
    return group


def list_modifier_options_by_group(db: Session, modifier_group_id: UUID) -> list[ModifierOption]:
    stmt = (
        select(ModifierOption)
        .where(ModifierOption.modifier_group_id == modifier_group_id)
        .order_by(ModifierOption.created_at.asc(), ModifierOption.id.asc())
    )
    return list(db.scalars(stmt))


def get_modifier_option(db: Session, modifier_option_id: UUID) -> ModifierOption | None:
    return db.get(ModifierOption, modifier_option_id)


def create_modifier_option(
    db: Session,
    *,
    modifier_group_id: UUID,
    code: str,
    label: str,
    price_delta,
) -> ModifierOption:
    option = ModifierOption(
        modifier_group_id=modifier_group_id,
        code=code,
        label=label,
        price_delta=price_delta,
        is_active=True,
    )
    db.add(option)
    db.flush()
    return option


def get_modifier_groups_by_ids(db: Session, modifier_group_ids: list[UUID]) -> list[ModifierGroup]:
    if not modifier_group_ids:
        return []
    stmt = select(ModifierGroup).where(ModifierGroup.id.in_(modifier_group_ids))
    return list(db.scalars(stmt))


def get_modifier_options_by_ids(db: Session, modifier_option_ids: list[UUID]) -> list[ModifierOption]:
    if not modifier_option_ids:
        return []
    stmt = select(ModifierOption).where(ModifierOption.id.in_(modifier_option_ids))
    return list(db.scalars(stmt))


def get_menu_item(db: Session, menu_item_id: UUID) -> MenuItem | None:
    return db.get(MenuItem, menu_item_id)


def clear_menu_item_modifier_config(db: Session, menu_item_id: UUID) -> None:
    group_ids_stmt = select(MenuItemModifierGroup.id).where(MenuItemModifierGroup.menu_item_id == menu_item_id)
    group_ids = list(db.scalars(group_ids_stmt))
    if group_ids:
        db.execute(
            delete(MenuItemModifierGroupOption).where(
                MenuItemModifierGroupOption.menu_item_modifier_group_id.in_(group_ids)
            )
        )
    db.execute(delete(MenuItemModifierGroup).where(MenuItemModifierGroup.menu_item_id == menu_item_id))
    db.flush()


def create_menu_item_modifier_group(
    db: Session,
    *,
    menu_item_id: UUID,
    modifier_group_id: UUID,
    min_select: int,
    max_select: int,
) -> MenuItemModifierGroup:
    row = MenuItemModifierGroup(
        menu_item_id=menu_item_id,
        modifier_group_id=modifier_group_id,
        min_select=min_select,
        max_select=max_select,
    )
    db.add(row)
    db.flush()
    return row


def create_menu_item_modifier_group_option(
    db: Session,
    *,
    menu_item_modifier_group_id: UUID,
    modifier_option_id: UUID,
) -> MenuItemModifierGroupOption:
    row = MenuItemModifierGroupOption(
        menu_item_modifier_group_id=menu_item_modifier_group_id,
        modifier_option_id=modifier_option_id,
    )
    db.add(row)
    db.flush()
    return row


def list_menu_item_modifier_groups(
    db: Session,
    menu_item_id: UUID,
) -> list[tuple[MenuItemModifierGroup, ModifierGroup]]:
    stmt = (
        select(MenuItemModifierGroup, ModifierGroup)
        .join(ModifierGroup, MenuItemModifierGroup.modifier_group_id == ModifierGroup.id)
        .where(MenuItemModifierGroup.menu_item_id == menu_item_id)
        .order_by(MenuItemModifierGroup.created_at.asc(), MenuItemModifierGroup.id.asc())
    )
    return list(db.execute(stmt).all())


def list_menu_item_modifier_option_links(
    db: Session,
    menu_item_modifier_group_ids: list[UUID],
) -> list[MenuItemModifierGroupOption]:
    if not menu_item_modifier_group_ids:
        return []
    stmt = select(MenuItemModifierGroupOption).where(
        MenuItemModifierGroupOption.menu_item_modifier_group_id.in_(menu_item_modifier_group_ids)
    )
    return list(db.scalars(stmt))
