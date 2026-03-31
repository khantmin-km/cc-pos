# backend/tests/test_billing_operations.py
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.physical_table import PhysicalTable
from app.models.user import User
from app.services import billing_service, table_group_service
from app.services.errors import ConflictError, InvalidStateError


def seed_table(db: Session, table_code: str) -> PhysicalTable:
    table = PhysicalTable(id=uuid4(), table_code=table_code)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def seed_order_item(db: Session, table_group_id, physical_table_id, price: str) -> OrderItem:
    order = Order(table_group_id=table_group_id, idempotency_key=str(uuid4()), state="CONFIRMED")
    db.add(order)
    db.flush()
    item = OrderItem(
        order_id=order.id,
        physical_table_id=physical_table_id,
        menu_item_id=None,
        menu_item_name_snap="Bill Item",
        unit_price_snap=Decimal(price),
        status="ACTIVE",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def seed_user(db: Session, username: str = "admin") -> User:
    user = User(id=uuid4(), username=username, pin_hash="x", role="ADMIN", active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_get_bill_breakdown_includes_totals_and_state(db_session: Session) -> None:
    table = seed_table(db_session, "B1")
    group_id = table_group_service.start_service(db_session, table.id)
    seed_order_item(db_session, group_id, table.id, "10.00")
    seed_order_item(db_session, group_id, table.id, "5.00")
    admin = seed_user(db_session)

    table_group_service.request_bill(db_session, group_id)
    billing_service.create_bill_adjustment(
        db_session,
        group_id,
        amount=Decimal("-2.00"),
        description="Customer complaint discount",
        reason="Cold food",
        actor=admin,
    )

    breakdown = billing_service.get_bill_breakdown(db_session, group_id)

    assert breakdown["table_group_state"] == "BILL_REQUESTED"
    assert breakdown["items_total"] == Decimal("15.00")
    assert breakdown["adjustments_total"] == Decimal("-2.00")
    assert breakdown["subtotal"] == Decimal("13.00")
    assert breakdown["tax_total"] == Decimal("0.91")
    assert breakdown["final_total"] == Decimal("13.91")


def test_create_adjustment_rejects_non_bill_requested(db_session: Session) -> None:
    table = seed_table(db_session, "B2")
    group_id = table_group_service.start_service(db_session, table.id)
    admin = seed_user(db_session)

    with pytest.raises(InvalidStateError):
        billing_service.create_bill_adjustment(
            db_session,
            group_id,
            amount=Decimal("1.00"),
            description="Manual charge",
            reason=None,
            actor=admin,
        )


def test_create_adjustment_rejects_negative_without_reason(db_session: Session) -> None:
    table = seed_table(db_session, "B3")
    group_id = table_group_service.start_service(db_session, table.id)
    table_group_service.request_bill(db_session, group_id)
    admin = seed_user(db_session)

    with pytest.raises(ConflictError):
        billing_service.create_bill_adjustment(
            db_session,
            group_id,
            amount=Decimal("-1.00"),
            description="Discount",
            reason=None,
            actor=admin,
        )


def test_create_adjustment_rejects_negative_subtotal(db_session: Session) -> None:
    table = seed_table(db_session, "B4")
    group_id = table_group_service.start_service(db_session, table.id)
    seed_order_item(db_session, group_id, table.id, "5.00")
    table_group_service.request_bill(db_session, group_id)
    admin = seed_user(db_session)

    with pytest.raises(ConflictError):
        billing_service.create_bill_adjustment(
            db_session,
            group_id,
            amount=Decimal("-6.00"),
            description="Waiver",
            reason="Mistake",
            actor=admin,
        )


def test_get_bill_allows_closed_group(db_session: Session) -> None:
    table = seed_table(db_session, "B5")
    group_id = table_group_service.start_service(db_session, table.id)
    seed_order_item(db_session, group_id, table.id, "7.00")
    table_group_service.request_bill(db_session, group_id)
    table_group_service.mark_paid(db_session, group_id)
    table_group_service.close_group(db_session, group_id)

    breakdown = billing_service.get_bill_breakdown(db_session, group_id)

    assert breakdown["table_group_state"] == "CLOSED"
    assert breakdown["items_total"] == Decimal("7.00")
