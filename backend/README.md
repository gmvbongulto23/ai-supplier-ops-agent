# Backend

FastAPI application scaffold for the supply-chain ops demo.

## Local setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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
