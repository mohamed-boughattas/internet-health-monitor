#!/usr/bin/env python3
"""CLI utility for looking up ISO country codes.

Usage:
    python scripts/countries.py search QUERY   Search by name (case-insensitive substring)
    python scripts/countries.py list            List all 249 ISO countries
    python scripts/countries.py tracked         List tracked countries from config/countries.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pycountry
import yaml


def search(query: str) -> None:
    """Case-insensitive substring search across all pycountry countries.

    Args:
        query: Substring to search for in country names (case-insensitive).

    Prints all matching countries in "CC — Name (ISO3)" format.
    Exits with code 1 if no matches are found.
    """
    query_lower = query.lower()
    matches = [
        (c.alpha_2, c.name, c.alpha_3) for c in pycountry.countries if query_lower in c.name.lower()
    ]
    if not matches:
        print(f"No matches found for: {query}")
        sys.exit(1)
    for cc, name, iso3 in matches:
        print(f"{cc} — {name} ({iso3})")


def list_all() -> None:
    """List all 249 ISO countries sorted by code."""
    countries = sorted(pycountry.countries, key=lambda c: c.alpha_2)
    for c in countries:
        print(f"{c.alpha_2} — {c.name} ({c.alpha_3})")
    print(f"\n{len(countries)} countries total.")


def list_tracked() -> None:
    """List countries tracked in config/countries.yaml."""
    config_path = Path(__file__).parent.parent / "config" / "countries.yaml"
    data = yaml.safe_load(config_path.read_text())["TRACKED_COUNTRIES"]
    n = len(data)
    print(f"{n} tracked countries:")
    for cc in sorted(data):
        entry = data[cc]
        print(f"  {cc} — {entry['name']} ({entry['iso_alpha3']})")


def main() -> None:
    """Parse CLI arguments and dispatch to the appropriate subcommand."""
    parser = argparse.ArgumentParser(description="ISO country code lookup utility.")
    parser.add_argument("command", choices=["search", "list", "tracked"])
    parser.add_argument("query", nargs="?", default="", help="Search term (for 'search' command)")
    args = parser.parse_args()

    if args.command == "search":
        if not args.query:
            sys.exit("Usage: countries.py search QUERY")
        search(args.query)
    elif args.command == "list":
        list_all()
    elif args.command == "tracked":
        list_tracked()


if __name__ == "__main__":
    main()
