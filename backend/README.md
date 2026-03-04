# Backend

Sync FastAPI service using SQLAlchemy 2.0 and Alembic.

## Local setup (uv)
- `uv venv`
- `uv pip install -r` is not used; uv reads `pyproject.toml`
- `uv pip sync` to install dependencies

## Run
- `uvicorn app.main:app --reload`

## Database
- Copy `.env.example` to `.env` and set `DATABASE_URL`.
- `APP_ENV` is optional and defaults to `development`.
