# backend/app/services/waiter_service.py
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import actor_session_repo, waiter_repo
from app.services.errors import ConflictError, NotFoundError
from app.services.transaction import transactional


def list_waiters(db: Session):
    return waiter_repo.list_waiters(db)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_waiter(db: Session, name: str):
    with transactional(db):
        existing = waiter_repo.get_waiter_by_name(db, name)
        if existing:
            raise ConflictError("Waiter name already exists")
        return waiter_repo.create_waiter(db, name=name)


def update_waiter(db: Session, waiter_id: UUID, *, name: str | None, active: bool | None):
    with transactional(db):
        waiter = waiter_repo.get_waiter(db, waiter_id)
        if not waiter:
            raise NotFoundError("Waiter not found")

        if name is not None and name != waiter.name:
            existing = waiter_repo.get_waiter_by_name(db, name)
            if existing:
                raise ConflictError("Waiter name already exists")
            waiter.name = name

        if active is not None:
            waiter.active = active
            if active is False:
                actor_session_repo.end_sessions_for_waiter(db, waiter_id, ended_at=_now_utc())

        db.flush()
        return waiter
