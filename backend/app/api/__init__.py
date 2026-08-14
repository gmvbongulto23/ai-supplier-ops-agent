from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.ops import router as ops_router


def get_api_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(health_router)
    api_router.include_router(ops_router)
    return api_router
