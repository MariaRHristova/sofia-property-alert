from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_scheduler_settings_can_be_saved() -> None:
    payload = {
        "enabled": True,
        "mode": "interval",
        "interval_minutes": 15,
        "daily_run_time": "08:30",
    }

    with TestClient(app) as client:
        response = client.post("/scheduler/settings", json=payload)
        current = client.get("/scheduler/settings")

    assert response.status_code == 200
    assert response.json()["enabled"] is True
    assert response.json()["mode"] == "interval"
    assert response.json()["interval_minutes"] == 15
    assert current.status_code == 200
    assert current.json()["enabled"] is True
    assert current.json()["mode"] == "interval"
    assert current.json()["interval_minutes"] == 15
    assert current.json()["next_run_at"] is not None


def test_scheduler_settings_validate_daily_time() -> None:
    payload = {
        "enabled": True,
        "mode": "daily_time",
        "interval_minutes": 60,
        "daily_run_time": "25:61",
    }

    with TestClient(app) as client:
        response = client.post("/scheduler/settings", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"][0]["msg"] == (
        "Value error, Daily run time must be in HH:MM format."
    )
