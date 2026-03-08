# backend/app/main.py
from fastapi import FastAPI

from app.api.routers import physical_tables, table_groups

app = FastAPI(title="CC Backend")

app.include_router(physical_tables.router, prefix="/tables", tags=["tables"])
app.include_router(table_groups.router, prefix="/table-groups", tags=["table-groups"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
