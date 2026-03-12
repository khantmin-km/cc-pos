#!/usr/bin/env python3
# backend/seed_db.py
"""Script to seed the database with initial data."""

import sys

from app.db.session import SessionLocal
from app.db.seed import seed_database


def main() -> int:
    """Run database seeding."""
    try:
        db = SessionLocal()
        seed_database(db)
        db.close()
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
