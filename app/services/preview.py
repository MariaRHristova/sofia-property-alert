from __future__ import annotations

from dataclasses import dataclass

from app.providers.base import ListingCandidate
from app.services.subscriptions import SubscriptionView


@dataclass(slots=True)
class PreviewResult:
    subscription: SubscriptionView
    matches: list[ListingCandidate]


def build_preview(
    subscription: SubscriptionView,
    listings: list[ListingCandidate],
) -> PreviewResult:
    matches = [
        listing for listing in listings if matches_subscription(subscription, listing)
    ]
    return PreviewResult(subscription=subscription, matches=matches)


def matches_subscription(
    subscription: SubscriptionView,
    listing: ListingCandidate,
) -> bool:
    if not subscription.active:
        return False
    if listing.city != subscription.city:
        return False
    if listing.transaction_type != subscription.transaction_type:
        return False
    if listing.property_type != subscription.property_type:
        return False
    if subscription.districts and listing.district not in subscription.districts:
        return False
    if subscription.min_price_eur is not None:
        if listing.price_eur is None or listing.price_eur < subscription.min_price_eur:
            return False
    if subscription.max_price_eur is not None:
        if listing.price_eur is None or listing.price_eur > subscription.max_price_eur:
            return False
    if subscription.min_area_sqm is not None:
        if listing.area_sqm is None or listing.area_sqm < subscription.min_area_sqm:
            return False
    if subscription.rooms is not None:
        if not rooms_match(subscription.rooms, listing.rooms):
            return False
    return True


def rooms_match(expected: str, actual: str | None) -> bool:
    if actual is None:
        return False
    if expected == "4+":
        return actual.isdigit() and int(actual) >= 4
    return expected == actual
