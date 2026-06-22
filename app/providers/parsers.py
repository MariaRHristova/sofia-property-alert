from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from app.catalog import canonicalize_district
from app.providers.base import ListingCandidate, ListingSearchCriteria

IMOT_BASE_URL = "https://www.imot.bg/"
TRANSACTION_PATHS = {
    "sale": "prodazhbi",
    "rent": "naemi",
}
PROPERTY_PATHS = {
    "apartment": {"2": "dvustaen", "3": "tristaen", "4+": "chetiristaen"},
    "house": {"2": "kashta", "3": "kashta", "4+": "kashta"},
}
CITY_SLUGS = {
    "Sofia": "grad-sofiya",
    "Plovdiv": "grad-plovdiv",
    "Varna": "grad-varna",
    "Burgas": "grad-burgas",
}
ROOM_SLUGS = {
    "1": "ednostaen",
    "2": "dvustaen",
    "3": "tristaen",
    "4+": "chetiristaen",
}


def build_imot_search_url(criteria: ListingSearchCriteria) -> str:
    transaction = TRANSACTION_PATHS.get(criteria.transaction_type)
    city = CITY_SLUGS.get(criteria.city)
    if transaction is None or city is None:
        raise ValueError("Unsupported imot.bg search criteria.")

    path_parts = ["obiavi", transaction, city]
    if criteria.district:
        path_parts.append(_slugify_district(criteria.district))

    room_slug = ROOM_SLUGS.get(criteria.rooms or "")
    property_slug = PROPERTY_PATHS.get(criteria.property_type, {}).get(
        criteria.rooms or ""
    )
    if room_slug:
        path_parts.append(property_slug or room_slug)
    elif property_slug:
        path_parts.append(property_slug)

    query: list[str] = []
    if criteria.min_price_eur is not None:
        query.append(f"price_min={int(criteria.min_price_eur)}")
    if criteria.max_price_eur is not None:
        query.append(f"price_max={int(criteria.max_price_eur)}")

    url = IMOT_BASE_URL + "/".join(path_parts)
    if query:
        url = f"{url}?{'&'.join(query)}"
    return url


def parse_imot_listing_cards(
    html: str, *, source: str = "imot.bg"
) -> list[ListingCandidate]:
    soup = BeautifulSoup(html, "lxml")
    seen_urls: set[str] = set()
    candidates: list[ListingCandidate] = []
    for anchor in soup.select('a[href*="/obiava-"]'):
        candidate = _parse_anchor(anchor, source=source)
        if candidate is None or candidate.url in seen_urls:
            continue
        seen_urls.add(candidate.url)
        candidates.append(candidate)
    return candidates


def _parse_anchor(anchor: Tag, *, source: str) -> ListingCandidate | None:
    href = anchor.get("href")
    if not href:
        return None
    url = urljoin(IMOT_BASE_URL, href)
    parsed = urlparse(url)
    if "/obiava-" not in parsed.path:
        return None

    title = _clean_text(anchor)
    if not title or title.lower() == "\u0441\u043d\u0438\u043c\u043a\u0430":
        return None

    card = (
        anchor.find_parent(class_=re.compile(r"(ads2023|listing|card|item)"))
        or anchor.parent
    )
    if card is None:
        return None

    summary = _extract_summary(card)
    if _looks_sponsored(anchor, card, title, summary):
        return None

    location_text = _extract_location(card)
    city, district = _split_location(location_text)
    if city is None:
        city = "Sofia"

    external_id = _parse_external_id(parsed.path)
    if external_id is None:
        return None

    transaction_type, property_type, rooms = _infer_listing_type(url, title, summary)

    return ListingCandidate(
        source=source,
        external_id=external_id,
        url=url,
        title=title,
        city=city,
        district=district,
        transaction_type=transaction_type,
        property_type=property_type,
        price_eur=_parse_price(_extract_price_text(card)),
        area_sqm=_parse_area(summary),
        rooms=rooms,
        published_at=_parse_published_at(_extract_published_at(card)),
        raw_summary=summary or None,
    )


def _clean_text(element: Tag) -> str:
    return element.get_text(" ", strip=True).replace(" ", " ").strip()


def _extract_summary(card: Tag) -> str:
    for selector in [".description", ".data", ".text", "[class*='opis']", ".price"]:
        found = card.select_one(selector)
        if found:
            return _clean_text(found)
    text = _clean_text(card)
    return text if len(text) < 300 else text[:300]


def _extract_location(card: Tag) -> str:
    for selector in [
        ".location",
        ".location2023",
        ".adr",
        "[class*='m2']",
        "[class*='city']",
    ]:
        found = card.select_one(selector)
        if found:
            return _clean_text(found)
    return ""


