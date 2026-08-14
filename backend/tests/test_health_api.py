from fastapi.testclient import TestClient

from app.api.health import get_readiness_checks
from app.main import create_app


def build_client() -> TestClient:
    return TestClient(create_app())


def test_liveness_returns_200_without_auth():
    client = build_client()
    response = client.get("/health/live")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "alive"
    assert body["service"]
    assert body["version"]


def test_readiness_returns_200_when_all_checks_pass():
    client = build_client()
    client.app.dependency_overrides[get_readiness_checks] = lambda: {"dummy": lambda: True}
    try:
        response = client.get("/health/ready")
    finally:
        client.app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["checks"] == {"dummy": "pass"}


def test_readiness_returns_503_with_reason_when_a_check_fails():
    client = build_client()
    client.app.dependency_overrides[get_readiness_checks] = lambda: {"database": lambda: False}
    try:
        response = client.get("/health/ready")
    finally:
        client.app.dependency_overrides.clear()
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"] == {"database": "fail"}


def test_readiness_returns_503_when_check_raises_exception():
    client = build_client()

    def _raising_check() -> bool:
        raise RuntimeError("dependency unavailable")

    client.app.dependency_overrides[get_readiness_checks] = lambda: {"database": _raising_check}
    try:
        response = client.get("/health/ready")
    finally:
        client.app.dependency_overrides.clear()
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"] == {"database": "fail"}
    assert "RuntimeError" not in response.text
