"""Country code utilities for standardizing country names and ISO codes."""

import pycountry
from typing import Optional


# Manual mappings for countries with non-standard names in data sources
COUNTRY_NAME_MAPPINGS = {
    # Joshua Project naming conventions
    "Korea South": "Korea, Republic of",
    "Korea North": "Korea, Democratic People's Republic of",
    "Congo Democratic Republic": "Congo, The Democratic Republic of the",
    "Congo Republic of the": "Congo",
    "China Hong Kong": "Hong Kong",
    "China Macau": "Macao",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Czechia": "Czechia",
    "Eswatini": "Eswatini",
    "North Macedonia": "North Macedonia",
    "Timor-Leste": "Timor-Leste",
    "West Bank Gaza": "Palestine, State of",
    "Micronesia Federated States": "Micronesia, Federated States of",
    "St Vincent and Grenadines": "Saint Vincent and the Grenadines",
    "Virgin Islands US": "Virgin Islands, U.S.",
    "British Virgin Islands": "Virgin Islands, British",
    "Wallis and Futuna Islands": "Wallis and Futuna",
    "Cocos (Keeling) Islands": "Cocos (Keeling) Islands",
    "Falkland Islands": "Falkland Islands (Malvinas)",
    "Pitcairn Islands": "Pitcairn",
    "Turks and Caicos Islands": "Turks and Caicos Islands",
    "Cayman Islands": "Cayman Islands",
    "Cook Islands": "Cook Islands",
    "Marshall Islands": "Marshall Islands",
    "Solomon Islands": "Solomon Islands",
    "Faroe Islands": "Faroe Islands",
    "Northern Mariana Islands": "Northern Mariana Islands",
    # Territories without ISO codes - use parent country
    "British Indian Ocean Territory": None,  # No standard ISO
    "Christmas Island": "Christmas Island",
    "Norfolk Island": "Norfolk Island",
    "Western Sahara": "Western Sahara",
    "Svalbard": None,  # Part of Norway
    "Saint Helena": "Saint Helena, Ascension and Tristan da Cunha",
    "Saint Pierre and Miquelon": "Saint Pierre and Miquelon",
    "French Guiana": "French Guiana",
    "French Polynesia": "French Polynesia",
    "Guadeloupe": "Guadeloupe",
    "Martinique": "Martinique",
    "Mayotte": "Mayotte",
    "New Caledonia": "New Caledonia",
    "Reunion": "Réunion",
    "Curacao": "Curaçao",
    "Sint Maarten": "Sint Maarten (Dutch part)",
    "Aruba": "Aruba",
}


def get_iso_alpha3(country_name: str) -> Optional[str]:
    """Get ISO 3166-1 alpha-3 code for a country name.

    Args:
        country_name: The country name to look up

    Returns:
        ISO alpha-3 code or None if not found
    """
    if not country_name:
        return None

    # Check manual mappings first
    mapped_name = COUNTRY_NAME_MAPPINGS.get(country_name, country_name)
    if mapped_name is None:
        return None

    # Try direct lookup
    try:
        country = pycountry.countries.get(name=mapped_name)
        if country:
            return country.alpha_3
    except (KeyError, LookupError):
        pass

    # Try fuzzy search
    try:
        results = pycountry.countries.search_fuzzy(mapped_name)
        if results:
            return results[0].alpha_3
    except LookupError:
        pass

    # Try common name lookup
    try:
        country = pycountry.countries.get(common_name=mapped_name)
        if country:
            return country.alpha_3
    except (KeyError, LookupError):
        pass

    return None


def get_country_name(iso_code: str) -> Optional[str]:
    """Get standard country name from ISO code.

    Args:
        iso_code: ISO 3166-1 alpha-2 or alpha-3 code

    Returns:
        Standard country name or None if not found
    """
    if not iso_code:
        return None

    try:
        if len(iso_code) == 2:
            country = pycountry.countries.get(alpha_2=iso_code.upper())
        else:
            country = pycountry.countries.get(alpha_3=iso_code.upper())

        if country:
            return getattr(country, 'common_name', country.name)
    except (KeyError, LookupError):
        pass

    return None


def standardize_country_name(country_name: str) -> str:
    """Standardize a country name to a consistent format.

    Args:
        country_name: Input country name

    Returns:
        Standardized country name
    """
    if not country_name:
        return country_name

    # Check manual mappings
    if country_name in COUNTRY_NAME_MAPPINGS:
        mapped = COUNTRY_NAME_MAPPINGS[country_name]
        if mapped:
            country_name = mapped

    # Try to get ISO code and back to standard name
    iso_code = get_iso_alpha3(country_name)
    if iso_code:
        standard_name = get_country_name(iso_code)
        if standard_name:
            return standard_name

    return country_name


def get_all_country_codes() -> dict:
    """Get a dictionary mapping country names to ISO codes.

    Returns:
        Dict mapping country names to alpha-3 codes
    """
    codes = {}
    for country in pycountry.countries:
        name = getattr(country, 'common_name', country.name)
        codes[name] = country.alpha_3
        codes[country.name] = country.alpha_3

    # Add manual mappings
    for name, mapped in COUNTRY_NAME_MAPPINGS.items():
        if mapped:
            iso = get_iso_alpha3(mapped)
            if iso:
                codes[name] = iso

    return codes
