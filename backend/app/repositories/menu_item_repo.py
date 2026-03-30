# backend/app/repositories/menu_item_repo.py
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem


def get_menu_items_for_update(db: Session, menu_item_ids: list[UUID]) -> list[MenuItem]:
    if not menu_item_ids:
        return []
    stmt = select(MenuItem).where(MenuItem.id.in_(menu_item_ids)).with_for_update()
    return list(db.scalars(stmt))


def list_menu_items(db: Session) -> list[MenuItem]:
    stmt = select(MenuItem).order_by(MenuItem.created_at.asc(), MenuItem.id.asc())
    return list(db.scalars(stmt))


def get_menu_item(db: Session, menu_item_id: UUID) -> MenuItem | None:
    return db.get(MenuItem, menu_item_id)


def create_menu_item(db: Session, name: str, price: Decimal, category: str, status: str) -> MenuItem:
    item = MenuItem(name=name, price=price, category=category, status=status)
    db.add(item)
    db.flush()
    return item
