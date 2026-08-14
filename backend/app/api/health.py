import logging
from typing import Callable

from fastapi import APIRouter, Depends, Response, status

from app.core.config import Settings, get_settings
from app.schemas.health import HealthLiveResponse, HealthReadyResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

ReadinessCheck = Callable[[], bool]


def get_readiness_checks() -> dict[str, ReadinessCheck]:
    """In-process readiness checks. Empty until external dependencies
    (database, etc.) are wired in by later stories."""
    return {}


@router.get("/health/live", response_model=HealthLiveResponse)
def get_liveness(settings: Settings = Depends(get_settings)) -> HealthLiveResponse:
    return HealthLiveResponse(status="alive", service=settings.service_name, version=settings.version)


@router.get("/health/ready", response_model=HealthReadyResponse)
def get_readiness(
    response: Response,
    checks: dict[str, ReadinessCheck] = Depends(get_readiness_checks),
) -> HealthReadyResponse:
    results: dict[str, str] = {}
    all_passed = True

    for name, check in checks.items():
        try:
            passed = check()
        except Exception:
            logger.exception("Readiness check '%s' raised an exception", name)
            passed = False
        results[name] = "pass" if passed else "fail"
        if not passed:
            all_passed = False

    response.status_code = status.HTTP_200_OK if all_passed else status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthReadyResponse(status="ready" if all_passed else "not_ready", checks=results)
