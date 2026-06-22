from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(slots=True)
class ListingCandidate:
    source: str
    external_id: str
    url: str
    title: str
    city: str
    district: str | None
    transaction_type: str
    property_type: str
    price_eur: float | None
    area_sqm: float | None
    rooms: str | None
    published_at: datetime | None
    raw_summary: str | None


@dataclass(slots=True)
class ListingSearchCriteria:
    transaction_type: str
    property_type: str
    city: str
    district: str | None = None
    min_price_eur: float | None = None
    max_price_eur: float | None = None
    rooms: str | None = None


class ListingProvider(Protocol):
    def fetch(
        self,
        criteria: ListingSearchCriteria | None = None,
    ) -> list[ListingCandidate]:
        """Return normalized listing candidates from a specific source."""
