from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.models.menu_item import MenuItem
from app.models.modifier_group import ModifierGroup
from app.models.modifier_option import ModifierOption


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


def seed_menu_item(db: Session, name: str = "Thai Noodle") -> MenuItem:
    item = MenuItem(
        id=uuid4(),
        name=name,
        price=Decimal("50.00"),
        category="Food",
        status="AVAILABLE",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def seed_modifier_group(db: Session, code: str, name: str, is_active: bool = True) -> ModifierGroup:
    group = ModifierGroup(id=uuid4(), code=code, name=name, is_active=is_active)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def seed_modifier_option(
    db: Session,
    group_id: UUID,
    code: str,
    label: str,
    price_delta: str = "10.00",
    is_active: bool = True,
) -> ModifierOption:
    option = ModifierOption(
        id=uuid4(),
        modifier_group_id=group_id,
        code=code,
        label=label,
        price_delta=Decimal(price_delta),
        is_active=is_active,
    )
    db.add(option)
    db.commit()
    db.refresh(option)
    return option


def test_modifier_group_crud_api(client: TestClient, admin_auth_header: dict[str, str]) -> None:
    created = client.post(
        "/modifier-groups",
        json={"code": "ADDON", "name": "Add-on"},
        headers=admin_auth_header,
    )
    assert created.status_code == 201
    group_id = created.json()["id"]

    listed = client.get("/modifier-groups", headers=admin_auth_header)
    assert listed.status_code == 200
    assert any(row["id"] == group_id for row in listed.json())

    fetched = client.get(f"/modifier-groups/{group_id}", headers=admin_auth_header)
    assert fetched.status_code == 200
    assert fetched.json()["code"] == "ADDON"

    updated = client.patch(
        f"/modifier-groups/{group_id}",
        json={"name": "Add-ons", "is_active": False},
        headers=admin_auth_header,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Add-ons"
    assert updated.json()["is_active"] is False


def test_modifier_option_crud_api(
    client: TestClient, db_session: Session, admin_auth_header: dict[str, str]
) -> None:
    group = seed_modifier_group(db_session, "SPICY_LEVEL", "Spicy Level")

    created = client.post(
        f"/modifier-groups/{group.id}/options",
        json={"code": "MEDIUM", "label": "Medium", "price_delta": "0.00"},
        headers=admin_auth_header,
    )
    assert created.status_code == 201
    option_id = created.json()["id"]

    listed = client.get(f"/modifier-groups/{group.id}/options", headers=admin_auth_header)
    assert listed.status_code == 200
    assert any(row["id"] == option_id for row in listed.json())

    fetched = client.get(f"/modifier-options/{option_id}", headers=admin_auth_header)
    assert fetched.status_code == 200
    assert fetched.json()["label"] == "Medium"

    updated = client.patch(
        f"/modifier-options/{option_id}",
        json={"label": "Medium Spicy", "price_delta": "5.00", "is_active": False},
        headers=admin_auth_header,
    )
    assert updated.status_code == 200
    payload = updated.json()
    assert payload["label"] == "Medium Spicy"
    assert payload["price_delta"] == "5.00"
    assert payload["is_active"] is False


def test_menu_item_modifier_config_put_and_get(
    client: TestClient, db_session: Session, admin_auth_header: dict[str, str]
) -> None:
    item = seed_menu_item(db_session)
    add_on_group = seed_modifier_group(db_session, "ADDON", "Add-on")
    spicy_group = seed_modifier_group(db_session, "SPICY_LEVEL", "Spicy Level")
    egg = seed_modifier_option(db_session, add_on_group.id, "FRIED_EGG", "Fried Egg")
    crackling = seed_modifier_option(db_session, add_on_group.id, "CRACKLING", "Pork Crackling")
    medium = seed_modifier_option(db_session, spicy_group.id, "MEDIUM", "Medium")

    put_response = client.put(
        f"/menu-items/{item.id}/modifiers",
        json={
            "groups": [
                {
                    "modifier_group_id": str(add_on_group.id),
                    "min_select": 0,
                    "max_select": 3,
                    "option_ids": [str(egg.id), str(crackling.id)],
                },
                {
                    "modifier_group_id": str(spicy_group.id),
                    "min_select": 1,
                    "max_select": 1,
                    "option_ids": [str(medium.id)],
                },
            ]
        },
        headers=admin_auth_header,
    )
    assert put_response.status_code == 200
    put_payload = put_response.json()
    assert len(put_payload["groups"]) == 2

    get_response = client.get(f"/menu-items/{item.id}/modifiers", headers=admin_auth_header)
    assert get_response.status_code == 200
    get_payload = get_response.json()
    assert len(get_payload["groups"]) == 2
    first_group = next(row for row in get_payload["groups"] if row["modifier_group_id"] == str(add_on_group.id))
    assert first_group["group_name"] == "Add-on"
    assert sorted(first_group["option_ids"]) == sorted([str(egg.id), str(crackling.id)])


def test_menu_item_modifier_config_rejects_duplicate_group_payload(
    client: TestClient, db_session: Session, admin_auth_header: dict[str, str]
) -> None:
    item = seed_menu_item(db_session)
    group = seed_modifier_group(db_session, "ADDON", "Add-on")
    option = seed_modifier_option(db_session, group.id, "EGG", "Egg")

    response = client.put(
        f"/menu-items/{item.id}/modifiers",
        json={
            "groups": [
                {
                    "modifier_group_id": str(group.id),
                    "min_select": 0,
                    "max_select": 1,
                    "option_ids": [str(option.id)],
                },
                {
                    "modifier_group_id": str(group.id),
                    "min_select": 0,
                    "max_select": 2,
                    "option_ids": [str(option.id)],
                },
            ]
        },
        headers=admin_auth_header,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate modifier_group_id in groups payload"


def test_menu_item_modifier_config_rejects_option_group_mismatch(
    client: TestClient, db_session: Session, admin_auth_header: dict[str, str]
) -> None:
    item = seed_menu_item(db_session)
    add_on = seed_modifier_group(db_session, "ADDON", "Add-on")
    spicy = seed_modifier_group(db_session, "SPICY", "Spicy")
    spicy_option = seed_modifier_option(db_session, spicy.id, "MEDIUM", "Medium")

    response = client.put(
        f"/menu-items/{item.id}/modifiers",
        json={
            "groups": [
                {
                    "modifier_group_id": str(add_on.id),
                    "min_select": 0,
                    "max_select": 1,
                    "option_ids": [str(spicy_option.id)],
                }
            ]
        },
        headers=admin_auth_header,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "ModifierOption does not belong to requested ModifierGroup"


def test_menu_item_modifier_config_rejects_inactive_group_or_option(
    client: TestClient, db_session: Session, admin_auth_header: dict[str, str]
) -> None:
    item = seed_menu_item(db_session)
    inactive_group = seed_modifier_group(db_session, "ADDON", "Add-on", is_active=False)
    inactive_option = seed_modifier_option(
        db_session, inactive_group.id, "EGG", "Egg", is_active=False
    )

    group_response = client.put(
        f"/menu-items/{item.id}/modifiers",
        json={
            "groups": [
                {
                    "modifier_group_id": str(inactive_group.id),
                    "min_select": 0,
                    "max_select": 1,
                    "option_ids": [str(inactive_option.id)],
                }
            ]
        },
        headers=admin_auth_header,
    )
    assert group_response.status_code == 409
    assert group_response.json()["detail"] == "One or more ModifierGroups are inactive"


def test_modifier_endpoints_require_admin_role(
    client: TestClient, waiter_auth_header: dict[str, str]
) -> None:
    list_groups = client.get("/modifier-groups", headers=waiter_auth_header)
    create_group = client.post(
        "/modifier-groups",
        json={"code": "ADDON", "name": "Add-on"},
        headers=waiter_auth_header,
    )
    assert list_groups.status_code == 403
    assert create_group.status_code == 403
