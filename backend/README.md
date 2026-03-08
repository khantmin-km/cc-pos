# Backend

Sync FastAPI service using SQLAlchemy 2.0 and Alembic.

## Local setup (uv)
- `uv venv`
- `uv pip install -r` is not used; uv reads `pyproject.toml`
- `uv pip sync` to install dependencies
- `uv pip sync --extra dev` for test dependencies
- No database configuration is required for local smoke testing; the app will
  automatically create and use a SQLite file at `backend/cc_pos.db` when
  `DATABASE_URL` is not provided. The schema and a small set of sample tables
  and table groups are seeded automatically the first time the server starts.

## Run
- `uvicorn app.main:app --reload`

## Tests
- Set `TEST_DATABASE_URL` (e.g., `postgresql+psycopg2://localhost:5432/cc_dev_test`)
- Run `uv run pytest`

## Database
- Copy `.env.example` to `.env` and set `DATABASE_URL` if you want to point to
  a different database (e.g., PostgreSQL). If omitted, the default SQLite file
  is used.
- `APP_ENV` is optional and defaults to `development`.
