from fastapi.testclient import TestClient
from sqlalchemy import func, select

import app.main as main_module
from app.main import app
from app.models import Listing, ListingMatch


def test_health_endpoint_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_subscription_rejects_invalid_district() -> None:
    payload = {
        "email": "invalid@example.com",
        "transaction_type": "sale",
        "property_type": "apartment",
        "city": "Sofia",
        "districts": ["Not a district"],
    }

    with TestClient(app) as client:
        response = client.post("/subscriptions", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"][0]["msg"] == (
        "Value error, One or more districts do not belong to the selected city."
    )


def test_root_endpoint_renders_poc_page() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Bulgaria Property Alert" in response.text
    assert "Create a subscription" in response.text


def test_root_endpoint_renders_in_live_mode(monkeypatch) -> None:
    monkeypatch.setattr(main_module.settings, "imot_live_enabled", True)
    monkeypatch.setattr(main_module, "load_listings_for_subscriptions", lambda *_: [])

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Bulgaria Property Alert" in response.text


def test_create_subscription_returns_preview_count() -> None:
    payload = {
        "email": "route@example.com",
        "transaction_type": "sale",
        "property_type": "apartment",
        "city": "Sofia",
        "districts": ["Лозенец"],
        "min_price_eur": 200000,
        "max_price_eur": 300000,
        "rooms": "2",
        "min_area_sqm": 70,
    }

    with TestClient(app) as client:
        response = client.post("/subscriptions", json=payload)
        page_response = client.get("/")

    assert response.status_code == 201
    assert response.json()["preview_match_count"] == 1
    assert "Delete permanently" in page_response.text


def test_unsubscribe_can_reactivate_subscription(monkeypatch) -> None:
    payload = {
        "email": "delete@example.com",
        "transaction_type": "sale",
        "property_type": "apartment",
        "city": "Sofia",
        "districts": ["\u041b\u043e\u0437\u0435\u043d\u0435\u0446"],
        "min_price_eur": 200000,
        "max_price_eur": 300000,
        "rooms": "2",
        "min_area_sqm": 70,
    }

    with TestClient(app) as client:
        monkeypatch.setattr(main_module.settings, "email_backend", "preview")
        create_response = client.post("/subscriptions", json=payload)
        subscription_id = create_response.json()["id"]
        unsubscribe_url = create_response.json()["unsubscribe_url"]
        subscribe_again_url = (
            unsubscribe_url.removesuffix("/unsubscribe") + "/subscribe"
        )
        client.post("/jobs/run")
        with main_module.SessionLocal() as session:
            match_count = session.scalar(
                select(func.count())
                .select_from(ListingMatch)
                .where(ListingMatch.subscription_id == subscription_id)
            )
        unsubscribe_response = client.post(unsubscribe_url)
        with main_module.SessionLocal() as session:
            remaining_matches = session.scalar(
                select(func.count())
                .select_from(ListingMatch)
                .where(ListingMatch.subscription_id == subscription_id)
            )
            remaining_listings = session.scalar(
                select(func.count()).select_from(Listing)
            )
        inactive_page_response = client.get("/")
        reactivate_response = client.post(subscribe_again_url)
        page_response = client.get("/")

    assert match_count == 1
    assert unsubscribe_response.status_code == 200
    assert unsubscribe_response.json() == {"status": "unsubscribed"}
    assert remaining_matches == 0
    assert remaining_listings == 0
    assert "Subscribe again" in inactive_page_response.text
    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["status"] == "subscribed"
    assert reactivate_response.json()["preview_match_count"] >= 0
    assert payload["email"] in page_response.text
    assert "Subscribe again" not in page_response.text
    assert "Unsubscribe" in page_response.text


def test_job_run_records_job_summary(monkeypatch) -> None:
    monkeypatch.setattr(main_module.settings, "email_backend", "preview")
    with TestClient(app) as client:
        response = client.post("/jobs/run")
        recent = client.get("/jobs/recent")

    assert response.status_code == 200
    assert response.json()["status"] == "finished"
    assert response.json()["email_backend"] == "preview"
    assert response.json()["email_errors"] == []
    assert response.json()["matches_created"] >= 0
    assert recent.status_code == 200
    assert recent.json()["jobs"]


def test_daily_job_runs_for_subscription_email(monkeypatch) -> None:
    payload = {
        "email": "daily@example.com",
        "transaction_type": "sale",
        "property_type": "apartment",
        "city": "Sofia",
        "districts": ["Лозенец"],
        "min_price_eur": 200000,
        "max_price_eur": 300000,
        "rooms": "2",
        "min_area_sqm": 70,
    }

    with TestClient(app) as client:
        monkeypatch.setattr(main_module.settings, "email_backend", "preview")
        create_response = client.post("/subscriptions", json=payload)
        job_response = client.post("/jobs/run")
        recent_response = client.get("/jobs/recent")

    assert create_response.status_code == 201
    assert create_response.json()["email"] == payload["email"]
    assert create_response.json()["preview_match_count"] == 1
    assert job_response.status_code == 200
    assert job_response.json()["listings_seen"] > 0
    assert recent_response.status_code == 200
    assert recent_response.json()["jobs"][0]["status"] == "finished"


def test_job_run_surfaces_smtp_delivery_error(monkeypatch) -> None:
    monkeypatch.setattr(main_module.settings, "email_backend", "smtp")
    monkeypatch.setattr(
        main_module.EmailService,
        "_send_smtp",
        lambda *_: "SMTP authentication failed. Use a Google App Password.",
    )
    payload = {
        "email": "route@example.com",
        "transaction_type": "sale",
        "property_type": "apartment",
        "city": "Sofia",
        "districts": ["Лозенец"],
        "min_price_eur": 200000,
        "max_price_eur": 300000,
        "rooms": "2",
        "min_area_sqm": 70,
    }

    with TestClient(app) as client:
        client.post("/subscriptions", json=payload)
        response = client.post("/jobs/run")

    assert response.status_code == 200
    assert response.json()["status"] == "finished_with_errors"
    assert response.json()["emails_sent"] == 0
    assert response.json()["email_errors"] == [
        "SMTP authentication failed. Use a Google App Password."
    ]
