from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

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
    def __init__(self, client, max_pages: int = 10) -> None:
        self.client = client
        self.max_pages = max_pages

    def fetch(
        self,
        criteria: ListingSearchCriteria | None = None,
    ) -> list[ListingCandidate]:
        if criteria is None:
            raise ValueError("Imot.bg listings require search criteria.")

        listings: list[ListingCandidate] = []
        seen_listing_urls: set[str] = set()
        seen_page_urls: set[str] = set()
        next_url = build_imot_search_url(criteria)

        for _ in range(self.max_pages):
            if next_url in seen_page_urls:
                break
            seen_page_urls.add(next_url)
            response = self.client.get(next_url)
            response.raise_for_status()

            page_listings = parse_imot_listing_cards(response.content)
            for listing in page_listings:
                if listing.url in seen_listing_urls:
                    continue
                seen_listing_urls.add(listing.url)
                listings.append(listing)

            soup = BeautifulSoup(response.content, "lxml")
            next_link = soup.select_one('link[rel="next"][href], a.next[href]')
            if next_link is None:
                break
            resolved_next_url = urljoin(next_url, next_link["href"])
            if resolved_next_url in seen_page_urls:
                break
            next_url = resolved_next_url

        return listings
