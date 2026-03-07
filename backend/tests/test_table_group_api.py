# backend/tests/test_table_group_api.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import app
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.physical_table import PhysicalTable


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


def seed_order_item(db: Session, table_group_id, physical_table_id) -> OrderItem:
    order = Order(table_group_id=table_group_id, idempotency_key=str(uuid4()), state="CONFIRMED")
    db.add(order)
    db.flush()
    item = OrderItem(
        order_id=order.id,
        physical_table_id=physical_table_id,
        menu_item_id=None,
        menu_item_name_snap="API Test Item",
        unit_price_snap=Decimal("12.00"),
        status="ACTIVE",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def assert_table_group_payload_contract(
    payload: dict,
    *,
    expected_state: str | None = None,
    expect_closed_at_none: bool | None = None,
) -> None:
    assert set(payload.keys()) == {"id", "state", "physical_table_ids", "opened_at", "closed_at"}
    UUID(payload["id"])
    assert isinstance(payload["state"], str)
    if expected_state is not None:
        assert payload["state"] == expected_state
    assert isinstance(payload["physical_table_ids"], list)
    for table_id in payload["physical_table_ids"]:
        UUID(table_id)
    datetime.fromisoformat(payload["opened_at"])
    if expect_closed_at_none is True:
        assert payload["closed_at"] is None
    elif expect_closed_at_none is False:
        assert payload["closed_at"] is not None
        datetime.fromisoformat(payload["closed_at"])


def test_get_tables_returns_seeded_tables(client: TestClient, db_session: Session) -> None:
    table = seed_table(db_session, "API_T1")

    response = client.get("/tables")

    assert response.status_code == 200
    payload = response.json()
    assert any(row["id"] == str(table.id) for row in payload)
    assert any(row["table_code"] == "API_T1" for row in payload)


def test_start_service_returns_group_payload(client: TestClient, db_session: Session) -> None:
    table = seed_table(db_session, "API_T1")

    response = client.post(f"/tables/{table.id}/start-service")

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "OPEN"
    assert str(table.id) in payload["physical_table_ids"]
    assert payload["closed_at"] is None


def test_start_service_returns_409_for_assigned_table(
    client: TestClient, db_session: Session
) -> None:
    table = seed_table(db_session, "API_T1")
    first = client.post(f"/tables/{table.id}/start-service")
    assert first.status_code == 200

    second = client.post(f"/tables/{table.id}/start-service")

    assert second.status_code == 409


def test_get_table_group_by_id_returns_404_for_missing(client: TestClient) -> None:
    response = client.get(f"/table-groups/{uuid4()}")
    assert response.status_code == 404


def test_request_bill_then_mark_paid_then_close(client: TestClient, db_session: Session) -> None:
    table = seed_table(db_session, "API_T1")
    start = client.post(f"/tables/{table.id}/start-service")
    group_id = start.json()["id"]

    bill = client.post(f"/table-groups/{group_id}/request-bill")
    paid = client.post(f"/table-groups/{group_id}/mark-paid")
    closed = client.post(f"/table-groups/{group_id}/close")
    final = client.get(f"/table-groups/{group_id}")

    assert bill.status_code == 200
    assert paid.status_code == 200
    assert closed.status_code == 200
    assert final.status_code == 200
    assert final.json()["state"] == "CLOSED"
    assert final.json()["physical_table_ids"] == []


def test_request_bill_returns_400_when_not_open(client: TestClient, db_session: Session) -> None:
    table = seed_table(db_session, "API_T1")
    start = client.post(f"/tables/{table.id}/start-service")
    group_id = start.json()["id"]
    first = client.post(f"/table-groups/{group_id}/request-bill")
    assert first.status_code == 200

    second = client.post(f"/table-groups/{group_id}/request-bill")
    assert second.status_code == 400


def test_merge_returns_400_when_group_not_open(client: TestClient, db_session: Session) -> None:
    table_a = seed_table(db_session, "API_T1")
    table_b = seed_table(db_session, "API_T2")
    group_a = client.post(f"/tables/{table_a.id}/start-service").json()["id"]
    group_b = client.post(f"/tables/{table_b.id}/start-service").json()["id"]
    client.post(f"/table-groups/{group_b}/request-bill")

    response = client.post(
        "/table-groups/merge",
        json={"source_group_id": group_b, "target_group_id": group_a},
    )

    assert response.status_code == 400


def test_split_returns_409_when_order_items_exist(client: TestClient, db_session: Session) -> None:
    table_a = seed_table(db_session, "API_T1")
    table_b = seed_table(db_session, "API_T2")
    group = client.post(f"/tables/{table_a.id}/start-service").json()["id"]
    attach = client.post(
        f"/table-groups/{group}/tables/add",
        json={"physical_table_id": str(table_b.id)},
    )
    assert attach.status_code == 200
    seed_order_item(db_session, group, table_a.id)

    split = client.post(
        f"/table-groups/{group}/split",
        json={"physical_table_ids": [str(table_b.id)]},
    )

    assert split.status_code == 409


def test_attach_table_returns_404_for_missing_group(client: TestClient, db_session: Session) -> None:
    table = seed_table(db_session, "API_T1")

    response = client.post(
        f"/table-groups/{uuid4()}/tables/add",
        json={"physical_table_id": str(table.id)},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "TableGroup not found"


def test_attach_table_returns_409_when_table_already_assigned(
    client: TestClient, db_session: Session
) -> None:
    table_a = seed_table(db_session, "API_T1")
    table_b = seed_table(db_session, "API_T2")
    table_c = seed_table(db_session, "API_T3")

    group_a = client.post(f"/tables/{table_a.id}/start-service").json()["id"]
    group_b = client.post(f"/tables/{table_b.id}/start-service").json()["id"]
    attach = client.post(
        f"/table-groups/{group_a}/tables/add",
        json={"physical_table_id": str(table_c.id)},
    )
    assert attach.status_code == 200

    response = client.post(
        f"/table-groups/{group_b}/tables/add",
        json={"physical_table_id": str(table_c.id)},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "PhysicalTable is already assigned to a TableGroup"


def test_remove_table_returns_409_when_table_not_attached(
    client: TestClient, db_session: Session
) -> None:
    table_a = seed_table(db_session, "API_T1")
    table_b = seed_table(db_session, "API_T2")
    group = client.post(f"/tables/{table_a.id}/start-service").json()["id"]

    response = client.post(
        f"/table-groups/{group}/tables/remove",
        json={"physical_table_id": str(table_b.id)},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "PhysicalTable is not attached to this TableGroup"


def test_switch_returns_409_when_target_already_assigned(
    client: TestClient, db_session: Session
) -> None:
    table_a = seed_table(db_session, "API_T1")
    table_b = seed_table(db_session, "API_T2")
    table_c = seed_table(db_session, "API_T3")
    group_a = client.post(f"/tables/{table_a.id}/start-service").json()["id"]
    _group_b = client.post(f"/tables/{table_b.id}/start-service").json()["id"]

    response = client.post(
        f"/table-groups/{group_a}/switch",
        json={"from_table_id": str(table_a.id), "to_table_id": str(table_b.id)},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Target table is already assigned to a TableGroup"

    # Ensure original attachment is preserved.
    group_payload = client.get(f"/table-groups/{group_a}").json()
    assert str(table_a.id) in group_payload["physical_table_ids"]
    assert str(table_c.id) not in group_payload["physical_table_ids"]


def test_merge_returns_409_when_source_equals_target(
    client: TestClient, db_session: Session
) -> None:
    table = seed_table(db_session, "API_T1")
    group = client.post(f"/tables/{table.id}/start-service").json()["id"]

    response = client.post(
        "/table-groups/merge",
        json={"source_group_id": group, "target_group_id": group},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Source and target TableGroup must be different"


def test_split_returns_409_for_empty_physical_table_list(
    client: TestClient, db_session: Session
) -> None:
    table = seed_table(db_session, "API_T1")
    group = client.post(f"/tables/{table.id}/start-service").json()["id"]

    response = client.post(f"/table-groups/{group}/split", json={"physical_table_ids": []})
    assert response.status_code == 409
    assert response.json()["detail"] == "Split requires at least one PhysicalTable"


def test_switch_validation_returns_422_for_invalid_uuid(client: TestClient) -> None:
    response = client.post(
        f"/table-groups/{uuid4()}/switch",
        json={"from_table_id": "not-a-uuid", "to_table_id": "also-bad"},
    )
    assert response.status_code == 422


def test_merge_validation_returns_422_for_missing_field(client: TestClient) -> None:
    response = client.post("/table-groups/merge", json={"source_group_id": str(uuid4())})
    assert response.status_code == 422


def test_split_validation_returns_422_for_wrong_body_shape(client: TestClient) -> None:
    response = client.post(f"/table-groups/{uuid4()}/split", json={"tables": [str(uuid4())]})
    assert response.status_code == 422


def test_start_service_response_schema_contract(client: TestClient, db_session: Session) -> None:
    table = seed_table(db_session, "API_CONTRACT_START")

    response = client.post(f"/tables/{table.id}/start-service")
    assert response.status_code == 200
    payload = response.json()

    assert_table_group_payload_contract(payload, expected_state="OPEN", expect_closed_at_none=True)
    assert payload["physical_table_ids"] == [str(table.id)]


def test_get_group_response_schema_contract(client: TestClient, db_session: Session) -> None:
    table = seed_table(db_session, "API_CONTRACT_GROUP")
    group_id = client.post(f"/tables/{table.id}/start-service").json()["id"]

    response = client.get(f"/table-groups/{group_id}")
    assert response.status_code == 200
    payload = response.json()

    assert_table_group_payload_contract(payload, expected_state="OPEN", expect_closed_at_none=True)
    assert payload["id"] == group_id


def test_open_list_response_schema_contract(client: TestClient, db_session: Session) -> None:
    table_a = seed_table(db_session, "API_CONTRACT_OPEN_A")
    table_b = seed_table(db_session, "API_CONTRACT_OPEN_B")
    group_a = client.post(f"/tables/{table_a.id}/start-service").json()["id"]
    group_b = client.post(f"/tables/{table_b.id}/start-service").json()["id"]
    client.post(f"/table-groups/{group_b}/request-bill")

    response = client.get("/table-groups/open")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload

    found = {row["id"] for row in payload}
    assert group_a in found
    assert group_b in found

    for row in payload:
        assert_table_group_payload_contract(row, expect_closed_at_none=True)


def test_list_open_groups_returns_non_closed_content_in_order(
    client: TestClient, db_session: Session
) -> None:
    table_a = seed_table(db_session, "API_OPEN_1")
    table_b = seed_table(db_session, "API_OPEN_2")
    table_c = seed_table(db_session, "API_OPEN_3")

    group_open = client.post(f"/tables/{table_a.id}/start-service").json()["id"]
    group_bill_requested = client.post(f"/tables/{table_b.id}/start-service").json()["id"]
    group_closed = client.post(f"/tables/{table_c.id}/start-service").json()["id"]

    client.post(f"/table-groups/{group_bill_requested}/request-bill")
    client.post(f"/table-groups/{group_closed}/request-bill")
    client.post(f"/table-groups/{group_closed}/mark-paid")
    client.post(f"/table-groups/{group_closed}/close")

    response = client.get("/table-groups/open")
    assert response.status_code == 200
    payload = response.json()

    ids = [row["id"] for row in payload]
    assert group_open in ids
    assert group_bill_requested in ids
    assert group_closed not in ids

    for row in payload:
        assert set(row.keys()) == {"id", "state", "physical_table_ids", "opened_at", "closed_at"}
        assert row["state"] in {"OPEN", "BILL_REQUESTED", "PAID"}

    opened_at_values = [datetime.fromisoformat(row["opened_at"]) for row in payload]
    assert opened_at_values == sorted(opened_at_values)


def test_split_happy_path_returns_new_group_payload_and_updates_original(
    client: TestClient, db_session: Session
) -> None:
    table_a = seed_table(db_session, "API_SPLIT_1")
    table_b = seed_table(db_session, "API_SPLIT_2")
    table_c = seed_table(db_session, "API_SPLIT_3")

    source_group_id = client.post(f"/tables/{table_a.id}/start-service").json()["id"]
    client.post(
        f"/table-groups/{source_group_id}/tables/add",
        json={"physical_table_id": str(table_b.id)},
    )
    client.post(
        f"/table-groups/{source_group_id}/tables/add",
        json={"physical_table_id": str(table_c.id)},
    )

    split_response = client.post(
        f"/table-groups/{source_group_id}/split",
        json={"physical_table_ids": [str(table_b.id), str(table_c.id)]},
    )
    assert split_response.status_code == 200
    new_group = split_response.json()

    assert new_group["id"] != source_group_id
    assert new_group["state"] == "OPEN"
    assert set(new_group["physical_table_ids"]) == {str(table_b.id), str(table_c.id)}
    assert new_group["opened_at"] is not None
    assert new_group["closed_at"] is None

    source_response = client.get(f"/table-groups/{source_group_id}")
    assert source_response.status_code == 200
    source_group = source_response.json()
    assert source_group["state"] == "OPEN"
    assert source_group["physical_table_ids"] == [str(table_a.id)]
