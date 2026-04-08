#!/usr/bin/env python
"""
Seed demo physical tables for the POS system.
Creates 6 demo tables: Table1 through Table6
"""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app import models  # noqa: F401
from app.models.physical_table import PhysicalTable


def seed_tables(db: Session) -> None:
    """Create 6 demo physical tables."""
    
    for i in range(1, 7):
        table_code = f"Table{i}"
        
        # Check if table already exists
        existing = db.scalar(select(PhysicalTable).where(PhysicalTable.table_code == table_code))
        
        if existing:
            print(f"Table {table_code} already exists")
        else:
            print(f"Creating table: {table_code}")
            table = PhysicalTable(table_code=table_code)
            db.add(table)
    
    db.commit()


def main() -> None:
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required to seed tables")
    
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    
    with session_local() as db:
        seed_tables(db)
    
    print("\n✅ Seeded demo tables successfully!")
    for i in range(1, 7):
        print(f"- Table{i}")


if __name__ == "__main__":
    main()
