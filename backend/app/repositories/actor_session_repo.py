# backend/app/repositories/actor_session_repo.py
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.actor_session import ActorSession


def get_session(db: Session, session_id: UUID) -> ActorSession | None:
    return db.get(ActorSession, session_id)


def create_session(
    db: Session,
    *,
    role: str,
    actor_name: str,
    waiter_id: UUID | None,
    expires_at: datetime,
) -> ActorSession:
    session = ActorSession(
        role=role,
        actor_name=actor_name,
        waiter_id=waiter_id,
        expires_at=expires_at,
    )
    db.add(session)
    db.flush()
    return session


def end_session(db: Session, session_id: UUID, *, ended_at: datetime) -> None:
    stmt = update(ActorSession).where(ActorSession.id == session_id).values(ended_at=ended_at)
    db.execute(stmt)


def end_sessions_for_waiter(db: Session, waiter_id: UUID, *, ended_at: datetime) -> None:
    stmt = (
        update(ActorSession)
        .where(ActorSession.waiter_id == waiter_id)
        .where(ActorSession.ended_at.is_(None))
        .values(ended_at=ended_at)
    )
    db.execute(stmt)


def get_active_session(db: Session, session_id: UUID) -> ActorSession | None:
    stmt = (
        select(ActorSession)
        .where(ActorSession.id == session_id)
        .where(ActorSession.ended_at.is_(None))
    )
    return db.scalar(stmt)
