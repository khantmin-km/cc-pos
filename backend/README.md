# Backend

Sync FastAPI service using SQLAlchemy 2.0 and Alembic.

## Local setup (uv)
- `uv venv`
- `uv pip install -r` is not used; uv reads `pyproject.toml`
- `uv pip sync` to install dependencies
- `uv pip sync --extra dev` for test dependencies

## Run
- `uvicorn app.main:app --reload`

## Tests
- Set `TEST_DATABASE_URL` (e.g., `postgresql+psycopg2://localhost:5432/cc_dev_test`)
- Run `uv run pytest`

## Database
- Copy `.env.example` to `.env` and set `DATABASE_URL`.
- `APP_ENV` is optional and defaults to `development`.
