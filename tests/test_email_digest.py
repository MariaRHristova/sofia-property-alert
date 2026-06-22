from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.email.delivery import build_digest
from app.services.subscriptions import SubscriptionView


def make_subscription() -> SubscriptionView:
    return SubscriptionView(
        id=1,
        email="subscriber@example.com",
        transaction_type="sale",
        property_type="apartment",
        city="Sofia",
        districts=["Лозенец"],
        min_price_eur=200000,
        max_price_eur=300000,
        rooms="2",
        min_area_sqm=70,
        unsubscribe_token="token",
        active=True,
        initialized=True,
    )


def test_build_digest_uses_clear_empty_state_copy() -> None:
    digest = build_digest(make_subscription(), [])

    assert "No available listings in Sofia" in digest.subject
    assert "There are no available listings" in digest.text
    assert "Criteria: Sofia, sale, apartment" in digest.text
    assert "There are no available listings" in digest.html


def test_settings_default_smtp_backend(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    settings = Settings(_env_file=None)

    assert settings.email_backend == "smtp"
    assert settings.email_preview_dir == "var/email-previews"
