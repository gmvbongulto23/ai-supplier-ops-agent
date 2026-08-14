from fastapi import APIRouter

from app.api.health import router as health_router


def get_api_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(health_router)
    return api_router
