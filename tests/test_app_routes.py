from fastapi.testclient import TestClient
from sqlalchemy import func, select

import app.main as main_module
from app.main import app
from app.models import ListingMatch, Subscription


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


def test_create_subscription_rejects_non_sofia_city() -> None:
    payload = {
        "email": "invalid@example.com",
        "transaction_type": "sale",
        "property_type": "apartment",
        "city": "Plovdiv",
        "districts": [],
    }

    with TestClient(app) as client:
        response = client.post("/subscriptions", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"][0]["msg"] == "Value error, Unsupported city."


def test_root_endpoint_renders_editorial_property_alert_page() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        stylesheet_response = client.get("/static/app.css")

    assert response.status_code == 200
    assert "Property Finder" in response.text
    assert "Sofia edition" in response.text
    assert "Create an alert" in response.text
    assert "This proof of concept currently supports Sofia only." in response.text
    assert (
        "Preparing your digest and checking Sofia for new listings..."
        in response.text
    )
    assert 'href="#main-content"' in response.text
    assert '<main id="main-content">' in response.text
    assert 'autocomplete="email"' in response.text
    assert 'role="status"' in response.text
    assert stylesheet_response.status_code == 200
    assert "--blue: #1597c7" in stylesheet_response.text
    assert "--paper: #f7f7f5" in stylesheet_response.text
    assert "--paper-bright: #ffffff" in stylesheet_response.text
    assert "#fffaf0" not in stylesheet_response.text
    assert ".map-lens" in stylesheet_response.text


def test_root_endpoint_renders_in_live_mode(monkeypatch) -> None:
    monkeypatch.setattr(main_module.settings, "imot_live_enabled", True)
    monkeypatch.setattr(main_module, "load_listings_for_subscriptions", lambda *_: [])

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Property Finder" in response.text
    assert "Sofia edition" in response.text


def test_create_subscription_returns_preview_count() -> None:
    payload = {
        "email": "route@example.com",
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
        response = client.post("/subscriptions", json=payload)
        page_response = client.get("/")

    assert response.status_code == 201
    assert response.json()["preview_match_count"] == 1
    assert "Delete permanently" in page_response.text


def test_unsubscribe_deactivates_alert_and_keeps_resubscribe_path(monkeypatch) -> None:
    payload = {
        "email": "delete@example.com",
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
        monkeypatch.setattr(main_module.settings, "email_backend", "preview")
        create_response = client.post("/subscriptions", json=payload)
        subscription_id = create_response.json()["id"]
        unsubscribe_url = create_response.json()["unsubscribe_url"]
        client.post("/jobs/run")
        with main_module.SessionLocal() as session:
            match_count = session.scalar(
                select(func.count())
                .select_from(ListingMatch)
                .where(ListingMatch.subscription_id == subscription_id)
            )
        unsubscribe_response = client.get(unsubscribe_url)
        page_response = client.get("/")
        with main_module.SessionLocal() as session:
            remaining_matches = session.scalar(
                select(func.count())
                .select_from(ListingMatch)
                .where(ListingMatch.subscription_id == subscription_id)
            )
            remaining_subscriptions = session.scalar(
                select(func.count())
                .select_from(Subscription)
                .where(Subscription.id == subscription_id)
            )

    assert match_count == 1
    assert unsubscribe_response.status_code == 200
    assert "You are unsubscribed" in unsubscribe_response.text
    assert payload["email"] in page_response.text
    assert "Subscribe again" in page_response.text
    assert remaining_matches == 0
    assert remaining_subscriptions == 1


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
        "districts": ["Lozenets"],
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
        "districts": ["Lozenets"],
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
