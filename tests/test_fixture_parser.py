from pathlib import Path

from app.providers.fixtures import FixtureListingProvider
from app.providers.parsers import parse_imot_listing_cards


def test_parse_imot_listing_cards_returns_normalized_results() -> None:
    html = Path("tests/fixtures/imot_search_sample.html").read_text(encoding="utf-8")

    listings = parse_imot_listing_cards(html)

    assert len(listings) == 2
    assert listings[0].external_id == "1001"
    assert listings[0].city == "Sofia"
    assert listings[0].district == "Lozenets"
    assert listings[0].price_eur == 245000.0
    assert listings[0].area_sqm == 84.0
    assert listings[0].rooms == "2"
    assert listings[0].url == "https://www.imot.bg/pcgi/imot.cgi?act=5&adv=1a1001"


def test_fixture_provider_reads_html_fixture_from_disk() -> None:
    provider = FixtureListingProvider("tests/fixtures/imot_search_sample.html")

    listings = provider.fetch()

    assert [listing.external_id for listing in listings] == ["1001", "1002"]
