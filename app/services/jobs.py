from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.email.delivery import EmailDeliveryResult, EmailService
from app.models import JobRun, Listing, ListingMatch, Subscription
from app.providers.base import ListingCandidate
from app.services.listings import listing_source_label, load_listings_for_subscriptions
from app.services.preview import matches_subscription
from app.services.subscriptions import to_subscription_view


@dataclass(slots=True)
class JobResult:
    job_run: JobRun
    listings_seen: int
    listings_created: int
    matches_created: int
    emails_sent: int
    active_subscriptions: int
    email_backend: str
    preview_paths: list[str]
    email_errors: list[str]


class JobService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run_daily_job(
        self,
        provider_name: str,
        listings: list[ListingCandidate],
        email_service: EmailService,
    ) -> JobResult:
        job_run = JobRun(provider=provider_name, status="running")
        self.session.add(job_run)
        self.session.flush()

        active_subscriptions = list(
            self.session.scalars(
                select(Subscription).where(Subscription.active.is_(True))
            )
        )
        subscriptions = [
            to_subscription_view(subscription)
            for subscription in active_subscriptions
        ]

        listings_created = 0
        matches_created = 0
        preview_paths: list[str] = []
        email_errors: list[str] = []
        emails_sent = 0

        for candidate in listings:
            listing = self._upsert_listing(candidate)
            listings_created += int(listing is not None)

            for subscription in subscriptions:
                if not matches_subscription(subscription, candidate):
                    continue
                if self._create_match(subscription.id, listing.id):
                    matches_created += 1

        for subscription in subscriptions:
            matched_listings = self._load_subscription_matches(subscription.id)
            delivery_result = email_service.deliver(subscription, matched_listings)
            preview_paths.extend(self._record_delivery(delivery_result))
            if (
                delivery_result.error
                and delivery_result.error not in email_errors
            ):
                email_errors.append(delivery_result.error)
            emails_sent += int(delivery_result.sent)

        job_run.status = "finished_with_errors" if email_errors else "finished"
        job_run.listings_seen = len(listings)
        job_run.listings_created = listings_created
        job_run.matches_created = matches_created
        job_run.emails_sent = emails_sent
        job_run.finished_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(job_run)

        return JobResult(
            job_run=job_run,
            listings_seen=len(listings),
            listings_created=listings_created,
            matches_created=matches_created,
            emails_sent=emails_sent,
            active_subscriptions=len(subscriptions),
            email_backend=email_service.settings.email_backend,
            preview_paths=preview_paths,
            email_errors=email_errors,
        )

    def list_recent_job_runs(self, limit: int = 5) -> list[JobRun]:
        statement = select(JobRun).order_by(JobRun.started_at.desc()).limit(limit)
        return list(self.session.scalars(statement))

    def persist_subscription_preview(
        self,
        subscription_id: int,
        listings: list[ListingCandidate],
    ) -> int:
        created = 0
        for candidate in listings:
            listing = self._upsert_listing(candidate)
            if self._create_match(subscription_id, listing.id):
                created += 1
        self.session.commit()
        return created

    def _upsert_listing(self, candidate: ListingCandidate) -> Listing:
        statement = select(Listing).where(
            Listing.source == candidate.source,
            Listing.external_id == candidate.external_id,
        )
        existing = self.session.scalar(statement)
        if existing is not None:
            return existing

        listing = Listing(
            source=candidate.source,
            external_id=candidate.external_id,
            url=candidate.url,
            title=candidate.title,
            city=candidate.city,
            district=candidate.district,
            transaction_type=candidate.transaction_type,
            property_type=candidate.property_type,
            price_eur=candidate.price_eur,
            area_sqm=candidate.area_sqm,
            rooms=candidate.rooms,
            published_at=candidate.published_at,
            raw_summary=candidate.raw_summary,
        )
        self.session.add(listing)
        self.session.flush()
        return listing

    def _create_match(self, subscription_id: int, listing_id: int) -> bool:
        with self.session.begin_nested():
            match = ListingMatch(
                subscription_id=subscription_id,
                listing_id=listing_id,
                state="pending",
            )
            self.session.add(match)
            try:
                self.session.flush()
            except Exception:
                return False
        return True

    def _load_subscription_matches(
        self,
        subscription_id: int,
    ) -> list[dict[str, object]]:
        statement = (
            select(Listing)
            .join(ListingMatch, ListingMatch.listing_id == Listing.id)
            .where(ListingMatch.subscription_id == subscription_id)
            .order_by(
                Listing.published_at.desc().nullslast(),
                Listing.first_seen_at.desc(),
            )
        )
        return [
            {
                "title": listing.title,
                "url": listing.url,
                "city": listing.city,
                "district": listing.district,
                "price_eur": listing.price_eur,
                "area_sqm": listing.area_sqm,
            }
            for listing in self.session.scalars(statement)
        ]

    def _record_delivery(self, delivery_result: EmailDeliveryResult) -> list[str]:
        if delivery_result.output_path:
            return [delivery_result.output_path]
        return []


def execute_job_run(
    session_factory: Callable[[], Session],
    settings: Settings,
) -> JobResult:
    with session_factory() as session:
        job_service = JobService(session)
        email_service = EmailService(settings)
        subscriptions = [
            to_subscription_view(item)
            for item in session.scalars(
                select(Subscription).where(Subscription.active.is_(True))
            )
        ]
        listings = load_listings_for_subscriptions(subscriptions, settings)
        return job_service.run_daily_job(
            listing_source_label(settings),
            listings,
            email_service,
        )
