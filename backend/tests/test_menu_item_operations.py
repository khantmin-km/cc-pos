# backend/tests/test_menu_item_operations.py
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.models.physical_table import PhysicalTable
from app.schemas.order import OrderConfirmItemRequest
from app.services import menu_item_service, order_service, table_group_service
from app.services.errors import InvalidStateError, NotFoundError


def seed_table(db: Session, table_code: str) -> PhysicalTable:
    table = PhysicalTable(id=uuid4(), table_code=table_code)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def test_create_menu_item_defaults_to_available(db_session: Session) -> None:
    item = menu_item_service.create_menu_item(db_session, name="Soup", price=Decimal("7.50"))
    assert item.status == "AVAILABLE"
    assert item.name == "Soup"
    assert item.price == Decimal("7.50")


def test_list_menu_items_returns_created_items(db_session: Session) -> None:
    menu_item_service.create_menu_item(db_session, name="Soup", price=Decimal("7.50"))
    menu_item_service.create_menu_item(db_session, name="Tea", price=Decimal("2.00"))

    items = menu_item_service.list_menu_items(db_session)
    names = [item.name for item in items]
    assert "Soup" in names
    assert "Tea" in names


def test_update_menu_item_fields(db_session: Session) -> None:
    item = menu_item_service.create_menu_item(db_session, name="Soup", price=Decimal("7.50"))

    updated = menu_item_service.update_menu_item(
        db_session,
        item.id,
        name="Hot Soup",
        price=Decimal("8.00"),
        status="UNAVAILABLE",
    )

    assert updated.name == "Hot Soup"
    assert updated.price == Decimal("8.00")
    assert updated.status == "UNAVAILABLE"


def test_retired_menu_item_cannot_transition_back(db_session: Session) -> None:
    item = menu_item_service.create_menu_item(db_session, name="Soup", price=Decimal("7.50"))
    menu_item_service.retire_menu_item(db_session, item.id)

    with pytest.raises(InvalidStateError):
        menu_item_service.update_menu_item(db_session, item.id, status="AVAILABLE")


def test_retire_menu_item_referenced_by_order_is_allowed(db_session: Session) -> None:
    table = seed_table(db_session, "M1")
    table_group_service.start_service(db_session, table.id)
    item = menu_item_service.create_menu_item(db_session, name="Soup", price=Decimal("7.50"))

    order_service.confirm_order(
        db=db_session,
        physical_table_id=table.id,
        idempotency_key="menu-retire-key",
        items=[OrderConfirmItemRequest(menu_item_id=item.id, quantity=1)],
    )

    retired = menu_item_service.retire_menu_item(db_session, item.id)
    assert retired.status == "RETIRED"


def test_update_missing_menu_item_raises_not_found(db_session: Session) -> None:
    with pytest.raises(NotFoundError):
        menu_item_service.update_menu_item(db_session, uuid4(), name="Missing")


def test_menu_item_model_has_terminal_status_value(db_session: Session) -> None:
    item = MenuItem(id=uuid4(), name="Legacy", price=Decimal("1.00"), status="RETIRED")
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    assert item.status == "RETIRED"
