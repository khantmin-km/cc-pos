# Backend

Sync FastAPI service using SQLAlchemy 2.0 and Alembic.

## Local setup (uv)
- `uv venv`
- `uv pip install -r` is not used; uv reads `pyproject.toml`
- `uv pip sync` to install dependencies

## Run
- `uvicorn app.main:app --reload`
