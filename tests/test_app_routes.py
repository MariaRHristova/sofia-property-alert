from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint_reports_fixture_provider_status() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Bulgaria Property Alert"
    assert payload["provider"] == "fixture"
    assert payload["fixture_sample_count"] == 2
