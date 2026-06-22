from typing import Final

CITY_OPTIONS: Final[dict[str, dict[str, list[str]]]] = {
    "Sofia": {
        "slug": "grad-sofiya",
        "districts": [
            "Лозенец",
            "Младост",
            "Младост 1",
            "Младост 1А",
            "Младост 2",
            "Младост 3",
            "Младост 4",
            "Кръстова вада",
            "Център",
            "Бояна",
            "Студентски град",
            "Овча купел",
            "Люлин",
            "Панчарево",
            "Витоша",
            "Надежда",
            "Кремиковци",
            "Искър",
            "Връбница",
            "Драгалевци",
            "Симеоново",
            "Манастирски ливади",
            "Изток",
            "Изгрев",
            "Гео Милев",
            "Слатина",
            "Лагера",
            "Красно село",
            "Дружба",
        ],
    },
    "Plovdiv": {
        "slug": "grad-plovdiv",
        "districts": ["Kapana", "Trakia", "Kamenitsa", "Smirnenski", "Center"],
    },
    "Varna": {
        "slug": "grad-varna",
        "districts": ["Briz", "Levski", "Chayka", "Center", "Vazrazhdane"],
    },
    "Burgas": {
        "slug": "grad-burgas",
        "districts": ["Lazur", "Sarafovo", "Meden Rudnik", "Center", "Zornitsa"],
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
    "Lozenets": "Лозенец",
    "Mladost": "Младост",
    "Mladost 1": "Младост 1",
    "Mladost 1A": "Младост 1А",
    "Mladost 2": "Младост 2",
    "Mladost 3": "Младост 3",
    "Mladost 4": "Младост 4",
    "Krastova vada": "Кръстова вада",
    "Center": "Център",
    "Boyana": "Бояна",
    "Studentski grad": "Студентски град",
    "Ovcha kupel": "Овча купел",
    "Lyulin": "Люлин",
    "Pancharevo": "Панчарево",
    "Vitosha": "Витоша",
    "Nadezhda": "Надежда",
    "Kremikovtsi": "Кремиковци",
    "Iskar": "Искър",
    "Vrabnitsa": "Връбница",
    "Dragalevtsi": "Драгалевци",
    "Simeonovo": "Симеоново",
    "Manastirski livadi": "Манастирски ливади",
    "Iztok": "Изток",
    "Izgrev": "Изгрев",
    "Geo Milev": "Гео Милев",
    "Slatina": "Слатина",
    "Lagera": "Лагера",
    "Krasno selo": "Красно село",
    "Druzhba": "Дружба",
}


def canonicalize_district(value: str, *, city: str | None = None) -> str:
    cleaned = value.strip()
    if not cleaned:
        return cleaned
    if city == "Sofia":
        return SOFIA_DISTRICT_ALIASES.get(cleaned, cleaned)
    return cleaned
