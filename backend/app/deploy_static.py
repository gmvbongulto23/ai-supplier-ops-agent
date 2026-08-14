from pathlib import Path

from fastapi.staticfiles import StaticFiles

from app.main import app

frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend_dist"
app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
