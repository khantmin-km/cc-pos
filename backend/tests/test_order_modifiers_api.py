from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.models.menu_item import MenuItem
from app.models.order_item import OrderItem
from app.models.physical_table import PhysicalTable
from app.services import order_service


@pytest.fixture()
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def seed_table(db: Session, table_code: str) -> PhysicalTable:
    table = PhysicalTable(id=uuid4(), table_code=table_code)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def seed_menu_item(db: Session, name: str, price: str, category: str = "Food") -> MenuItem:
    item = MenuItem(
        id=uuid4(),
        name=name,
        price=Decimal(price),
        category=category,
        status="AVAILABLE",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _setup_modifier_config(
    client: TestClient,
    *,
    admin_auth_header: dict[str, str],
    menu_item_id: UUID,
) -> tuple[str, str]:
    group = client.post(
        "/modifier-groups",
        json={"code": "ADDON", "name": "Add-on"},
        headers=admin_auth_header,
    )
    assert group.status_code == 201
    group_id = group.json()["id"]

    option = client.post(
        f"/modifier-groups/{group_id}/options",
        json={"code": "EGG", "label": "Fried Egg", "price_delta": "10.00"},
        headers=admin_auth_header,
    )
    assert option.status_code == 201
    option_id = option.json()["id"]

    put = client.put(
        f"/menu-items/{menu_item_id}/modifiers",
        json={
            "groups": [
                {
                    "modifier_group_id": group_id,
                    "min_select": 1,
                    "max_select": 2,
                    "option_ids": [option_id],
                }
            ]
        },
        headers=admin_auth_header,
    )
    assert put.status_code == 200
    return group_id, option_id


def test_confirm_order_with_modifier_creates_main_and_child_items(
    client: TestClient,
    db_session: Session,
    waiter_auth_header: dict[str, str],
    admin_auth_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "OM1")
    menu_item = seed_menu_item(db_session, "Thai Noodle", "50.00")
    _group_id, option_id = _setup_modifier_config(
        client,
        admin_auth_header=admin_auth_header,
        menu_item_id=menu_item.id,
    )

    start = client.post(f"/tables/{table.id}/start-service", headers=waiter_auth_header)
    assert start.status_code == 200

    response = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "mod-order-1",
            "items": [
                {
                    "client_line_id": "line-1",
                    "menu_item_id": str(menu_item.id),
                    "note": "less soup",
                    "modifier_selections": [
                        {
                            "modifier_group_id": _group_id,
                            "selected_option_ids": [option_id],
                        }
                    ],
                }
            ],
        },
        headers=waiter_auth_header,
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["order_item_ids"]) == 2

    created_ids = [UUID(v) for v in payload["order_item_ids"]]
    items = list(db_session.scalars(select(OrderItem).where(OrderItem.id.in_(created_ids))))
    assert len(items) == 2

    main_items = [row for row in items if row.kind == "MAIN"]
    child_items = [row for row in items if row.kind == "MODIFIER"]
    assert len(main_items) == 1
    assert len(child_items) == 1

    main_item = main_items[0]
    child_item = child_items[0]
    assert child_item.parent_order_item_id == main_item.id
    assert child_item.modifier_group_name_snap == "Add-on"
    assert child_item.modifier_option_label_snap == "Fried Egg"
    assert str(child_item.unit_price_snap) == "10.00"


def test_confirm_order_modifier_validation_returns_structured_error(
    client: TestClient,
    db_session: Session,
    waiter_auth_header: dict[str, str],
    admin_auth_header: dict[str, str],
) -> None:
    table = seed_table(db_session, "OM2")
    menu_item = seed_menu_item(db_session, "Thai Noodle", "50.00")
    group_id, option_id = _setup_modifier_config(
        client,
        admin_auth_header=admin_auth_header,
        menu_item_id=menu_item.id,
    )

    start = client.post(f"/tables/{table.id}/start-service", headers=waiter_auth_header)
    assert start.status_code == 200

    response = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "mod-order-2",
            "items": [
                {
                    "client_line_id": "line-1",
                    "menu_item_id": str(menu_item.id),
                    "modifier_selections": [
                        {
                            "modifier_group_id": group_id,
                            "selected_option_ids": [option_id],
                        },
                        {
                            "modifier_group_id": group_id,
                            "selected_option_ids": [option_id],
                        },
                    ],
                }
            ],
        },
        headers=waiter_auth_header,
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["code"] == "MODIFIER_VALIDATION_FAILED"
    assert payload["message"] == "Modifier validation failed"
    assert isinstance(payload["details"], list)
    assert any(
        detail["client_line_id"] == "line-1"
        and detail["modifier_group_id"] == group_id
        and detail["reason"] == "DUPLICATE_GROUP_SELECTION"
        for detail in payload["details"]
    )


def test_confirm_order_prints_modifiers_grouped_under_main_item(
    client: TestClient,
    db_session: Session,
    waiter_auth_header: dict[str, str],
    admin_auth_header: dict[str, str],
    monkeypatch,
) -> None:
    table = seed_table(db_session, "OM3")
    menu_item = seed_menu_item(db_session, "Thai Noodle", "50.00")
    group_id, option_id = _setup_modifier_config(
        client,
        admin_auth_header=admin_auth_header,
        menu_item_id=menu_item.id,
    )
    second_option = client.post(
        f"/modifier-groups/{group_id}/options",
        json={"code": "CRACKLING", "label": "Pork Crackling", "price_delta": "15.00"},
        headers=admin_auth_header,
    )
    assert second_option.status_code == 201
    second_option_id = second_option.json()["id"]
    update = client.put(
        f"/menu-items/{menu_item.id}/modifiers",
        json={
            "groups": [
                {
                    "modifier_group_id": group_id,
                    "min_select": 0,
                    "max_select": 3,
                    "option_ids": [option_id, second_option_id],
                }
            ]
        },
        headers=admin_auth_header,
    )
    assert update.status_code == 200

    start = client.post(f"/tables/{table.id}/start-service", headers=waiter_auth_header)
    assert start.status_code == 200

    captured_items = []

    def capture_ticket(items):
        captured_items.extend(items)
        return True

    monkeypatch.setattr(order_service, "print_kitchen_ticket", capture_ticket)

    response = client.post(
        f"/tables/{table.id}/orders/confirm",
        json={
            "idempotency_key": "mod-order-3",
            "items": [
                {
                    "client_line_id": "line-1",
                    "menu_item_id": str(menu_item.id),
                    "modifier_selections": [
                        {
                            "modifier_group_id": group_id,
                            "selected_option_ids": [option_id, second_option_id],
                        }
                    ],
                }
            ],
        },
        headers=waiter_auth_header,
    )
    assert response.status_code == 200
    assert len(captured_items) == 1

    ticket_item = captured_items[0]
    assert ticket_item.menu_item_name == "Thai Noodle"
    assert len(ticket_item.modifier_groups) == 1
    assert ticket_item.modifier_groups[0].group_name == "Add-on"
    assert ticket_item.modifier_groups[0].option_labels == ("Fried Egg", "Pork Crackling")
