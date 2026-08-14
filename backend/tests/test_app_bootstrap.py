from app.core.config import Settings, get_settings
from app.main import create_app
from app.schemas.health import HealthLiveResponse, HealthReadyResponse


def test_get_settings_returns_safe_defaults(monkeypatch):
    monkeypatch.delenv("APP_SERVICE_NAME", raising=False)
    get_settings.cache_clear()
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.service_name
    assert settings.version
    get_settings.cache_clear()


def test_get_settings_reads_environment_overrides(monkeypatch):
    monkeypatch.setenv("APP_SERVICE_NAME", "custom-service")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.service_name == "custom-service"
    get_settings.cache_clear()


def test_create_app_registers_health_routes():
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/health/live" in paths
    assert "/health/ready" in paths


def test_create_app_exposes_openapi_schema():
    app = create_app()
    schema = app.openapi()
    assert schema["info"]["title"] == app.title
    assert "/health/live" in schema["paths"]
    assert "/health/ready" in schema["paths"]


def test_health_live_response_serializes_expected_fields():
    payload = HealthLiveResponse(status="alive", service="supply-chain-ops-api", version="0.1.0")
    assert payload.model_dump() == {
        "status": "alive",
        "service": "supply-chain-ops-api",
        "version": "0.1.0",
    }


def test_health_ready_response_serializes_checks_mapping():
    payload = HealthReadyResponse(status="not_ready", checks={"database": "fail"})
    assert payload.model_dump() == {
        "status": "not_ready",
        "checks": {"database": "fail"},
    }
