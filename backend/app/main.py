# backend/app/main.py
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routers import menu_items, order_items, orders, physical_tables, table_groups

app = FastAPI(title="CC Backend")

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(physical_tables.router, prefix="/tables", tags=["tables"])
app.include_router(orders.router, prefix="/tables", tags=["orders"])
app.include_router(order_items.router, prefix="/order-items", tags=["order-items"])
app.include_router(table_groups.router, prefix="/table-groups", tags=["table-groups"])
app.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