def _extract_price_text(card: Tag) -> str:
    price = card.select_one(".price")
    if price:
        return _clean_text(price)
    text = _clean_text(card)
    match = re.search(
        r"\d[\d\s\.]*\s*(?:\u20ac|eur|\u043b\u0432\.)", text, flags=re.IGNORECASE
    )
    return match.group(0) if match else ""


def _looks_sponsored(anchor: Tag, card: Tag, title: str, summary: str) -> bool:
    for node in [card, anchor, *card.parents]:
        classes = node.get("class", []) if isinstance(node, Tag) else []
        if "nova-sgrada" in classes:
            return True
    haystack = f"{title} {summary} {_clean_text(card)}".lower()
    return (
        "\u0440\u0435\u043a\u043b\u0430\u043c\u0430" in haystack
        or "sponsored" in haystack
    )


def _parse_external_id(path: str) -> str | None:
    match = re.search(r"/obiava-([a-z0-9]+)-", path, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    fallback = re.search(r"/obiava-([^/]+)", path, flags=re.IGNORECASE)
    return fallback.group(1) if fallback else None


def _infer_listing_type(
    url: str, title: str, summary: str
) -> tuple[str, str, str | None]:
    haystack = f"{url} {title} {summary}".lower()
    transaction_type = (
        "rent"
        if "/naemi/" in haystack
        or "\u043f\u043e\u0434 \u043d\u0430\u0435\u043c" in haystack
        else "sale"
    )
    property_type = (
        "house"
        if any(
            keyword in haystack
            for keyword in ["\u043a\u044a\u0449\u0430", "house", "kashta"]
        )
        else "apartment"
    )
    rooms = _parse_rooms(title + " " + summary)
    return transaction_type, property_type, rooms


def _parse_price(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r"([\d\s\.]+(?:,[\d]+)?)", text)
    if not match:
        return None
    value = match.group(1).replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


def _parse_area(summary: str) -> float | None:
    match = re.search(
        r"(\d+(?:[\.,]\d+)?)\s*(?:\u043a\u0432\.?\s*\u043c|sqm|sq\.m)",
        summary,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def _parse_rooms(text: str) -> str | None:
    normalized = text.lower()
    if any(
        keyword in normalized
        for keyword in [
            "\u0435\u0434\u043d\u043e\u0441\u0442\u0430\u0435\u043d",
            "studio",
            "1-\u0441\u0442\u0430\u0435\u043d",
        ]
    ):
        return "1"
    if any(
        keyword in normalized
        for keyword in [
            "\u0434\u0432\u0443\u0441\u0442\u0430\u0435\u043d",
            "2-\u0441\u0442\u0430\u0435\u043d",
        ]
    ):
        return "2"
    if any(
        keyword in normalized
        for keyword in [
            "\u0442\u0440\u0438\u0441\u0442\u0430\u0435\u043d",
            "3-\u0441\u0442\u0430\u0435\u043d",
        ]
    ):
        return "3"
    if any(
        keyword in normalized
        for keyword in [
            "\u0447\u0435\u0442\u0438\u0440\u0438\u0441\u0442\u0430\u0435\u043d",
            "4-\u0441\u0442\u0430\u0435\u043d",
            "\u043c\u043d\u043e\u0433\u043e\u0441\u0442\u0430\u0435\u043d",
        ]
    ):
        return "4+"
    return None


def _parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _extract_published_at(card: Tag) -> str | None:
    time_tag = card.find("time")
    if time_tag is not None:
        return time_tag.get("datetime") or time_tag.get_text(strip=True)
    return None


def _split_location(location: str) -> tuple[str | None, str | None]:
    text = location.strip()
    if not text:
        return None, None
    parts = [part.strip() for part in re.split(r"[,;]", text) if part.strip()]
    if len(parts) >= 2:
        city = _normalize_city(parts[0])
        return city, _normalize_district(parts[1], city=city)
    return _normalize_city(parts[0]), None


def _normalize_city(value: str) -> str:
    cleaned = value.strip().lower()
    if cleaned in {"sofia", "софия", "град софия"}:
        return "Sofia"
    if cleaned in {"plovdiv", "пловдив", "град пловдив"}:
        return "Plovdiv"
    if cleaned in {"varna", "варна", "град варна"}:
        return "Varna"
    if cleaned in {"burgas", "бургас", "град бургас"}:
        return "Burgas"
    return value.strip() or "Sofia"


def _normalize_district(value: str, *, city: str | None) -> str:
    cleaned = value.strip()
    if city == "Sofia":
        return canonicalize_district(cleaned, city=city)
    return cleaned


def _slugify_district(value: str) -> str:
    normalized = _transliterate_bulgarian(value).lower()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def _transliterate_bulgarian(value: str) -> str:
    transliteration_map = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sht",
        "ъ": "a",
        "ь": "",
        "ю": "yu",
        "я": "ya",
    }
    return "".join(transliteration_map.get(char, char) for char in value.lower())
