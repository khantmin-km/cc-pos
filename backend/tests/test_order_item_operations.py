# backend/tests/test_order_item_operations.py
from decimal import Decimal
import threading
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_item_print_event import OrderItemPrintEvent
from app.models.order_item_serving import OrderItemServing
from app.models.physical_table import PhysicalTable
from app.services import order_item_service, table_group_service
from app.services.errors import ConflictError, InvalidStateError


def seed_active_order_item(
    db: Session,
    *,
    table_code: str = "OI_T1",
) -> tuple[UUID, UUID, UUID]:
    table = PhysicalTable(id=uuid4(), table_code=table_code)
    db.add(table)
    db.commit()
    db.refresh(table)

    group_id = table_group_service.start_service(db, table.id)
    order = Order(table_group_id=group_id, idempotency_key=str(uuid4()), state="CONFIRMED")
    db.add(order)
    db.flush()

    item = OrderItem(
        order_id=order.id,
        physical_table_id=table.id,
        menu_item_id=None,
        menu_item_name_snap="Soup",
        unit_price_snap=Decimal("7.50"),
        status="ACTIVE",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return group_id, table.id, item.id


def test_void_order_item_success_and_idempotent(db_session: Session) -> None:
    _, _, order_item_id = seed_active_order_item(db_session)

    order_item_service.void_order_item(db_session, order_item_id)
    order_item_service.void_order_item(db_session, order_item_id)

    item = db_session.get(OrderItem, order_item_id)
    assert item is not None
    assert item.status == "VOIDED"
    assert item.voided_at is not None


def test_void_order_item_rejects_non_open_group(db_session: Session) -> None:
    group_id, _, order_item_id = seed_active_order_item(db_session)
    table_group_service.request_bill(db_session, group_id)

    with pytest.raises(InvalidStateError):
        order_item_service.void_order_item(db_session, order_item_id)


def test_void_order_item_rejects_served_item(db_session: Session) -> None:
    _, _, order_item_id = seed_active_order_item(db_session)
    order_item_service.mark_order_item_served(db_session, order_item_id)

    with pytest.raises(ConflictError):
        order_item_service.void_order_item(db_session, order_item_id)


def test_mark_served_success_and_idempotent(db_session: Session) -> None:
    _, _, order_item_id = seed_active_order_item(db_session)

    order_item_service.mark_order_item_served(db_session, order_item_id)
    order_item_service.mark_order_item_served(db_session, order_item_id)

    serving_count = db_session.scalar(
        select(func.count(OrderItemServing.order_item_id)).where(
            OrderItemServing.order_item_id == order_item_id
        )
    )
    assert int(serving_count or 0) == 1


def test_mark_served_rejects_voided_item(db_session: Session) -> None:
    _, _, order_item_id = seed_active_order_item(db_session)
    order_item_service.void_order_item(db_session, order_item_id)

    with pytest.raises(ConflictError):
        order_item_service.mark_order_item_served(db_session, order_item_id)


def test_mark_served_rejects_non_open_group(db_session: Session) -> None:
    group_id, _, order_item_id = seed_active_order_item(db_session)
    table_group_service.request_bill(db_session, group_id)

    with pytest.raises(InvalidStateError):
        order_item_service.mark_order_item_served(db_session, order_item_id)


def test_reprint_active_creates_duplicate_print_event(db_session: Session) -> None:
    _, _, order_item_id = seed_active_order_item(db_session)

    order_item_service.reprint_order_item(db_session, order_item_id)

    duplicate_count = db_session.scalar(
        select(func.count(OrderItemPrintEvent.order_item_id))
        .where(OrderItemPrintEvent.order_item_id == order_item_id)
        .where(OrderItemPrintEvent.print_type == "DUPLICATE")
    )
    assert int(duplicate_count or 0) == 1


def test_reprint_allows_closed_group_for_active_item(db_session: Session) -> None:
    group_id, _, order_item_id = seed_active_order_item(db_session)
    table_group_service.request_bill(db_session, group_id)
    table_group_service.mark_paid(db_session, group_id)
    table_group_service.close_group(db_session, group_id)

    order_item_service.reprint_order_item(db_session, order_item_id)

    duplicate_count = db_session.scalar(
        select(func.count(OrderItemPrintEvent.order_item_id))
        .where(OrderItemPrintEvent.order_item_id == order_item_id)
        .where(OrderItemPrintEvent.print_type == "DUPLICATE")
    )
    assert int(duplicate_count or 0) == 1


def test_reprint_rejects_voided_item(db_session: Session) -> None:
    _, _, order_item_id = seed_active_order_item(db_session)
    order_item_service.void_order_item(db_session, order_item_id)

    with pytest.raises(ConflictError):
        order_item_service.reprint_order_item(db_session, order_item_id)


def test_concurrent_void_same_item_is_retry_safe(engine) -> None:
    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrency lock test requires PostgreSQL")

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    with SessionLocal() as setup_db:
        _, _, order_item_id = seed_active_order_item(
            setup_db,
            table_code="OI_CONCURRENT",
        )

    barrier = threading.Barrier(2)
    results: list[str] = []
    lock = threading.Lock()

    def worker() -> None:
        with SessionLocal() as db:
            barrier.wait()
            try:
                order_item_service.void_order_item(db, order_item_id)
                outcome = "ok"
            except Exception as exc:  # pragma: no cover - asserted by outcome list
                outcome = type(exc).__name__
            with lock:
                results.append(outcome)

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert sorted(results) == ["ok", "ok"]

    with SessionLocal() as verify_db:
        item = verify_db.get(OrderItem, order_item_id)
        assert item is not None
        assert item.status == "VOIDED"
