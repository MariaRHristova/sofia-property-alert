from pathlib import Path

from app.providers.base import ListingSearchCriteria
from app.providers.fixtures import FixtureListingProvider, ImotBgListingProvider
from app.providers.parsers import build_imot_search_url, parse_imot_listing_cards

EXPECTED_TITLE_PREFIX = (
    "\u041f\u0440\u043e\u0434\u0430\u0432\u0430 2-"
    "\u0421\u0422\u0410\u0415\u041d"
)
EXPECTED_DISTRICT = "\u041b\u043e\u0437\u0435\u043d\u0435\u0446"


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

def test_build_imot_search_url_canonicalizes_sofia_aliases() -> None:
    criteria = ListingSearchCriteria(
        transaction_type="sale",
        property_type="apartment",
        city="Sofia",
        district="Center",
        min_price_eur=100000,
    )

    url = build_imot_search_url(criteria)

    assert url == (
        "https://www.imot.bg/obiavi/prodazhbi/grad-sofiya/tsentar?price_min=100000"
    )


def test_parse_imot_listing_cards_returns_normalized_results() -> None:
    html = Path("tests/fixtures/imot_search_sample.html").read_text(encoding="utf-8")

    listings = parse_imot_listing_cards(html)

    assert len(listings) == 2
    assert listings[0].external_id == "1b177425523801314"
    assert listings[0].title == "Двустаен апартамент, София, Лозенец"
    assert listings[0].city == "Sofia"
    assert listings[0].district == EXPECTED_DISTRICT
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

class _FakeResponse:
    def __init__(self, html: str) -> None:
        self.content = html.encode('utf-8')

    def raise_for_status(self) -> None:
        return None


class _FakeClient:
    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages
        self.requested_urls: list[str] = []

    def get(self, url: str) -> _FakeResponse:
        self.requested_urls.append(url)
        return _FakeResponse(self.pages[url])


def test_parse_live_listing_card_normalizes_sofia_district_and_price() -> None:
    html = (
        '<div class="item BEST" id="ida1b176406197723408">'
        '<div class="text"><div class="zaglavie">'
        '<a class="title saveSlink" '
        'href="//www.imot.bg/obiava-1b-lozenets">'
        f'{EXPECTED_TITLE_PREFIX}<location>град София, Лозенец</location>'
        '</a><div class="price"><div>179 000 €</div></div>'
        '</div></div></div>'
    )

    listings = parse_imot_listing_cards(html)

    assert len(listings) == 1
    assert listings[0].external_id == '1b'
    assert listings[0].title.startswith(EXPECTED_TITLE_PREFIX)
    assert listings[0].city == 'Sofia'
    assert listings[0].district == EXPECTED_DISTRICT
    assert listings[0].price_eur == 179000.0


def test_imot_provider_follows_next_page_links() -> None:
    criteria = ListingSearchCriteria(
        transaction_type='sale',
        property_type='apartment',
        city='Sofia',
        district=None,
        min_price_eur=100000,
        rooms='2',
    )
    first_url = 'https://www.imot.bg/obiavi/prodazhbi/grad-sofiya/dvustaen?price_min=100000'
    second_url = 'https://www.imot.bg/obiavi/prodazhbi/grad-sofiya/dvustaen/p-2?price_min=100000'
    pages = {
        first_url: (
            '<html><head>'
            '<link rel="next" '
            'href="/obiavi/prodazhbi/grad-sofiya/dvustaen/p-2?price_min=100000"/>'
            '</head><body>'
            '<div class="item BEST" id="ida1">'
            '<div class="text"><div class="zaglavie">'
            '<a class="title" href="//www.imot.bg/obiava-1a-lozenets">'
            f'{EXPECTED_TITLE_PREFIX}<location>град София, Лозенец</location>'
            '</a><div class="price"><div>110 000 €</div></div>'
            '</div></div></div>'
            '</body></html>'
        ),
        second_url: (
            '<html><body>'
            '<div class="item BEST" id="ida2">'
            '<div class="text"><div class="zaglavie">'
            '<a class="title" href="//www.imot.bg/obiava-1b-lozenets">'
            f'{EXPECTED_TITLE_PREFIX}<location>град София, Лозенец</location>'
            '</a><div class="price"><div>120 000 €</div></div>'
            '</div></div></div>'
            '</body></html>'
        ),
    }
    client = _FakeClient(pages)
    provider = ImotBgListingProvider(client, max_pages=5)

    listings = provider.fetch(criteria)

    assert [listing.external_id for listing in listings] == ['1a', '1b']
    assert client.requested_urls == [first_url, second_url]
