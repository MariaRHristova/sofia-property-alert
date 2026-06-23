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


def register_and_verify(client: TestClient, email: str) -> None:
    response = client.post(
        "/auth/register",
        data={"email": email, "password": PASSWORD},
        follow_redirects=False,
    )
    assert response.status_code == 303
    token = _extract_token(
        _preview_text_containing("/auth/verify?token="),
        "/auth/verify?token=",
    )
    verify_response = client.get(f"/auth/verify?token={token}", follow_redirects=False)
    assert verify_response.status_code == 303


def login(client: TestClient, email: str, password: str = PASSWORD) -> None:
    response = client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )
    assert response.status_code == 303


def csrf_token(client: TestClient) -> str:
    page = client.get("/")
    match = re.search(r'name="csrf-token" content="([^"]+)"', page.text)
    assert match
    return match.group(1)


def auth_headers(client: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": csrf_token(client)}


def test_health_endpoint_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_for_signed_out_user_renders_auth_sections() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        stylesheet_response = client.get("/static/app.css")

    assert response.status_code == 200
    assert "Create your account" in response.text
    assert "Log in" in response.text
    assert "Reset password" in response.text
    assert stylesheet_response.status_code == 200
    assert "--blue: #1597c7" in stylesheet_response.text
    assert ".auth-grid" in stylesheet_response.text


def test_create_subscription_requires_authenticated_user() -> None:
    payload = {
        "transaction_type": "sale",
        "property_type": "apartment",
        "city": "Sofia",
        "districts": ["Lozenets"],
    }

    with TestClient(app) as client:
        response = client.post("/subscriptions", json=payload)

    assert response.status_code == 401
    assert response.json()["error"] == "Sign in to continue."


def test_registration_verification_login_and_dashboard_flow() -> None:
    with TestClient(app) as client:
        register_and_verify(client, "reader@example.com")
        login(client, "reader@example.com")
        page = client.get("/")

    assert page.status_code == 200
    assert "reader@example.com" in page.text
    assert "Your scheduler" in page.text
    assert "Delivery email" in page.text
    assert "autocomplete=\"email\" readonly" in page.text


def test_authenticated_user_can_create_reactivate_and_delete_subscription() -> None:
    payload = {
        "transaction_type": "sale",
        "property_type": "apartment",
        "city": "Sofia",
        "districts": ["Lozenets"],
        "min_price_eur": 200000,
        "max_price_eur": 300000,
        "rooms": "2",
        "min_area_sqm": 70,
    }

    with TestClient(app) as client:
        register_and_verify(client, "owner@example.com")
        login(client, "owner@example.com")
        headers = auth_headers(client)
        create_response = client.post("/subscriptions", json=payload, headers=headers)
        unsubscribe_url = create_response.json()["unsubscribe_url"]
        unsubscribe_response = client.post(unsubscribe_url, headers=headers)
        page_response = client.get("/")
        subscribe_response = client.post(
            unsubscribe_url.replace("/unsubscribe", "/subscribe"),
            headers=headers,
        )
        delete_response = client.request(
            "DELETE",
            unsubscribe_url.replace("/unsubscribe", ""),
            headers=headers,
        )

    assert create_response.status_code == 201
    assert create_response.json()["email"] == "owner@example.com"
    assert create_response.json()["preview_match_count"] == 1
    assert unsubscribe_response.status_code == 200
    assert "Subscribe again" in page_response.text
    assert subscribe_response.status_code == 200
    assert subscribe_response.json()["preview_match_count"] == 1
    assert delete_response.status_code == 200


def test_manual_job_and_scheduler_settings_are_scoped_per_user(monkeypatch) -> None:
    monkeypatch.setattr(main_module.settings, "email_backend", "preview")
    payload = {
        "transaction_type": "sale",
        "property_type": "apartment",
        "city": "Sofia",
        "districts": ["Lozenets"],
        "min_price_eur": 200000,
        "max_price_eur": 300000,
        "rooms": "2",
        "min_area_sqm": 70,
    }

    with TestClient(app) as user_one:
        register_and_verify(user_one, "first@example.com")
        login(user_one, "first@example.com")
        one_headers = auth_headers(user_one)
        user_one.post("/subscriptions", json=payload, headers=one_headers)
        scheduler_response = user_one.post(
            "/scheduler/settings",
            json={
                "enabled": True,
                "mode": "interval",
                "interval_minutes": 15,
                "daily_run_time": "08:30",
            },
            headers=one_headers,
        )
        job_response = user_one.post("/jobs/run", headers=one_headers)

    with TestClient(app) as user_two:
        register_and_verify(user_two, "second@example.com")
        login(user_two, "second@example.com")
        scheduler_current = user_two.get("/scheduler/settings")
        recent_jobs = user_two.get("/jobs/recent")
        dashboard = user_two.get("/")

    assert scheduler_response.status_code == 200
    assert scheduler_response.json()["enabled"] is True
    assert scheduler_response.json()["interval_minutes"] == 15
    assert job_response.status_code == 200
    assert job_response.json()["active_subscriptions"] == 1
    assert scheduler_current.status_code == 200
    assert scheduler_current.json()["enabled"] is False
    assert recent_jobs.status_code == 200
    assert recent_jobs.json()["jobs"] == []
    assert "first@example.com" not in dashboard.text


def test_password_reset_preview_allows_setting_new_password() -> None:
    with TestClient(app) as client:
        register_and_verify(client, "reset@example.com")
        request_response = client.post(
            "/auth/password/request",
            data={"email": "reset@example.com"},
            follow_redirects=False,
        )
        token = _extract_token(
            _preview_text_containing("/auth/password/reset?token="),
            "/auth/password/reset?token=",
        )
        reset_response = client.post(
            "/auth/password/reset",
            data={"token": token, "password": "new secure password"},
            follow_redirects=False,
        )
        login_response = client.post(
            "/auth/login",
            data={"email": "reset@example.com", "password": "new secure password"},
            follow_redirects=False,
        )

    assert request_response.status_code == 303
    assert reset_response.status_code == 303
    assert login_response.status_code == 303
