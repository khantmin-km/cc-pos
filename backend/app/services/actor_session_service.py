# backend/app/services/actor_session_service.py
from datetime import datetime, timedelta, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories import actor_session_repo, waiter_repo
from app.services.errors import ConflictError, NotFoundError
from app.services.transaction import transactional


WAITER = "WAITER"
ADMIN = "ADMIN"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _compute_expiry(now_utc: datetime) -> datetime:
    tz = ZoneInfo(settings.session_timezone)
    local_now = now_utc.astimezone(tz)
    hour, minute = [int(part) for part in settings.session_close_time.split(":")]
    close_dt = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if local_now >= close_dt:
        close_dt += timedelta(days=1)
    expiry_local = close_dt + timedelta(minutes=settings.session_grace_minutes)
    return expiry_local.astimezone(timezone.utc)


def create_waiter_session(db: Session, waiter_id: UUID):
    with transactional(db):
        waiter = waiter_repo.get_waiter(db, waiter_id)
        if not waiter:
            raise NotFoundError("Waiter not found")
        if not waiter.active:
            raise ConflictError("Waiter is inactive")

        expires_at = _compute_expiry(_now_utc())
        return actor_session_repo.create_session(
            db,
            role=WAITER,
            actor_name=waiter.name,
            waiter_id=waiter.id,
            expires_at=expires_at,
        )


def create_admin_session(db: Session, actor_name: str | None = None):
    with transactional(db):
        expires_at = _compute_expiry(_now_utc())
        name = actor_name or "admin"
        return actor_session_repo.create_session(
            db,
            role=ADMIN,
            actor_name=name,
            waiter_id=None,
            expires_at=expires_at,
        )


def end_session(db: Session, session_id: UUID) -> None:
    with transactional(db):
        session = actor_session_repo.get_session(db, session_id)
        if not session:
            raise NotFoundError("Session not found")
        if session.ended_at is not None:
            return
        actor_session_repo.end_session(db, session_id, ended_at=_now_utc())


def get_valid_session(db: Session, session_id: UUID):
    session = actor_session_repo.get_active_session(db, session_id)
    if not session:
        raise NotFoundError("Session not found")
    if session.ended_at is not None:
        raise ConflictError("Session has ended")
    if session.expires_at <= _now_utc():
        raise ConflictError("Session expired")
    if session.waiter_id is not None:
        waiter = waiter_repo.get_waiter(db, session.waiter_id)
        if not waiter or not waiter.active:
            raise ConflictError("Waiter is inactive")
    return session
