# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import menu_items, order_items, orders, physical_tables, table_groups

app = FastAPI(title="CC Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(physical_tables.router, prefix="/tables", tags=["tables"])
app.include_router(orders.router, prefix="/tables", tags=["orders"])
app.include_router(order_items.router, prefix="/order-items", tags=["order-items"])
app.include_router(table_groups.router, prefix="/table-groups", tags=["table-groups"])
app.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
