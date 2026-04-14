"""Shared constants for the dashboard.

This module contains country code constants used across the dashboard
to avoid duplication.
"""

TRACKED_COUNTRIES: dict[str, str] = {
    "US": "United States",
    "DE": "Germany",
    "BR": "Brazil",
    "IN": "India",
    "JP": "Japan",
}

MAP_COUNTRY_CODES: list[str] = list(TRACKED_COUNTRIES.keys())

ISO_ALPHA3: dict[str, str] = {
    "US": "USA",
    "DE": "DEU",
    "BR": "BRA",
    "IN": "IND",
    "JP": "JPN",
}

REVERSE_ISO3: dict[str, str] = {v: k for k, v in ISO_ALPHA3.items()}

METRICS: list[dict[str, str]] = [
    {"label": "IPv6", "value": "ipv6"},
    {"label": "HTTPS", "value": "https"},
    {"label": "DNSSEC", "value": "dnssec"},
    {"label": "ROA/RPKI", "value": "roa"},
]

COUNTRY_OPTIONS: list[dict[str, str]] = [
    {"label": f"{code} - {name}", "value": code} for code, name in TRACKED_COUNTRIES.items()
]
