"""Shared constants for the dashboard.

Country data is loaded from config/countries.yaml — the single source of truth.
All other constants are derived from it.
"""

from __future__ import annotations

from pathlib import Path

import yaml

_COUNTRIES_YAML: Path = Path(__file__).parent.parent / "config" / "countries.yaml"

with open(_COUNTRIES_YAML) as _f:
    _raw: dict[str, dict[str, str]] = yaml.safe_load(_f)["TRACKED_COUNTRIES"]

TRACKED_COUNTRIES: dict[str, str] = {cc: v["name"] for cc, v in _raw.items()}

ISO_ALPHA3: dict[str, str] = {cc: v["iso_alpha3"] for cc, v in _raw.items()}

MAP_COUNTRY_CODES: list[str] = list(TRACKED_COUNTRIES.keys())

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
