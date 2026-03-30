# backend/app/services/menu_item_service.py
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import menu_item_repo
from app.services.errors import ConflictError, InvalidStateError, NotFoundError
from app.services.transaction import transactional


AVAILABLE = "AVAILABLE"
UNAVAILABLE = "UNAVAILABLE"
RETIRED = "RETIRED"

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
MENU_DIR = STATIC_DIR / "menu"
MAX_IMAGE_BYTES = 5 * 1024 * 1024
IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


def list_menu_items(db: Session):
    return menu_item_repo.list_menu_items(db)


def create_menu_item(db: Session, name: str, price: Decimal, category: str):
    with transactional(db):
        return menu_item_repo.create_menu_item(
            db,
            name=name,
            price=price,
            category=category,
            status=AVAILABLE,
        )


def update_menu_item(
    db: Session,
    menu_item_id: UUID,
    *,
    name: str | None = None,
    price: Decimal | None = None,
    category: str | None = None,
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
        if category is not None:
            item.category = category
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


def update_menu_item_image(
    db: Session,
    menu_item_id: UUID,
    *,
    content_type: str | None,
    data: bytes,
) -> object:
    if not content_type or content_type not in IMAGE_TYPES:
        raise ConflictError("Unsupported image type")
    if len(data) > MAX_IMAGE_BYTES:
        raise ConflictError("Image exceeds maximum size")

    with transactional(db):
        item = menu_item_repo.get_menu_item(db, menu_item_id)
        if not item:
            raise NotFoundError("MenuItem not found")

        MENU_DIR.mkdir(parents=True, exist_ok=True)
        ext = IMAGE_TYPES[content_type]
        filename = f"{item.id}.{ext}"
        file_path = MENU_DIR / filename

        try:
            file_path.write_bytes(data)
        except OSError as exc:
            raise ConflictError(f"Failed to store image: {exc}") from exc

        item.image_path = f"menu/{filename}"
        db.flush()
        return item
