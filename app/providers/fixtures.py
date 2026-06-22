from pathlib import Path

from app.providers.base import ListingCandidate, ListingProvider, ListingSearchCriteria
from app.providers.parsers import build_imot_search_url, parse_imot_listing_cards


class FixtureListingProvider(ListingProvider):
    def __init__(self, html_path: str) -> None:
        self.html_path = Path(html_path)

    def fetch(
        self,
        criteria: ListingSearchCriteria | None = None,
    ) -> list[ListingCandidate]:
        html = self.html_path.read_text(encoding="utf-8")
        return parse_imot_listing_cards(html)


class ImotBgListingProvider(ListingProvider):
    def __init__(self, client) -> None:
        self.client = client

    def fetch(
        self,
        criteria: ListingSearchCriteria | None = None,
    ) -> list[ListingCandidate]:
        if criteria is None:
            raise ValueError("Imot.bg listings require search criteria.")
        url = build_imot_search_url(criteria)
        response = self.client.get(url)
        response.raise_for_status()
        return parse_imot_listing_cards(response.text)
