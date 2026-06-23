from __future__ import annotations

import re
from email import policy
from email.parser import Parser
from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app

PASSWORD = "correct horse battery staple"


def _preview_text_containing(fragment: str) -> str:
    preview_dir = Path(main_module.settings.email_preview_dir)
    files = sorted(preview_dir.glob("*.eml"), key=lambda path: path.stat().st_mtime)
    matches = [path for path in files if fragment in path.read_text(encoding="utf-8")]
    assert matches
    return matches[-1].read_text(encoding="utf-8")


def _extract_token(email_text: str, path_prefix: str) -> str:
    message = Parser(policy=policy.default).parsestr(email_text)
    body = message.get_body(preferencelist=("plain",))
    assert body is not None
    text = body.get_content()
    match = re.search(re.escape(path_prefix) + r"([^\s]+)", text)
    assert match
    return match.group(1)


def _register_login(client: TestClient, email: str) -> dict[str, str]:
    client.post(
        "/auth/register",
        data={"email": email, "password": PASSWORD},
        follow_redirects=False,
    )
    token = _extract_token(
        _preview_text_containing("/auth/verify?token="),
        "/auth/verify?token=",
    )
    client.get(f"/auth/verify?token={token}", follow_redirects=False)
    client.post(
        "/auth/login",
        data={"email": email, "password": PASSWORD},
        follow_redirects=False,
    )
    page = client.get("/")
    csrf = re.search(r'name="csrf-token" content="([^"]+)"', page.text)
    assert csrf
    return {"X-CSRF-Token": csrf.group(1)}


def test_scheduler_settings_can_be_saved_per_user() -> None:
    payload = {
        "enabled": True,
        "mode": "interval",
        "interval_minutes": 15,
        "daily_run_time": "08:30",
    }

    with TestClient(app) as client:
        headers = _register_login(client, "scheduler@example.com")
        response = client.post("/scheduler/settings", json=payload, headers=headers)
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
        headers = _register_login(client, "scheduler2@example.com")
        response = client.post("/scheduler/settings", json=payload, headers=headers)

    assert response.status_code == 422
    assert response.json()["errors"][0]["msg"] == (
        "Value error, Daily run time must be in HH:MM format."
    )
