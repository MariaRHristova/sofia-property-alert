from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.providers.base import ListingCandidate

IMOT_BASE_URL = "https://www.imot.bg/"


def parse_imot_listing_cards(html: str) -> list[ListingCandidate]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("[data-listing-id]")
    return [candidate for card in cards if (candidate := _parse_card(card)) is not None]


def _parse_card(card: Tag) -> ListingCandidate | None:
    external_id = card.get("data-listing-id")
    if not external_id:
        return None

    title = _safe_text(card, ".listing__title")
    if not title:
        return None

    link = _safe_attr(card, "a.listing__link", "href")
    if not link:
        return None

    summary = _safe_text(card, ".listing__meta")
    location = _safe_text(card, ".listing__location")
    city, district = _split_location(location)

    return ListingCandidate(
        source="imot.bg-fixture",
        external_id=external_id,
        url=urljoin(IMOT_BASE_URL, link),
        title=title,
        city=city,
        district=district,
        transaction_type=_safe_attr(card, ".listing__card", "data-offer-type", "sale"),
        property_type=_safe_attr(
            card, ".listing__card", "data-property-type", "apartment"
        ),
        price_eur=_parse_price(_safe_text(card, ".listing__price")),
        area_sqm=_parse_area(summary),
        rooms=_parse_rooms(summary),
        published_at=_parse_published_at(_safe_attr(card, "time", "datetime")),
        raw_summary=summary or None,
    )


def _safe_text(element: Tag, selector: str, default: str = "") -> str:
    found = element.select_one(selector)
    return found.get_text(" ", strip=True) if found else default


def _safe_attr(
    element: Tag, selector: str, attr: str, default: str | None = None
) -> str | None:
    found = element.select_one(selector)
    return found.get(attr, default) if found else default


def _parse_price(text: str) -> float | None:
    digits = re.sub(r"[^\d]", "", text)
    return float(digits) if digits else None


def _parse_area(summary: str) -> float | None:
    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*sq\.m", summary, flags=re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def _parse_rooms(summary: str) -> str | None:
    match = re.search(r"(\d+)\s*bed", summary, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _split_location(location: str) -> tuple[str, str | None]:
    parts = [part.strip() for part in location.split(",") if part.strip()]
    if not parts:
        return "Unknown", None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1]
