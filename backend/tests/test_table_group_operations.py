# backend/tests/test_table_group_operations.py
from decimal import Decimal
import threading
import time
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.physical_table import PhysicalTable
from app.repositories import table_group_repo
from app.services import table_group_service
from app.services.errors import ConflictError, InvalidStateError, NotFoundError, SplitNotAllowedError


def seed_table(db: Session, table_code: str) -> PhysicalTable:
    table = PhysicalTable(id=uuid4(), table_code=table_code)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def seed_order_item(db: Session, table_group_id, physical_table_id) -> OrderItem:
    order = Order(table_group_id=table_group_id, state="CONFIRMED")
    db.add(order)
    db.flush()
    item = OrderItem(
        order_id=order.id,
        physical_table_id=physical_table_id,
        menu_item_id=None,
        menu_item_name_snap="Test Item",
        unit_price_snap=Decimal("10.00"),
        status="ACTIVE",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def test_start_service_creates_group_and_attaches_table(db_session: Session) -> None:
    table = seed_table(db_session, "T1")
    group_id = table_group_service.start_service(db_session, table.id)
    group = table_group_repo.get_table_group(db_session, group_id)
    assert group is not None
    assert group.state == "OPEN"
    table_ids = table_group_repo.list_physical_table_ids(db_session, group_id)
    assert table.id in table_ids


def test_start_service_rejects_assigned_table(db_session: Session) -> None:
    table = seed_table(db_session, "T1")
    table_group_service.start_service(db_session, table.id)
    with pytest.raises(ConflictError):
        table_group_service.start_service(db_session, table.id)


def test_attach_and_switch_table(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    group_id = table_group_service.start_service(db_session, table_a.id)

    table_group_service.attach_table(db_session, group_id, table_b.id)
    table_ids = set(table_group_repo.list_physical_table_ids(db_session, group_id))
    assert table_b.id in table_ids

    table_c = seed_table(db_session, "T3")
    table_group_service.switch_table(db_session, group_id, table_b.id, table_c.id)
    table_ids = set(table_group_repo.list_physical_table_ids(db_session, group_id))
    assert table_b.id not in table_ids
    assert table_c.id in table_ids


def test_merge_groups_closes_source(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    group_a = table_group_service.start_service(db_session, table_a.id)
    group_b = table_group_service.start_service(db_session, table_b.id)

    table_group_service.merge_groups(db_session, group_b, group_a)

    source = table_group_repo.get_table_group(db_session, group_b)
    target = table_group_repo.get_table_group(db_session, group_a)
    assert source is not None and source.state == "CLOSED"
    assert target is not None and target.state == "OPEN"
    table_ids = set(table_group_repo.list_physical_table_ids(db_session, group_a))
    assert table_a.id in table_ids
    assert table_b.id in table_ids


def test_request_bill_from_open_group(db_session: Session) -> None:
    table = seed_table(db_session, "T1")
    group_id = table_group_service.start_service(db_session, table.id)

    table_group_service.request_bill(db_session, group_id)

    group = table_group_repo.get_table_group(db_session, group_id)
    assert group is not None
    assert group.state == "BILL_REQUESTED"


def test_request_bill_rejects_non_open_group(db_session: Session) -> None:
    table = seed_table(db_session, "T1")
    group_id = table_group_service.start_service(db_session, table.id)
    table_group_service.request_bill(db_session, group_id)

    with pytest.raises(InvalidStateError):
        table_group_service.request_bill(db_session, group_id)


def test_mark_paid_rejects_non_bill_requested_group(db_session: Session) -> None:
    table = seed_table(db_session, "T1")
    group_id = table_group_service.start_service(db_session, table.id)

    with pytest.raises(InvalidStateError):
        table_group_service.mark_paid(db_session, group_id)


def test_close_group_releases_tables(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    group_id = table_group_service.start_service(db_session, table_a.id)
    table_group_service.attach_table(db_session, group_id, table_b.id)
    table_group_service.request_bill(db_session, group_id)
    table_group_service.mark_paid(db_session, group_id)
    table_group_service.close_group(db_session, group_id)

    group = table_group_repo.get_table_group(db_session, group_id)
    assert group is not None
    assert group.state == "CLOSED"
    assert table_group_repo.list_physical_table_ids(db_session, group_id) == []


def test_merge_rejects_non_open_groups(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    group_a = table_group_service.start_service(db_session, table_a.id)
    group_b = table_group_service.start_service(db_session, table_b.id)
    table_group_service.request_bill(db_session, group_b)

    with pytest.raises(InvalidStateError):
        table_group_service.merge_groups(db_session, group_b, group_a)


def test_attach_rejects_table_assigned_to_another_group(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    table_c = seed_table(db_session, "T3")
    group_a = table_group_service.start_service(db_session, table_a.id)
    group_b = table_group_service.start_service(db_session, table_b.id)

    table_group_service.attach_table(db_session, group_a, table_c.id)
    with pytest.raises(ConflictError):
        table_group_service.attach_table(db_session, group_b, table_c.id)


def test_close_group_rejects_non_paid_states(db_session: Session) -> None:
    table_open = seed_table(db_session, "T_OPEN")
    group_open = table_group_service.start_service(db_session, table_open.id)
    with pytest.raises(InvalidStateError):
        table_group_service.close_group(db_session, group_open)

    table_bill = seed_table(db_session, "T_BILL")
    group_bill = table_group_service.start_service(db_session, table_bill.id)
    table_group_service.request_bill(db_session, group_bill)
    with pytest.raises(InvalidStateError):
        table_group_service.close_group(db_session, group_bill)


def test_merge_rejects_same_group(db_session: Session) -> None:
    table = seed_table(db_session, "T1")
    group_id = table_group_service.start_service(db_session, table.id)

    with pytest.raises(ConflictError):
        table_group_service.merge_groups(db_session, group_id, group_id)


def test_switch_rejects_source_not_attached(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    table_c = seed_table(db_session, "T3")
    group_id = table_group_service.start_service(db_session, table_a.id)
    table_group_service.attach_table(db_session, group_id, table_b.id)

    with pytest.raises(ConflictError):
        table_group_service.switch_table(db_session, group_id, table_c.id, table_b.id)


def test_switch_rejects_missing_target_table(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    group_id = table_group_service.start_service(db_session, table_a.id)

    with pytest.raises(NotFoundError):
        table_group_service.switch_table(db_session, group_id, table_a.id, uuid4())

    table_ids = set(table_group_repo.list_physical_table_ids(db_session, group_id))
    assert table_a.id in table_ids
    assert table_b.id not in table_ids


def test_detach_rejects_unattached_table(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    group_id = table_group_service.start_service(db_session, table_a.id)

    with pytest.raises(ConflictError):
        table_group_service.detach_table(db_session, group_id, table_b.id)


def test_split_group_with_zero_items(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    group_id = table_group_service.start_service(db_session, table_a.id)
    table_group_service.attach_table(db_session, group_id, table_b.id)

    new_group_id = table_group_service.split_group(db_session, group_id, [table_b.id])
    new_tables = set(table_group_repo.list_physical_table_ids(db_session, new_group_id))
    assert table_b.id in new_tables


def test_split_group_rejects_when_order_items_exist(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    group_id = table_group_service.start_service(db_session, table_a.id)
    table_group_service.attach_table(db_session, group_id, table_b.id)
    seed_order_item(db_session, group_id, table_a.id)

    with pytest.raises(SplitNotAllowedError):
        table_group_service.split_group(db_session, group_id, [table_b.id])


@pytest.mark.parametrize("target_state", ["BILL_REQUESTED", "PAID", "CLOSED"])
def test_split_rejects_non_open_states(db_session: Session, target_state: str) -> None:
    table_a = seed_table(db_session, f"T1_{target_state}")
    table_b = seed_table(db_session, f"T2_{target_state}")
    group_id = table_group_service.start_service(db_session, table_a.id)
    table_group_service.attach_table(db_session, group_id, table_b.id)

    if target_state in {"BILL_REQUESTED", "PAID", "CLOSED"}:
        table_group_service.request_bill(db_session, group_id)
    if target_state in {"PAID", "CLOSED"}:
        table_group_service.mark_paid(db_session, group_id)
    if target_state == "CLOSED":
        table_group_service.close_group(db_session, group_id)

    with pytest.raises(InvalidStateError):
        table_group_service.split_group(db_session, group_id, [table_b.id])


def test_split_rejects_empty_target_list(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    group_id = table_group_service.start_service(db_session, table_a.id)

    with pytest.raises(ConflictError):
        table_group_service.split_group(db_session, group_id, [])


def test_split_rejects_table_not_in_group(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    group_id = table_group_service.start_service(db_session, table_a.id)

    with pytest.raises(ConflictError):
        table_group_service.split_group(db_session, group_id, [table_b.id])


def test_split_group_rejects_all_tables(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    group_id = table_group_service.start_service(db_session, table_a.id)

    with pytest.raises(ConflictError):
        table_group_service.split_group(db_session, group_id, [table_a.id])


def test_detach_rejects_last_table(db_session: Session) -> None:
    table = seed_table(db_session, "T1")
    group_id = table_group_service.start_service(db_session, table.id)

    with pytest.raises(ConflictError):
        table_group_service.detach_table(db_session, group_id, table.id)


def test_split_moves_only_selected_tables_and_keeps_original_open(db_session: Session) -> None:
    table_a = seed_table(db_session, "T1")
    table_b = seed_table(db_session, "T2")
    table_c = seed_table(db_session, "T3")
    group_id = table_group_service.start_service(db_session, table_a.id)
    table_group_service.attach_table(db_session, group_id, table_b.id)
    table_group_service.attach_table(db_session, group_id, table_c.id)

    new_group_id = table_group_service.split_group(db_session, group_id, [table_b.id])

    original_group = table_group_repo.get_table_group(db_session, group_id)
    new_group = table_group_repo.get_table_group(db_session, new_group_id)
    assert original_group is not None and original_group.state == "OPEN"
    assert new_group is not None and new_group.state == "OPEN"
    assert set(table_group_repo.list_physical_table_ids(db_session, group_id)) == {table_a.id, table_c.id}
    assert set(table_group_repo.list_physical_table_ids(db_session, new_group_id)) == {table_b.id}


def test_concurrent_attach_same_table_only_one_succeeds(engine) -> None:
    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrency lock test requires PostgreSQL")

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    with SessionLocal() as setup_db:
        table_a_id = uuid4()
        table_b_id = uuid4()
        table_c_id = uuid4()
        table_a = PhysicalTable(id=table_a_id, table_code="C_ATTACH_A")
        table_b = PhysicalTable(id=table_b_id, table_code="C_ATTACH_B")
        table_c = PhysicalTable(id=table_c_id, table_code="C_ATTACH_C")
        setup_db.add_all([table_a, table_b, table_c])
        setup_db.commit()

        group_a = table_group_service.start_service(setup_db, table_a_id)
        group_b = table_group_service.start_service(setup_db, table_b_id)

    barrier = threading.Barrier(2)
    results: list[str] = []
    lock = threading.Lock()

    def worker(target_group_id):
        with SessionLocal() as db:
            barrier.wait()
            try:
                table_group_service.attach_table(db, target_group_id, table_c_id)
                result = "ok"
            except Exception as exc:  # pragma: no cover - assertion checks outcome types
                result = type(exc).__name__
            with lock:
                results.append(result)

    t1 = threading.Thread(target=worker, args=(group_a,))
    t2 = threading.Thread(target=worker, args=(group_b,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert sorted(results) == ["ConflictError", "ok"]

    with SessionLocal() as verify_db:
        owner_group = table_group_repo.get_any_group_id_for_table(verify_db, table_c_id)
        assert owner_group in {group_a, group_b}


def test_concurrent_merge_waits_for_row_lock(engine) -> None:
    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrency lock test requires PostgreSQL")

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    with SessionLocal() as setup_db:
        table_a_id = uuid4()
        table_b_id = uuid4()
        table_a = PhysicalTable(id=table_a_id, table_code="C_MERGE_A")
        table_b = PhysicalTable(id=table_b_id, table_code="C_MERGE_B")
        setup_db.add_all([table_a, table_b])
        setup_db.commit()
        group_a = table_group_service.start_service(setup_db, table_a_id)
        group_b = table_group_service.start_service(setup_db, table_b_id)

    lock_acquired = threading.Event()

    def hold_lock():
        with SessionLocal() as db:
            tx = db.begin()
            db.execute(select(PhysicalTable).where(PhysicalTable.id == table_b_id).with_for_update())
            lock_acquired.set()
            time.sleep(0.5)
            tx.commit()

    holder = threading.Thread(target=hold_lock)
    holder.start()
    assert lock_acquired.wait(timeout=2)

    start = time.monotonic()
    with SessionLocal() as merge_db:
        table_group_service.merge_groups(merge_db, group_b, group_a)
    elapsed = time.monotonic() - start
    holder.join()

    assert elapsed >= 0.45

    with SessionLocal() as verify_db:
        source = table_group_repo.get_table_group(verify_db, group_b)
        target = table_group_repo.get_table_group(verify_db, group_a)
        assert source is not None and source.state == "CLOSED"
        assert target is not None and target.state == "OPEN"
