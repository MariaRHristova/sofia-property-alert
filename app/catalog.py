# ruff: noqa: E501
from typing import Final

CITY_OPTIONS: Final[dict[str, dict[str, list[str]]]] = {
    "Sofia": {
        "slug": "grad-sofiya",
        "districts": [
            "\u041b\u043e\u0437\u0435\u043d\u0435\u0446",
            "\u041c\u043b\u0430\u0434\u043e\u0441\u0442",
            "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 1",
            "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 1\u0410",
            "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 2",
            "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 3",
            "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 4",
            "\u041a\u0440\u044a\u0441\u0442\u043e\u0432\u0430 \u0432\u0430\u0434\u0430",
            "\u0426\u0435\u043d\u0442\u044a\u0440",
            "\u0411\u043e\u044f\u043d\u0430",
            "\u0421\u0442\u0443\u0434\u0435\u043d\u0442\u0441\u043a\u0438 \u0433\u0440\u0430\u0434",
            "\u041e\u0432\u0447\u0430 \u043a\u0443\u043f\u0435\u043b",
            "\u041b\u044e\u043b\u0438\u043d",
            "\u041f\u0430\u043d\u0447\u0430\u0440\u0435\u0432\u043e",
            "\u0412\u0438\u0442\u043e\u0448\u0430",
            "\u041d\u0430\u0434\u0435\u0436\u0434\u0430",
            "\u041a\u0440\u0435\u043c\u0438\u043a\u043e\u0432\u0446\u0438",
            "\u0418\u0441\u043a\u044a\u0440",
            "\u0412\u0440\u044a\u0431\u043d\u0438\u0446\u0430",
            "\u0414\u0440\u0430\u0433\u0430\u043b\u0435\u0432\u0446\u0438",
            "\u0421\u0438\u043c\u0435\u043e\u043d\u043e\u0432\u043e",
            "\u041c\u0430\u043d\u0430\u0441\u0442\u0438\u0440\u0441\u043a\u0438 \u043b\u0438\u0432\u0430\u0434\u0438",
            "\u0418\u0437\u0442\u043e\u043a",
            "\u0418\u0437\u0433\u0440\u0435\u0432",
            "\u0413\u0435\u043e \u041c\u0438\u043b\u0435\u0432",
            "\u0421\u043b\u0430\u0442\u0438\u043d\u0430",
            "\u041b\u0430\u0433\u0435\u0440\u0430",
            "\u041a\u0440\u0430\u0441\u043d\u043e \u0441\u0435\u043b\u043e",
            "\u0414\u0440\u0443\u0436\u0431\u0430",
        ],
    },
}

TRANSACTION_TYPES: Final[dict[str, str]] = {"sale": "prodazhbi", "rent": "naemi"}
PROPERTY_TYPES: Final[dict[str, str]] = {
    "apartment": "apartamenti",
    "house": "kashchi",
}
ROOM_OPTIONS: Final[dict[str, str]] = {
    "1": "ednostaen",
    "2": "dvustaen",
    "3": "tristaen",
    "4+": "chetiristaen",
}

SUPPORTED_LOCATIONS: Final[dict[str, list[str]]] = {
    city: values["districts"] for city, values in CITY_OPTIONS.items()
}

SOFIA_DISTRICT_ALIASES: Final[dict[str, str]] = {
    "Lozenets": "\u041b\u043e\u0437\u0435\u043d\u0435\u0446",
    "Mladost": "\u041c\u043b\u0430\u0434\u043e\u0441\u0442",
    "Mladost 1": "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 1",
    "Mladost 1A": "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 1\u0410",
    "Mladost 2": "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 2",
    "Mladost 3": "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 3",
    "Mladost 4": "\u041c\u043b\u0430\u0434\u043e\u0441\u0442 4",
    "Krastova vada": "\u041a\u0440\u044a\u0441\u0442\u043e\u0432\u0430 \u0432\u0430\u0434\u0430",
    "Center": "\u0426\u0435\u043d\u0442\u044a\u0440",
    "Boyana": "\u0411\u043e\u044f\u043d\u0430",
    "Studentski grad": "\u0421\u0442\u0443\u0434\u0435\u043d\u0442\u0441\u043a\u0438 \u0433\u0440\u0430\u0434",
    "Ovcha kupel": "\u041e\u0432\u0447\u0430 \u043a\u0443\u043f\u0435\u043b",
    "Lyulin": "\u041b\u044e\u043b\u0438\u043d",
    "Pancharevo": "\u041f\u0430\u043d\u0447\u0430\u0440\u0435\u0432\u043e",
    "Vitosha": "\u0412\u0438\u0442\u043e\u0448\u0430",
    "Nadezhda": "\u041d\u0430\u0434\u0435\u0436\u0434\u0430",
    "Kremikovtsi": "\u041a\u0440\u0435\u043c\u0438\u043a\u043e\u0432\u0446\u0438",
    "Iskar": "\u0418\u0441\u043a\u044a\u0440",
    "Vrabnitsa": "\u0412\u0440\u044a\u0431\u043d\u0438\u0446\u0430",
    "Dragalevtsi": "\u0414\u0440\u0430\u0433\u0430\u043b\u0435\u0432\u0446\u0438",
    "Simeonovo": "\u0421\u0438\u043c\u0435\u043e\u043d\u043e\u0432\u043e",
    "Manastirski livadi": "\u041c\u0430\u043d\u0430\u0441\u0442\u0438\u0440\u0441\u043a\u0438 \u043b\u0438\u0432\u0430\u0434\u0438",
    "Iztok": "\u0418\u0437\u0442\u043e\u043a",
    "Izgrev": "\u0418\u0437\u0433\u0440\u0435\u0432",
    "Geo Milev": "\u0413\u0435\u043e \u041c\u0438\u043b\u0435\u0432",
    "Slatina": "\u0421\u043b\u0430\u0442\u0438\u043d\u0430",
    "Lagera": "\u041b\u0430\u0433\u0435\u0440\u0430",
    "Krasno selo": "\u041a\u0440\u0430\u0441\u043d\u043e \u0441\u0435\u043b\u043e",
    "Druzhba": "\u0414\u0440\u0443\u0436\u0431\u0430",
}


def canonicalize_district(value: str, *, city: str | None = None) -> str:
    cleaned = value.strip()
    if not cleaned:
        return cleaned
    if city == "Sofia":
        return SOFIA_DISTRICT_ALIASES.get(cleaned, cleaned)
    return cleaned
