# backend/app/services/table_group_service.py
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import physical_table_repo, table_group_repo
from app.services.errors import ConflictError, InvalidStateError, NotFoundError, SplitNotAllowedError
from app.services.transaction import transactional


OPEN = "OPEN"
BILL_REQUESTED = "BILL_REQUESTED"
PAID = "PAID"
CLOSED = "CLOSED"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def start_service(db: Session, physical_table_id: UUID) -> UUID:
    with transactional(db):
        physical_table_repo.lock_tables(db, [physical_table_id])
        table = physical_table_repo.get_table(db, physical_table_id)
        if not table:
            raise NotFoundError("PhysicalTable not found")

        existing_group = table_group_repo.get_any_group_id_for_table(db, physical_table_id)
        if existing_group is not None:
            raise ConflictError("PhysicalTable is already assigned to a TableGroup")

        group = table_group_repo.create_table_group(db, state=OPEN)
        physical_table_repo.attach_table(db, group.id, physical_table_id)
        return group.id


def list_open_groups(db: Session) -> list[tuple[UUID, str, list[UUID], datetime, datetime | None]]:
    groups = table_group_repo.list_open_table_groups(db)
    results: list[tuple[UUID, str, list[UUID], datetime, datetime | None]] = []
    for group in groups:
        table_ids = table_group_repo.list_physical_table_ids(db, group.id)
        results.append((group.id, group.state, table_ids, group.opened_at, group.closed_at))
    return results


def get_group(db: Session, table_group_id: UUID) -> tuple[UUID, str, list[UUID], datetime, datetime | None]:
    group = table_group_repo.get_table_group(db, table_group_id)
    if not group:
        raise NotFoundError("TableGroup not found")
    table_ids = table_group_repo.list_physical_table_ids(db, group.id)
    return group.id, group.state, table_ids, group.opened_at, group.closed_at


def request_bill(db: Session, table_group_id: UUID) -> None:
    with transactional(db):
        group = table_group_repo.get_table_group(db, table_group_id)
        if not group:
            raise NotFoundError("TableGroup not found")
        if group.state != OPEN:
            raise InvalidStateError("TableGroup must be OPEN to request bill")
        table_group_repo.update_state(db, table_group_id, BILL_REQUESTED)


def mark_paid(db: Session, table_group_id: UUID) -> None:
    with transactional(db):
        group = table_group_repo.get_table_group(db, table_group_id)
        if not group:
            raise NotFoundError("TableGroup not found")
        if group.state != BILL_REQUESTED:
            raise InvalidStateError("TableGroup must be BILL_REQUESTED to mark paid")
        table_group_repo.update_state(db, table_group_id, PAID)


def close_group(db: Session, table_group_id: UUID) -> None:
    with transactional(db):
        group = table_group_repo.get_table_group(db, table_group_id)
        if not group:
            raise NotFoundError("TableGroup not found")
        if group.state != PAID:
            raise InvalidStateError("TableGroup must be PAID to close")
        table_group_repo.update_state(db, table_group_id, CLOSED)
        table_ids = table_group_repo.list_physical_table_ids(db, table_group_id)
        table_group_repo.delete_group_tables(db, table_group_id, table_ids)
        group.closed_at = _now_utc()


def attach_table(db: Session, table_group_id: UUID, physical_table_id: UUID) -> None:
    with transactional(db):
        physical_table_repo.lock_tables(db, [physical_table_id])
        group = table_group_repo.get_table_group(db, table_group_id)
        if not group:
            raise NotFoundError("TableGroup not found")
        if group.state != OPEN:
            raise InvalidStateError("TableGroup must be OPEN to attach table")
        if not physical_table_repo.get_table(db, physical_table_id):
            raise NotFoundError("PhysicalTable not found")
        if table_group_repo.get_any_group_id_for_table(db, physical_table_id) is not None:
            raise ConflictError("PhysicalTable is already assigned to a TableGroup")
        physical_table_repo.attach_table(db, table_group_id, physical_table_id)


