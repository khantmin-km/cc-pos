# backend/app/main.py
from fastapi import FastAPI

app = FastAPI(title="CC Backend")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
