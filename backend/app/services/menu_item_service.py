# backend/app/services/menu_item_service.py
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import menu_item_repo
from app.services.errors import InvalidStateError, NotFoundError
from app.services.transaction import transactional


AVAILABLE = "AVAILABLE"
UNAVAILABLE = "UNAVAILABLE"
RETIRED = "RETIRED"


def list_menu_items(db: Session):
    return menu_item_repo.list_menu_items(db)


def create_menu_item(db: Session, name: str, price: Decimal):
    with transactional(db):
        return menu_item_repo.create_menu_item(db, name=name, price=price, status=AVAILABLE)


def update_menu_item(
    db: Session,
    menu_item_id: UUID,
    *,
    name: str | None = None,
    price: Decimal | None = None,
    status: str | None = None,
):
    with transactional(db):
        item = menu_item_repo.get_menu_item(db, menu_item_id)
        if not item:
            raise NotFoundError("MenuItem not found")

        if item.status == RETIRED and status in {AVAILABLE, UNAVAILABLE}:
            raise InvalidStateError("RETIRED MenuItem cannot transition to AVAILABLE or UNAVAILABLE")

        if name is not None:
            item.name = name
        if price is not None:
            item.price = price
        if status is not None:
            item.status = status

        db.flush()
        return item


def retire_menu_item(db: Session, menu_item_id: UUID):
    with transactional(db):
        item = menu_item_repo.get_menu_item(db, menu_item_id)
        if not item:
            raise NotFoundError("MenuItem not found")
        item.status = RETIRED
        db.flush()
        return item
