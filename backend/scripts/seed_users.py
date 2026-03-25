# backend/scripts/seed_users.py
import argparse
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app import models  # noqa: F401
from app.repositories import user_repo
from app.services import auth_service


@dataclass
class SeedUser:
    username: str
    pin: str
    role: str


def _parse_user(value: str) -> SeedUser:
    parts = value.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("User must be in 'username:pin:role' format")
    username, pin, role = [p.strip() for p in parts]
    role = role.upper()
    if role not in {auth_service.ROLE_ADMIN, auth_service.ROLE_WAITER}:
        raise argparse.ArgumentTypeError("Role must be ADMIN or WAITER")
    if not username or not pin:
        raise argparse.ArgumentTypeError("Username and pin are required")
    return SeedUser(username=username, pin=pin, role=role)


def seed_users(db: Session, users: list[SeedUser]) -> None:
    for user in users:
        existing = user_repo.get_user_by_username(db, user.username)
        pin_hash = auth_service.hash_pin(user.pin)
        if existing:
            existing.pin_hash = pin_hash
            existing.role = user.role
            existing.active = True
        else:
            user_repo.create_user(
                db,
                username=user.username,
                pin_hash=pin_hash,
                role=user.role,
            )
    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed users for local development.")
    parser.add_argument(
        "--user",
        action="append",
        type=_parse_user,
        help="User in username:pin:role format. Can be repeated.",
    )
    args = parser.parse_args()

    users = args.user or [
        SeedUser("admin", "1234", auth_service.ROLE_ADMIN),
        SeedUser("waiter1", "1111", auth_service.ROLE_WAITER),
        SeedUser("waiter2", "2222", auth_service.ROLE_WAITER),
        SeedUser("waiter3", "3333", auth_service.ROLE_WAITER),
    ]

    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required to seed users")

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with session_local() as db:
        seed_users(db, users)

    print("Seeded users:")
    for user in users:
        print(f"- {user.username} ({user.role})")


if __name__ == "__main__":
    main()
