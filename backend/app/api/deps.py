# backend/app/api/deps.py
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services import auth_service
from app.services.errors import UnauthorizedError


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization required")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization required")
    try:
        return auth_service.get_user_for_token(db, token)
    except UnauthorizedError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def require_admin_user(user=Depends(get_current_user)):
    if user.role != auth_service.ROLE_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user


__all__ = ["get_db", "get_current_user", "require_admin_user"]
