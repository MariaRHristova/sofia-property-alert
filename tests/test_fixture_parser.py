from pathlib import Path

from app.providers.base import ListingSearchCriteria
from app.providers.fixtures import FixtureListingProvider
from app.providers.parsers import build_imot_search_url, parse_imot_listing_cards


def test_build_imot_search_url_uses_real_imot_slugs() -> None:
    criteria = ListingSearchCriteria(
        transaction_type="sale",
        property_type="apartment",
        city="Sofia",
        district="Кръстова вада",
        min_price_eur=100000,
        max_price_eur=200000,
        rooms="2",
    )

    url = build_imot_search_url(criteria)

    assert url == (
        "https://www.imot.bg/obiavi/prodazhbi/grad-sofiya/krastova-vada/dvustaen"
        "?price_min=100000&price_max=200000"
    )


def test_parse_imot_listing_cards_returns_normalized_results() -> None:
    html = Path("tests/fixtures/imot_search_sample.html").read_text(encoding="utf-8")

    listings = parse_imot_listing_cards(html)

    assert len(listings) == 2
    assert listings[0].external_id == "1b177425523801314"
    assert listings[0].title == "Двустаен апартамент, София, Лозенец"
    assert listings[0].city == "Sofia"
    assert listings[0].district == "Лозенец"
    assert listings[0].price_eur == 200000.0
    assert listings[0].area_sqm == 84.0
    assert listings[0].rooms == "2"
    assert listings[0].url == (
        "https://www.imot.bg/obiava-1b177425523801314-prodava-"
        "dvustaen-apartament-grad-sofiya-lozenets-bul-dzheyms-bauchar"
    )


def test_fixture_provider_reads_html_fixture_from_disk() -> None:
    provider = FixtureListingProvider("tests/fixtures/imot_search_sample.html")

    listings = provider.fetch()

    assert [listing.external_id for listing in listings] == [
        "1b177425523801314",
        "1b177425523801315",
    ]
