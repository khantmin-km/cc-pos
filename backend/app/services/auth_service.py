# backend/app/services/auth_service.py
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories import session_repo, user_repo
from app.services.errors import UnauthorizedError
from app.services.transaction import transactional


ROLE_ADMIN = "ADMIN"
ROLE_WAITER = "WAITER"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def hash_pin(pin: str) -> str:
    return pbkdf2_sha256.hash(pin)


def verify_pin(pin: str, pin_hash: str) -> bool:
    return pbkdf2_sha256.verify(pin, pin_hash)


def login(db: Session, *, username: str, pin: str):
    with transactional(db):
        user = user_repo.get_user_by_username(db, username)
        if not user or not user.active:
            raise UnauthorizedError("Invalid credentials")
        if not verify_pin(pin, user.pin_hash):
            raise UnauthorizedError("Invalid credentials")

        token = str(uuid4())
        expires_at = _now_utc() + timedelta(hours=settings.session_ttl_hours)
        session = session_repo.create_session(db, user_id=user.id, token=token, expires_at=expires_at)
        return user, session


def get_user_for_token(db: Session, token: str):
    session = session_repo.get_session_by_token(db, token)
    if not session:
        raise UnauthorizedError("Invalid session")
    if session.revoked_at is not None:
        raise UnauthorizedError("Session revoked")
    if session.expires_at <= _now_utc():
        raise UnauthorizedError("Session expired")
    user = user_repo.get_user(db, session.user_id)
    if not user or not user.active:
        raise UnauthorizedError("User inactive")
    return user
