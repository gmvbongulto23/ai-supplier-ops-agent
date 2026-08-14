from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import get_api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.service_name, version=settings.version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    app.include_router(get_api_router())
    return app


app = create_app()
