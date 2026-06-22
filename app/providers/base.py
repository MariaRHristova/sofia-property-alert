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


class ListingProvider(Protocol):
    def fetch(self) -> list[ListingCandidate]:
        """Return normalized listing candidates from a specific source."""
