from fastapi import FastAPI

from app.api import get_api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.service_name, version=settings.version)
    app.include_router(get_api_router())
    return app


app = create_app()
