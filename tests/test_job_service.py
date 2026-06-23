from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from sqlalchemy import select

import app.main as main_module
from app.email.delivery import EmailDeliveryResult
from app.models import ListingMatch, Subscription, User
from app.providers.base import ListingCandidate
from app.services.jobs import JobService


class FakeEmailService:
    def __init__(self, *, sent: bool = True, error: str | None = None) -> None:
        self.settings = SimpleNamespace(email_backend="smtp")
        self.sent = sent
        self.error = error
        self.calls: list[tuple[str, list[str]]] = []

    def deliver(self, subscription, matches):  # noqa: ANN001
        self.calls.append(
            (subscription.email, [str(match["title"]) for match in matches])
        )
        return EmailDeliveryResult(
            backend="smtp",
            sent=self.sent,
            error=self.error,
        )


def _make_candidate(
    external_id: str,
    title: str,
    *,
    price: int = 240000,
) -> ListingCandidate:
    return ListingCandidate(
        source="fixture",
        external_id=external_id,
        url=f"https://example.com/{external_id}",
        title=title,
        city="Sofia",
        district="Lozenets",
        transaction_type="sale",
        property_type="apartment",
        price_eur=float(price),
        area_sqm=82.0,
        rooms="2",
        published_at=datetime(2026, 6, 23, tzinfo=timezone.utc),
        raw_summary=title,
    )


def _create_subscription(session) -> Subscription:  # noqa: ANN001
    user = User(
        email="owner@example.com",
        password_hash="hash",
        active=True,
    )
    session.add(user)
    session.flush()
    subscription = Subscription(
        user_id=user.id,
        email="owner@example.com",
        transaction_type="sale",
        property_type="apartment",
        city="Sofia",
        districts="Lozenets",
        min_price_eur=200000,
        max_price_eur=300000,
        rooms="2",
        min_area_sqm=70,
        active=True,
        initialized=True,
        unsubscribe_token="token-1",
    )
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription


def test_daily_job_only_emails_new_matches_after_delivery() -> None:
    with main_module.SessionLocal() as session:
        subscription = _create_subscription(session)
        service = JobService(session)
        email_service = FakeEmailService(sent=True)
        first_candidate = _make_candidate("listing-1", "First matching flat")
        second_candidate = _make_candidate("listing-2", "Second matching flat")

        first_result = service.run_daily_job(
            "fixture",
            [first_candidate],
            email_service,
            user_id=subscription.user_id,
        )
        second_result = service.run_daily_job(
            "fixture",
            [first_candidate],
            email_service,
            user_id=subscription.user_id,
        )
        third_result = service.run_daily_job(
            "fixture",
            [second_candidate],
            email_service,
            user_id=subscription.user_id,
        )

    with main_module.SessionLocal() as verify_session:
        matches = list(
            verify_session.scalars(select(ListingMatch).order_by(ListingMatch.id))
        )

    assert first_result.matches_created == 1
    assert first_result.emails_sent == 1
    assert email_service.calls[0][1] == ["First matching flat"]
    assert second_result.matches_created == 0
    assert second_result.emails_sent == 1
    assert email_service.calls[1][1] == []
    assert third_result.matches_created == 1
    assert third_result.emails_sent == 1
    assert email_service.calls[2][1] == ["Second matching flat"]
    assert [match.state for match in matches] == ["delivered", "delivered"]
    assert all(match.delivered_at is not None for match in matches)


def test_daily_job_keeps_matches_pending_after_delivery_failure() -> None:
    with main_module.SessionLocal() as session:
        subscription = _create_subscription(session)
        service = JobService(session)
        failing_email_service = FakeEmailService(
            sent=False,
            error="SMTP delivery failed",
        )
        candidate = _make_candidate("listing-3", "Retry me later")

        failed_result = service.run_daily_job(
            "fixture",
            [candidate],
            failing_email_service,
            user_id=subscription.user_id,
        )

    with main_module.SessionLocal() as verify_session:
        pending_match = verify_session.scalar(
            select(ListingMatch).order_by(ListingMatch.id)
        )

    with main_module.SessionLocal() as session:
        service = JobService(session)
        retry_service = FakeEmailService(sent=True)
        retry_result = service.run_daily_job(
            "fixture",
            [candidate],
            retry_service,
            user_id=subscription.user_id,
        )

    with main_module.SessionLocal() as verify_session:
        updated_match = verify_session.scalar(
            select(ListingMatch).order_by(ListingMatch.id)
        )

    assert failed_result.matches_created == 1
    assert failed_result.emails_sent == 0
    assert pending_match is not None
    assert pending_match.state == "pending"
    assert pending_match.delivered_at is None
    assert retry_result.matches_created == 0
    assert retry_result.emails_sent == 1
    assert retry_service.calls[0][1] == ["Retry me later"]
    assert updated_match is not None
    assert updated_match.state == "delivered"
    assert updated_match.delivered_at is not None
