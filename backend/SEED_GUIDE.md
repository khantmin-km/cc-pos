# Backend Database Seeding Guide

## Automatic Seeding (Development)

When running the backend in **development mode** (`APP_ENV=development`), the database is automatically seeded on startup with:

- **9 Menu Items**: Sample restaurant menu items with prices
- **8 Physical Tables**: Table numbers T-1 through T-8

The seeding is **idempotent** — it checks if data already exists and skips seeding if found.

### Setup

1. **Create `.env` file** in the backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost/ccpos_db
APP_ENV=development
```

2. **Run migrations**:

```bash
cd backend
alembic upgrade head
```

3. **Start the backend** (seeding happens automatically):

```bash
python -m uvicorn app.main:app --reload
```

## Manual Seeding

If you want to reseed the database manually:

```bash
cd backend
python seed_db.py
```

## Menu Items Seeded

| Name | Price | Status |
|------|-------|--------|
| Fried Chicken with Ice-Cream | 1000 | AVAILABLE |
| A Kyaw Sone | 2500 | AVAILABLE |
| Tea Leaf Salad | 750 | AVAILABLE |
| Fried Ice-Cream | 0 | AVAILABLE |
| Mango Sticky Rice | 1200 | AVAILABLE |
| Brownie with Vanilla Ice-Cream | 1500 | AVAILABLE |
| Fresh Orange Juice | 800 | AVAILABLE |
| Iced Latte | 1500 | AVAILABLE |
| Green Tea | 500 | AVAILABLE |

## Physical Tables Seeded

15 tables with codes: **T-1** through **T-8**

## Verify Seeding

Check the database:

```bash
# List menu items
curl http://localhost:8000/menu-items

# List tables
curl http://localhost:8000/tables
```

Both should return data if seeding was successful.
