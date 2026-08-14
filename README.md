# AI Supplier Operations Agent

A supply-chain operations dashboard: tracks suppliers, orders, deliveries, and
inventory, and runs a lightweight rules-based agent that flags at-risk
inventory and delayed deliveries with actionable recommendations (e.g. switch
to a backup supplier, expedite an order).

FastAPI backend + React (Vite) frontend, in-memory demo data seeded on
startup.

## Structure

```
backend/    FastAPI app (app/), Alembic migrations, pytest tests
frontend/   React + TypeScript + Vite dashboard
Dockerfile  Bundles backend + frontend + Postgres into one deployable image
```

## Running locally

**Backend** — see [backend/README.md](backend/README.md) for full setup
(Postgres, migrations, tests). Quick start:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs at `http://127.0.0.1:8000/docs`.

**Frontend** — see [frontend/README.md](frontend/README.md). Quick start:

```bash
cd frontend
npm install
npm run dev
```

Dashboard at `http://127.0.0.1:5173`, routes to `/suppliers`, `/orders`,
`/deliveries`, `/inventory`, `/risks`, and `/recommendations`.

## Deployment

`Dockerfile` builds a single self-contained image (Postgres + backend +
frontend, frontend served as static files from the backend so both share one
origin/port). `entrypoint.sh` starts Postgres, runs migrations, then starts
the API.

```bash
docker build --platform linux/amd64 -t ai-supplier-ops-agent .
docker run -p 8000:8000 ai-supplier-ops-agent
```

This has been deployed as a [Daytona](https://daytona.io) sandbox for demo
purposes — ask if you need the current live URL.
