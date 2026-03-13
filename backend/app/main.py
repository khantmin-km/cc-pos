# backend/app/main.py
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers import (
    menu_items,
    order_items,
    orders,
    physical_tables,
    sessions,
    table_groups,
    waiters,
)
from app.core.config import settings

app = FastAPI(title="CC Backend")

origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(physical_tables.router, prefix="/tables", tags=["tables"])
app.include_router(orders.router, prefix="/tables", tags=["orders"])
app.include_router(order_items.router, prefix="/order-items", tags=["order-items"])
app.include_router(table_groups.router, prefix="/table-groups", tags=["table-groups"])
app.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])
app.include_router(waiters.router, prefix="/waiters", tags=["waiters"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
