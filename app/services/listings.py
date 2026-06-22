from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from typing import Iterator

import httpx

from app.config import Settings
from app.providers.base import ListingCandidate, ListingProvider, ListingSearchCriteria
from app.providers.fixtures import FixtureListingProvider, ImotBgListingProvider
from app.services.subscriptions import SubscriptionView

LIVE_USER_AGENT = "BulgariaPropertyAlert/1.0 (+https://github.com/MariaRHristova/sofia-property-alert)"


def build_search_criteria(subscription: SubscriptionView) -> ListingSearchCriteria:
    return ListingSearchCriteria(
        transaction_type=subscription.transaction_type,
        property_type=subscription.property_type,
        city=subscription.city,
        district=subscription.districts[0] if subscription.districts else None,
        min_price_eur=subscription.min_price_eur,
        max_price_eur=subscription.max_price_eur,
        rooms=subscription.rooms,
    )


def listing_source_label(settings: Settings) -> str:
    return "imot.bg live" if settings.imot_live_enabled else "fixture"


def load_listings_for_subscription(
    subscription: SubscriptionView,
    settings: Settings,
) -> list[ListingCandidate]:
    return load_listings_for_subscriptions([subscription], settings)


def load_listings_for_subscriptions(
    subscriptions: Iterable[SubscriptionView],
    settings: Settings,
) -> list[ListingCandidate]:
    subscription_list = list(subscriptions)
    if not subscription_list:
        return []

    if settings.imot_live_enabled:
        with _open_live_provider() as provider:
            return _collect_listings(subscription_list, provider, live_mode=True)

    provider = FixtureListingProvider(settings.fixture_html_path)
    return _collect_listings(subscription_list, provider, live_mode=False)


@contextmanager
def _open_live_provider() -> Iterator[ListingProvider]:
    with httpx.Client(
        timeout=30.0,
        headers={"User-Agent": LIVE_USER_AGENT},
        follow_redirects=True,
        trust_env=False,
    ) as client:
        yield ImotBgListingProvider(client)


def _collect_listings(
    subscriptions: list[SubscriptionView],
    provider: ListingProvider,
    *,
    live_mode: bool,
) -> list[ListingCandidate]:
    if not live_mode:
        return provider.fetch()

    results: list[ListingCandidate] = []
    seen_urls: set[str] = set()
    cache: dict[tuple[object, ...], list[ListingCandidate]] = {}

    for subscription in subscriptions:
        criteria = build_search_criteria(subscription)
        live_criteria = _live_fetch_criteria(criteria)
        cache_key = _criteria_cache_key(live_criteria)
        if cache_key not in cache:
            cache[cache_key] = provider.fetch(live_criteria)
        for candidate in cache[cache_key]:
            if candidate.url in seen_urls:
                continue
            seen_urls.add(candidate.url)
            results.append(candidate)

    return results


def _live_fetch_criteria(criteria: ListingSearchCriteria) -> ListingSearchCriteria:
    return ListingSearchCriteria(
        transaction_type=criteria.transaction_type,
        property_type=criteria.property_type,
        city=criteria.city,
        district=None,
        min_price_eur=criteria.min_price_eur,
        max_price_eur=criteria.max_price_eur,
        rooms=criteria.rooms,
    )


def _criteria_cache_key(criteria: ListingSearchCriteria) -> tuple[object, ...]:
    return (
        criteria.transaction_type,
        criteria.property_type,
        criteria.city,
        criteria.district,
        criteria.min_price_eur,
        criteria.max_price_eur,
        criteria.rooms,
    )
