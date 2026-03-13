# backend/app/api/deps.py
from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.db.dependencies import get_db

def require_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    if x_admin_token is None or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin token required")


__all__ = ["get_db", "require_admin_token"]