def detach_table(db: Session, table_group_id: UUID, physical_table_id: UUID) -> None:
    with transactional(db):
        physical_table_repo.lock_tables(db, [physical_table_id])
        group = table_group_repo.get_table_group(db, table_group_id)
        if not group:
            raise NotFoundError("TableGroup not found")
        if group.state != OPEN:
            raise InvalidStateError("TableGroup must be OPEN to detach table")
        table_ids = table_group_repo.list_physical_table_ids(db, table_group_id)
        if physical_table_id not in table_ids:
            raise ConflictError("PhysicalTable is not attached to this TableGroup")
        if len(table_ids) <= 1:
            raise ConflictError("Cannot detach the last table from a TableGroup")
        physical_table_repo.detach_table(db, table_group_id, physical_table_id)


def switch_table(db: Session, table_group_id: UUID, from_table_id: UUID, to_table_id: UUID) -> None:
    with transactional(db):
        physical_table_repo.lock_tables(db, sorted([from_table_id, to_table_id]))
        group = table_group_repo.get_table_group(db, table_group_id)
        if not group:
            raise NotFoundError("TableGroup not found")
        if group.state != OPEN:
            raise InvalidStateError("TableGroup must be OPEN to switch tables")

        table_ids = table_group_repo.list_physical_table_ids(db, table_group_id)
        if from_table_id not in table_ids:
            raise ConflictError("Source table is not attached to this TableGroup")
        if not physical_table_repo.get_table(db, to_table_id):
            raise NotFoundError("Target table not found")
        if table_group_repo.get_any_group_id_for_table(db, to_table_id) is not None:
            raise ConflictError("Target table is already assigned to a TableGroup")

        physical_table_repo.detach_table(db, table_group_id, from_table_id)
        physical_table_repo.attach_table(db, table_group_id, to_table_id)


def merge_groups(db: Session, source_group_id: UUID, target_group_id: UUID) -> None:
    if source_group_id == target_group_id:
        raise ConflictError("Source and target TableGroup must be different")
    with transactional(db):
        group_source = table_group_repo.get_table_group(db, source_group_id)
        group_target = table_group_repo.get_table_group(db, target_group_id)
        if not group_source or not group_target:
            raise NotFoundError("TableGroup not found")
        if group_source.state != OPEN or group_target.state != OPEN:
            raise InvalidStateError("Both TableGroups must be OPEN to merge")

        source_tables = table_group_repo.list_physical_table_ids(db, source_group_id)
        target_tables = table_group_repo.list_physical_table_ids(db, target_group_id)
        physical_table_repo.lock_tables(db, sorted(source_tables + target_tables))

        table_group_repo.move_tables(db, source_group_id, target_group_id)
        table_group_repo.update_state(db, source_group_id, CLOSED)
        group_source.closed_at = _now_utc()


def split_group(db: Session, table_group_id: UUID, new_group_table_ids: list[UUID]) -> UUID:
    if not new_group_table_ids:
        raise ConflictError("Split requires at least one PhysicalTable")

    with transactional(db):
        group = table_group_repo.get_table_group(db, table_group_id)
        if not group:
            raise NotFoundError("TableGroup not found")
        if group.state != OPEN:
            raise InvalidStateError("TableGroup must be OPEN to split")

        current_tables = table_group_repo.list_physical_table_ids(db, table_group_id)
        if not set(new_group_table_ids).issubset(set(current_tables)):
            raise ConflictError("Split tables must belong to the TableGroup")
        if len(current_tables) == len(new_group_table_ids):
            raise ConflictError("Split cannot move all tables")

        physical_table_repo.lock_tables(db, sorted(current_tables))

        item_count = table_group_repo.count_order_items(db, table_group_id)
        if item_count > 0:
            raise SplitNotAllowedError("Split is allowed only when the TableGroup has zero OrderItems")

        new_group = table_group_repo.create_table_group(db, state=OPEN)
        table_group_repo.delete_group_tables(db, table_group_id, new_group_table_ids)
        for table_id in new_group_table_ids:
            physical_table_repo.attach_table(db, new_group.id, table_id)

        return new_group.id
