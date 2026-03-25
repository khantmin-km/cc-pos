# backend/app/repositories/user_repo.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user(db: Session, user_id: UUID) -> User | None:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    return db.scalar(stmt)


def create_user(db: Session, *, username: str, pin_hash: str, role: str) -> User:
    user = User(username=username, pin_hash=pin_hash, role=role, active=True)
    db.add(user)
    db.flush()
    return user
