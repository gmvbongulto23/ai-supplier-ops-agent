# Backend

FastAPI application scaffold for the supply-chain ops demo.

## Local setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Database

Requires a local PostgreSQL server. The app connects using `Settings.database_url`
(env var `APP_DATABASE_URL`), which defaults to `postgresql://localhost:5432/supply_chain_ops`.

```bash
createdb supply_chain_ops
createdb supply_chain_ops_test   # used by the migration integration tests
alembic upgrade head
```

## Run

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the generated OpenAPI documentation.

## Test

```bash
pytest
```

Migration integration tests in `tests/test_operational_migrations.py` run against
`supply_chain_ops_test` (override with the `TEST_DATABASE_URL` env var) and manage
their own schema via Alembic upgrade/downgrade — no manual setup needed beyond
`createdb supply_chain_ops_test`.
