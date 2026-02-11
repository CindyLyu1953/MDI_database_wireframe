"""
Configuration file for contextual metadata extraction pipeline.
Contains common constants, country mappings, and utility functions.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_INTERMEDIATE_DIR = BASE_DIR / "data_intermediate"
OUTPUT_DIR = BASE_DIR / "output"
VDEM_DIR = BASE_DIR / "vdem"
INTERNET_FREEDOM_DIR = BASE_DIR / "internet_freedom"
TRUST_IN_NEWS_DIR = BASE_DIR / "trust_in_news"
WGI_DIR = BASE_DIR / "wgi"
WORLDBANK_DIR = BASE_DIR / "worldbank"

# Ensure directories exist
DATA_INTERMEDIATE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Target countries (standard names)
TARGET_COUNTRIES = [
    "Denmark",
    "United States",
    "United Kingdom",
    "Bosnia and Herzegovina",
    "Cyprus",
]

# Country name variations mapping to standard names
COUNTRY_NAME_MAPPING = {
    # Denmark variations
    "denmark": "Denmark",
    "dnk": "Denmark",
    # United States variations
    "united states": "United States",
    "united states of america": "United States",
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "america": "United States",
    # United Kingdom variations
    "united kingdom": "United Kingdom",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "great britain": "United Kingdom",
    "britain": "United Kingdom",
    "gbr": "United Kingdom",
    "england": "United Kingdom",  # Note: England is part of UK
    # Bosnia and Herzegovina variations
    "bosnia and herzegovina": "Bosnia and Herzegovina",
    "bosnia-herzegovina": "Bosnia and Herzegovina",
    "bosnia & herzegovina": "Bosnia and Herzegovina",
    "bosnia": "Bosnia and Herzegovina",
    "bih": "Bosnia and Herzegovina",
    # Cyprus variations
    "cyprus": "Cyprus",
    "cyp": "Cyprus",
}

# ISO3 codes for target countries
COUNTRY_ISO3 = {
    "Denmark": "DNK",
    "United States": "USA",
    "United Kingdom": "GBR",
    "Bosnia and Herzegovina": "BIH",
    "Cyprus": "CYP",
}

# Time range
YEAR_START = 2010
YEAR_END = 2025

# Indicator names mapping
INDICATOR_NAMES = {
    "v2x_libdem": "Liberal Democracy",
    "internet_freedom_score": "Internet Freedom",
    "wgi_pv": "Governance Quality",
    "v2x_delibdem": "Polarization",
    "internet_penetration": "Internet Penetration",
    "election_period": "Election Period",
    "covid_period": "Covid Period",
    "trust_in_news_overall": "Trust in News",
}

# Data sources mapping
INDICATOR_SOURCES = {
    "Liberal Democracy": "V-Dem",
    "Internet Freedom": "Freedom House",
    "Governance Quality": "WGI",
    "Polarization": "V-Dem",
    "Internet Penetration": "World Bank",
    "Election Period": "Manual",
    "Covid Period": "Manual",
    "Trust in News": "Reuters Institute",
}

# COVID period definition (binary: 1 if within period)
COVID_START_YEAR = 2019
COVID_END_YEAR = 2023

# Election years for each country (approximate national elections)
# Parliamentary/Presidential elections
ELECTION_YEARS = {
    "Denmark": [2011, 2015, 2019, 2022],  # Parliamentary
    "United States": [
        2010,
        2012,
        2014,
        2016,
        2018,
        2020,
        2022,
        2024,
    ],  # Congressional/Presidential
    "United Kingdom": [2010, 2015, 2017, 2019, 2024],  # Parliamentary
    "Bosnia and Herzegovina": [2010, 2014, 2018, 2022],  # General elections
    "Cyprus": [2011, 2013, 2016, 2018, 2021, 2023],  # Presidential/Parliamentary
}


def standardize_country_name(name: str) -> str | None:
    """
    Standardize country name to our canonical form.
    Returns None if country is not in our target list.
    """
    if name is None:
        return None

    name_lower = name.lower().strip()

    # Direct match (exact)
    if name_lower in COUNTRY_NAME_MAPPING:
        return COUNTRY_NAME_MAPPING[name_lower]

    # Check if already standard (case-insensitive)
    for target in TARGET_COUNTRIES:
        if name_lower == target.lower():
            return target

    # Try more specific patterns for common variations
    # Only use exact word boundary matching to avoid false positives

    # Denmark
    if name_lower in ["denmark", "dnk", "the kingdom of denmark"]:
        return "Denmark"

    # United States - be very specific to avoid matching "Australia", "Austria" etc.
    if name_lower in [
        "united states",
        "united states of america",
        "usa",
        "u.s.",
        "u.s.a.",
    ]:
        return "United States"

    # United Kingdom - be specific
    if name_lower in [
        "united kingdom",
        "uk",
        "u.k.",
        "great britain",
        "britain",
        "united kingdom of great britain and northern ireland",
        "gbr",
    ]:
        return "United Kingdom"

    # Bosnia and Herzegovina
    if "bosnia" in name_lower and (
        "herzegovina" in name_lower or name_lower == "bosnia"
    ):
        return "Bosnia and Herzegovina"
    if name_lower == "bih":
        return "Bosnia and Herzegovina"

    # Cyprus
    if name_lower in ["cyprus", "cyp", "republic of cyprus"]:
        return "Cyprus"

    return None


def get_iso3(country_name: str) -> str | None:
    """Get ISO3 code for a country name."""
    standard_name = standardize_country_name(country_name)
    if standard_name:
        return COUNTRY_ISO3.get(standard_name)
    return None


def is_covid_period(year: int) -> int:
    """Return 1 if year is in COVID period, 0 otherwise."""
    return 1 if COVID_START_YEAR <= year <= COVID_END_YEAR else 0


def is_election_period(country: str, year: int) -> int:
    """Return 1 if year is an election year for the country, 0 otherwise."""
    standard_name = standardize_country_name(country)
    if standard_name and standard_name in ELECTION_YEARS:
        return 1 if year in ELECTION_YEARS[standard_name] else 0
    return 0
