# backend/app/db/seed.py
"""Database seed script for initial menu items and tables."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.models.physical_table import PhysicalTable


def seed_menu_items(db: Session) -> None:
    """Seed initial menu items if database is empty."""
    # Check if we already have menu items
    existing = db.scalars(select(MenuItem)).first()
    if existing:
        print("Menu items already exist, skipping seed")
        return

    menu_items = [
        MenuItem(id=uuid4(), name="Fried Chicken with Ice-Cream", price=Decimal("1000"), status="AVAILABLE"),
        MenuItem(id=uuid4(), name="A Kyaw Sone", price=Decimal("2500"), status="AVAILABLE"),
        MenuItem(id=uuid4(), name="Tea Leaf Salad", price=Decimal("750"), status="AVAILABLE"),
        MenuItem(id=uuid4(), name="Fried Ice-Cream", price=Decimal("0"), status="AVAILABLE"),
        MenuItem(id=uuid4(), name="Mango Sticky Rice", price=Decimal("1200"), status="AVAILABLE"),
        MenuItem(id=uuid4(), name="Brownie with Vanilla Ice-Cream", price=Decimal("1500"), status="AVAILABLE"),
        MenuItem(id=uuid4(), name="Fresh Orange Juice", price=Decimal("800"), status="AVAILABLE"),
        MenuItem(id=uuid4(), name="Iced Latte", price=Decimal("1500"), status="AVAILABLE"),
        MenuItem(id=uuid4(), name="Green Tea", price=Decimal("500"), status="AVAILABLE"),
    ]

    for item in menu_items:
        db.add(item)

    db.commit()
    print(f"✓ Seeded {len(menu_items)} menu items")


def seed_physical_tables(db: Session) -> None:
    """Seed initial physical tables if database is empty."""
    # Check if we already have tables
    existing = db.scalars(select(PhysicalTable)).first()
    if existing:
        print("Physical tables already exist, skipping seed")
        return

    tables = [
        PhysicalTable(id=uuid4(), table_code="T-1"),
        PhysicalTable(id=uuid4(), table_code="T-2"),
        PhysicalTable(id=uuid4(), table_code="T-3"),
        PhysicalTable(id=uuid4(), table_code="T-4"),
        PhysicalTable(id=uuid4(), table_code="T-5"),
        PhysicalTable(id=uuid4(), table_code="T-6"),
        PhysicalTable(id=uuid4(), table_code="T-7"),
        PhysicalTable(id=uuid4(), table_code="T-8"),
    ]

    for table in tables:
        db.add(table)

    db.commit()
    print(f"✓ Seeded {len(tables)} physical tables")


def seed_database(db: Session) -> None:
    """Run all seed functions."""
    print("🌱 Seeding database...")
    try:
        seed_menu_items(db)
        seed_physical_tables(db)
        print("✓ Database seeding complete")
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        raise
