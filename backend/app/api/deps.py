# backend/app/api/deps.py
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.dependencies import get_db
from app.services import actor_session_service
from app.services.errors import ConflictError, NotFoundError

def require_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    if x_admin_token is None or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin token required")


def require_actor_session(
    x_actor_session: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not x_actor_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Actor session required")
    try:
        session_id = UUID(x_actor_session)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid actor session") from exc
    try:
        return actor_session_service.get_valid_session(db, session_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def require_admin_session(
    session=Depends(require_actor_session),
):
    if session.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin session required")
    return session


__all__ = ["get_db", "require_admin_token", "require_actor_session", "require_admin_session"]
