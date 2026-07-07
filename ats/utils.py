HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", text).strip()


# ISO-3166 alpha-2 -> country name. location_filter is a plain substring match,
# so a location that carries only a bare ISO code ("Tel Aviv, IL") is silently
# dropped by an "israel" filter. Pullers expand the code so the country name is
# present in the location string.
ISO_COUNTRY = {
    "IL": "Israel", "US": "United States", "GB": "United Kingdom", "DE": "Germany",
    "FR": "France", "IN": "India", "PL": "Poland", "NL": "Netherlands", "CA": "Canada",
    "AU": "Australia", "SG": "Singapore", "ES": "Spain", "IE": "Ireland", "IT": "Italy",
    "JP": "Japan", "BR": "Brazil", "CO": "Colombia", "HK": "Hong Kong", "PT": "Portugal",
    "SE": "Sweden", "CH": "Switzerland", "RO": "Romania", "CZ": "Czech Republic",
}


def expand_country(code: str) -> str:
    """Map a 2-letter ISO-3166 alpha-2 code to its country name; pass through anything else."""
    if not code:
        return code
    return ISO_COUNTRY.get(code.strip().upper(), code)


def qualify_location(location: str) -> str:
    """
    Append the full country name when a location string carries a bare ISO country
    code but not the country name itself (e.g. "Ra'anana, IL, 4366202" -> ".., Israel").
    Fixes the location_filter substring gotcha for ATSes that emit ISO codes.
    """
    if not location:
        return location
    for part in location.split(","):
        code = part.strip()
        if len(code) == 2 and code.upper() in ISO_COUNTRY:
            country = ISO_COUNTRY[code.upper()]
            if country.lower() not in location.lower():
                return f"{location}, {country}"
    return location
