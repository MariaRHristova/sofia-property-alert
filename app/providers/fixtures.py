from pathlib import Path

from app.providers.base import ListingCandidate, ListingProvider
from app.providers.parsers import parse_imot_listing_cards


class FixtureListingProvider(ListingProvider):
    def __init__(self, html_path: str) -> None:
        self.html_path = Path(html_path)

    def fetch(self) -> list[ListingCandidate]:
        html = self.html_path.read_text(encoding="utf-8")
        return parse_imot_listing_cards(html)
