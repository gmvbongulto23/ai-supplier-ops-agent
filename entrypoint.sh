#!/bin/bash
set -euo pipefail

service postgresql start

for i in $(seq 1 30); do
  if su postgres -c "pg_isready -q"; then
    break
  fi
  sleep 1
done

su postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='app'\"" | grep -q 1 \
  || su postgres -c "psql -c \"CREATE ROLE app WITH LOGIN PASSWORD 'app'\""

su postgres -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='supply_chain_ops'\"" | grep -q 1 \
  || su postgres -c "psql -c \"CREATE DATABASE supply_chain_ops OWNER app\""

export APP_DATABASE_URL="postgresql://app:app@localhost:5432/supply_chain_ops"

cd /app/backend
alembic upgrade head

exec uvicorn app.deploy_static:app --host 0.0.0.0 --port 8000
