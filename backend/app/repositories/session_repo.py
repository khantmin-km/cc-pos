# backend/app/repositories/session_repo.py
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.user_session import UserSession


def create_session(
    db: Session,
    *,
    user_id: UUID,
    token: str,
    expires_at: datetime,
) -> UserSession:
    session = UserSession(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
    )
    db.add(session)
    db.flush()
    return session


def get_session_by_token(db: Session, token: str) -> UserSession | None:
    stmt = select(UserSession).where(UserSession.token == token)
    return db.scalar(stmt)


def revoke_session(db: Session, session_id: UUID, *, revoked_at: datetime) -> None:
    stmt = update(UserSession).where(UserSession.id == session_id).values(revoked_at=revoked_at)
    db.execute(stmt)
