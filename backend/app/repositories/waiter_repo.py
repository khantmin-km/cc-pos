# backend/app/repositories/waiter_repo.py
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.waiter import Waiter


def list_waiters(db: Session) -> list[Waiter]:
    stmt = select(Waiter).order_by(Waiter.created_at.asc(), Waiter.id.asc())
    return list(db.scalars(stmt))


def get_waiter(db: Session, waiter_id: UUID) -> Waiter | None:
    return db.get(Waiter, waiter_id)


def get_waiter_by_name(db: Session, name: str) -> Waiter | None:
    stmt = select(Waiter).where(Waiter.name == name)
    return db.scalar(stmt)


def create_waiter(db: Session, name: str) -> Waiter:
    waiter = Waiter(name=name, active=True)
    db.add(waiter)
    db.flush()
    return waiter


def set_waiter_active(db: Session, waiter_id: UUID, active: bool) -> None:
    stmt = update(Waiter).where(Waiter.id == waiter_id).values(active=active)
    db.execute(stmt)
