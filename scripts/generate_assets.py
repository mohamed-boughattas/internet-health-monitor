#!/usr/bin/env python3
"""Generate pipeline assets from config/countries.yaml.

This script reads TRACKED_COUNTRIES and ISO_ALPHA3 from config/countries.yaml
(the single source of truth) and generates:

  - assets/ingestion/{ipv6,https,dnssec_validation,roa_4,roa_6}/*.yml
  - assets/transformations/{ipv6,https,dnssec}_combined.sql
  - assets/transformations/roa_combined.sql
  - pipeline.yml
  - tests/conftest.py

Usage:
    python scripts/generate_assets.py                    # Regenerate all assets
    python scripts/generate_assets.py --add MA Morocco MAR  # Add country then regenerate
    python scripts/generate_assets.py --check            # Exit 1 if generated files are stale

The script is idempotent — safe to run any time.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import string
import sys
from pathlib import Path

import pycountry
import yaml

ROOT = Path(__file__).parent.parent
INGESTION_DIR = ROOT / "assets" / "ingestion"
TRANSFORM_DIR = ROOT / "assets" / "transformations"
CONFIG_YAML = ROOT / "config" / "countries.yaml"
PIPELINE_YML = ROOT / "pipeline.yml"

METRIC_SUBDIRS = [
    ("ipv6", "ipv6", "ipv6"),
    ("https", "https", "https"),
    ("dnssec_validation", "dnssec_validation", "dnssec_validation"),
    ("roa_4", "roa:4", "roa_4"),
    ("roa_6", "roa:6", "roa_6"),
]


def load_constants() -> tuple[dict[str, str], dict[str, str]]:
    """Load TRACKED_COUNTRIES and ISO_ALPHA3 from config/countries.yaml.

    Returns:
        A tuple containing two dictionaries: (TRACKED_COUNTRIES, ISO_ALPHA3).
        TRACKED_COUNTRIES maps country codes to country names.
        ISO_ALPHA3 maps country codes to ISO alpha-3 codes.
    """
    data = yaml.safe_load(CONFIG_YAML.read_text())["TRACKED_COUNTRIES"]
    countries = {cc: v["name"] for cc, v in data.items()}
    iso = {cc: v["iso_alpha3"] for cc, v in data.items()}
    return countries, iso


def _country_score(cc: str, metric: str) -> float:
    """Generate a deterministic score in the 10-95 range for test fixtures.

    Args:
        cc: The country code.
        metric: The metric name.

    Returns:
        A deterministic float score between 10 and 95.
    """
    seed = hashlib.md5(f"{cc}-{metric}".encode()).hexdigest()
    return round(float(int(seed[:8], 16) % 8500) / 100 + 10, 1)


# ---------------------------------------------------------------------------
# Ingestion assets
# ---------------------------------------------------------------------------

INGESTION_TPL = string.Template("""name: raw.${metric_name}_${cc}
type: ingestr
connection: duckdb-default

materialization:
  type: table
  strategy: delete+insert
  incremental_key: date

columns:
  - name: date
    type: date
    primary_key: true
  - name: value
    type: float

parameters:
  source_connection: isoc-pulse-default
  source_table: "${source_table}"
  destination: duckdb
""")


def generate_ingestion_assets(countries: dict[str, str]) -> None:
    """Delete and recreate all ingestion YAML files per metric subfolder.

    Args:
        countries: A dictionary mapping country codes to country names.
    """
    for metric_dir, source_table_metric, raw_metric_name in METRIC_SUBDIRS:
        subdir = INGESTION_DIR / metric_dir
        subdir.mkdir(parents=True, exist_ok=True)

        for cc in countries:
            source_table = f"{source_table_metric}:{cc}"
            content = INGESTION_TPL.substitute(
                metric_name=raw_metric_name,
                cc=cc,
                source_table=source_table,
            )
            (subdir / f"{raw_metric_name}_{cc}.asset.yml").write_text(content)

    print(f"Generated {len(countries) * len(METRIC_SUBDIRS)} ingestion assets.")


# ---------------------------------------------------------------------------
# SQL transforms
# ---------------------------------------------------------------------------


def generate_combined_sql(
    output_path: Path,
    metric_dir: str,
    score_col: str,
    countries: dict[str, str],
) -> None:
    """Generate a simple {metric}_combined.sql (UNION ALL per country).

    Args:
        output_path: The path to write the SQL file to.
        metric_dir: The metric directory name.
        score_col: The score column name.
        countries: A dictionary mapping country codes to country names.
    """
    table_name = f"staging.{metric_dir}_combined"
    depends = "\n  - ".join(f"raw.{metric_dir}_{cc}" for cc in sorted(countries))

    union_blocks = "\nUNION ALL\n".join(
        f"SELECT date, value * 100 AS {score_col}, '{cc}' AS country_code "
        f"FROM raw.{metric_dir}_{cc}"
        for cc in sorted(countries)
    )

    content = f"""/* @bruin

name: {table_name}
type: duckdb.sql
materialization:
  type: table
depends:
  - {depends}

@bruin */

{union_blocks}
"""
    output_path.write_text(content)


def generate_roa_combined_sql(output_path: Path, countries: dict[str, str]) -> None:
    """Generate roa_combined.sql (IPv4+IPv6 merged per country).

    Args:
        output_path: The path to write the SQL file to.
        countries: A dictionary mapping country codes to country names.
    """
    depends_4 = "\n  - ".join(f"raw.roa_4_{cc}" for cc in sorted(countries))
    depends_6 = "\n  - ".join(f"raw.roa_6_{cc}" for cc in sorted(countries))

    union_blocks = "\n    UNION ALL\n    ".join(
        f"""SELECT date, '{cc}' AS country_code,\n           """
        f"""(SELECT value FROM raw.roa_4_{cc} WHERE date = d.date) AS ipv4_value,\n           """
        f"""(SELECT value FROM raw.roa_6_{cc} WHERE date = d.date) AS ipv6_value\n    """
        f"""FROM (SELECT DISTINCT date FROM raw.roa_4_{cc}) d"""
        for cc in sorted(countries)
    )

    content = f"""/* @bruin

name: staging.roa_combined
type: duckdb.sql
materialization:
  type: table
depends:
  - {depends_4}
  - {depends_6}

@bruin */

SELECT date, (ipv4_value + ipv6_value) / 2 * 100 AS roa_score, country_code FROM (
    {union_blocks}
)
"""
    output_path.write_text(content)


def generate_pipeline_yml(countries: dict[str, str]) -> None:
    """Regenerate pipeline.yml countries list while preserving all other config.

    Args:
        countries: A dictionary mapping country codes to country names.
    """
    src = PIPELINE_YML.read_text()

    country_lines = "\n      - ".join(f'"{cc}"' for cc in sorted(countries))

    new_defaults = f"""variables:
  countries:
    type: array
    items:
      type: string
    default:
      - {country_lines}"""

    src = re.sub(
        r"variables:\s*\n\s*countries:\s*\n\s*type:\s*array\s*\n\s*items:\s*\n\s*type:\s*string\s*\n\s*default:\s*\n(\s*-.*?\n)*",
        new_defaults + "\n",
        src,
        flags=re.DOTALL,
    )
    PIPELINE_YML.write_text(src)


# ---------------------------------------------------------------------------
# Incremental generation (for add-country only)
# ---------------------------------------------------------------------------


def _regenerate_shared(countries: dict[str, str]) -> None:
    """Regenerate the 4 SQL transforms, pipeline.yml, and conftest.py.

    Called by both add-country and remove-country after the countries list changes.

    Args:
        countries: A dictionary mapping country codes to country names.
    """
    print("  Regenerating SQL transforms...")
    generate_combined_sql(TRANSFORM_DIR / "ipv6_combined.sql", "ipv6", "ipv6_score", countries)
    generate_combined_sql(TRANSFORM_DIR / "https_combined.sql", "https", "https_score", countries)
    generate_combined_sql(
        TRANSFORM_DIR / "dnssec_validation_combined.sql",
        "dnssec_validation",
        "dnssec_score",
        countries,
    )
    generate_roa_combined_sql(TRANSFORM_DIR / "roa_combined.sql", countries)

    print("  Updating pipeline.yml...")
    generate_pipeline_yml(countries)

    print("  Regenerating conftest.py...")
    scores = generate_conftest_data(countries)
    generate_conftest(countries, scores)


# ---------------------------------------------------------------------------
# Test fixture generation
# ---------------------------------------------------------------------------

METRICS_SCORED = ["ipv6_score", "https_score", "dnssec_score", "roa_score"]


def generate_conftest_data(
    countries: dict[str, str],
) -> dict[str, dict[str, float]]:
    """Build per-country score dicts from deterministic hash.

    Args:
        countries: A dictionary mapping country codes to country names.

    Returns:
        A dictionary mapping country codes to their metric scores.
    """
    data: dict[str, dict[str, float]] = {}
    for cc in countries:
        scores: dict[str, float] = {}
        for metric in METRICS_SCORED:
            scores[metric] = _country_score(cc, metric)
        ipv6 = scores["ipv6_score"]
        https = scores["https_score"]
        dnssec = scores["dnssec_score"]
        roa = scores["roa_score"]
        scores["health_score"] = round(
            (ipv6 * 0.25) + (https * 0.25) + (dnssec * 0.25) + (roa * 0.25), 3
        )
        data[cc] = scores
    return data


def generate_conftest(countries: dict[str, str], scores: dict[str, dict[str, float]]) -> None:
    """Regenerate tests/conftest.py from TRACKED_COUNTRIES.

    Args:
        countries: A dictionary mapping country codes to country names.
        scores: A dictionary mapping country codes to their metric scores.
    """
    n = len(countries)
    sorted_cc = sorted(countries.keys())

    cc_list = ",\n            ".join(f'"{cc}"' for cc in sorted_cc)
    health_list = ",\n            ".join(str(scores[cc]["health_score"]) for cc in sorted_cc)
    ipv6_list = ",\n            ".join(str(scores[cc]["ipv6_score"]) for cc in sorted_cc)
    https_list = ",\n            ".join(str(scores[cc]["https_score"]) for cc in sorted_cc)
    dnssec_list = ",\n            ".join(str(scores[cc]["dnssec_score"]) for cc in sorted_cc)
    roa_list = ",\n            ".join(str(scores[cc]["roa_score"]) for cc in sorted_cc)

    cr_rows = ",\n            ".join(
        f"('{cc}', {scores[cc]['health_score']}, {scores[cc]['ipv6_score']}, "
        f"{scores[cc]['https_score']}, {scores[cc]['dnssec_score']}, "
        f"{scores[cc]['roa_score']}, '2024-01-01')"
        for cc in sorted_cc
    )

    https_rows = ",\n            ".join(
        f"('{d}', {scores[cc]['https_score']}, '{cc}')"
        for d in ["2024-01-01", "2024-01-02", "2024-01-03"]
        for cc in sorted_cc
    )

    dnssec_rows = ",\n            ".join(
        f"('{d}', {scores[cc]['dnssec_score']}, '{cc}')"
        for d in ["2024-01-01", "2024-01-02", "2024-01-03"]
        for cc in sorted_cc
    )

    roa_rows = ",\n            ".join(
        f"('{d}', {scores[cc]['roa_score']}, '{cc}')"
        for d in ["2024-01-01", "2024-01-02", "2024-01-03"]
        for cc in sorted_cc
    )

    ipv6_rows = ",\n            ".join(
        f"('2024-01-01', {scores[cc]['ipv6_score']}, '{cc}')" for cc in sorted_cc
    )

    summary_rows = ",\n            ".join(
        f"('2024-01-01', '{cc}', {scores[cc]['ipv6_score']}, {scores[cc]['https_score']}, "
        f"{scores[cc]['dnssec_score']}, {scores[cc]['roa_score']}, {scores[cc]['health_score']})"
        for cc in sorted_cc
    )

    content = f'''"""Pytest configuration and fixtures.

Auto-generated from dashboard/constants.py by scripts/generate_assets.py.
DO NOT EDIT MANUALLY — run `just generate` after changing TRACKED_COUNTRIES.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import duckdb
import pandas as pd
import pytest


@pytest.fixture
def sample_country_scores() -> pd.DataFrame:
    """Provide sample country health scores for testing.

    Returns:
        A DataFrame with sample health metric data for all tracked countries
        including all required columns for testing.
    """
    return pd.DataFrame(
        {{
            "country_code": [
            {cc_list}
            ],
            "health_score": [
            {health_list}
            ],
            "ipv6_score": [
            {ipv6_list}
            ],
            "https_score": [
            {https_list}
            ],
            "dnssec_score": [
            {dnssec_list}
            ],
            "roa_score": [
            {roa_list}
            ],
            "date": pd.to_datetime(["2024-01-01"] * {n}),
        }}
    )


@pytest.fixture(scope="session")
def duckdb_test_db():
    """Create a temporary DuckDB database with test data.

    This fixture creates a session-scoped temporary DuckDB database
    populated with deterministic test data matching the pipeline schema.
    It is cleaned up automatically after the test session.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_internet_health.db"
        conn = duckdb.connect(str(db_path))

        conn.execute("CREATE SCHEMA raw")
        conn.execute("CREATE SCHEMA staging")
        conn.execute("CREATE SCHEMA marts")

        conn.execute("""
            CREATE TABLE marts.country_rankings (
                country_code VARCHAR,
                health_score DOUBLE,
                ipv6_score DOUBLE,
                https_score DOUBLE,
                dnssec_score DOUBLE,
                roa_score DOUBLE,
                date DATE
            )
        """)
        conn.execute("""
            INSERT INTO marts.country_rankings
                (country_code, health_score, ipv6_score, https_score, dnssec_score, roa_score, date)
                VALUES
            {cr_rows}
        """)

        conn.execute("""
            CREATE TABLE staging.https_combined (
                date DATE,
                https_score DOUBLE,
                country_code VARCHAR
            )
        """)
        conn.execute("""
            INSERT INTO staging.https_combined (date, https_score, country_code)
                VALUES
            {https_rows}
        """)

        conn.execute("""
            CREATE TABLE staging.dnssec_combined (
                date DATE,
                dnssec_score DOUBLE,
                country_code VARCHAR
            )
        """)
        conn.execute("""
            INSERT INTO staging.dnssec_combined (date, dnssec_score, country_code)
                VALUES
            {dnssec_rows}
        """)

        conn.execute("""
            CREATE TABLE staging.roa_combined (
                date DATE,
                roa_score DOUBLE,
                country_code VARCHAR
            )
        """)
        conn.execute("""
            INSERT INTO staging.roa_combined (date, roa_score, country_code)
                VALUES
            {roa_rows}
        """)

        conn.execute("""
            CREATE TABLE staging.ipv6_combined (
                date DATE,
                ipv6_score DOUBLE,
                country_code VARCHAR
            )
        """)
        conn.execute("""
            INSERT INTO staging.ipv6_combined (date, ipv6_score, country_code)
                VALUES
            {ipv6_rows}
        """)

        conn.execute("""
            CREATE TABLE marts.internet_health_summary (
                date DATE,
                country_code VARCHAR,
                ipv6_score DOUBLE,
                https_score DOUBLE,
                dnssec_score DOUBLE,
                roa_score DOUBLE,
                health_score DOUBLE
            )
        """)
        conn.execute("""
            INSERT INTO marts.internet_health_summary
                (date, country_code, ipv6_score, https_score, dnssec_score, roa_score, health_score)
                VALUES
            {summary_rows}
        """)

        conn.close()
        yield Path(db_path)


@pytest.fixture(scope="session")
def duckdb_empty_db():
    """Create an empty DuckDB database with transform tables but no data.

    Used for testing edge cases like empty tables.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_empty_internet_health.db"
        conn = duckdb.connect(str(db_path))

        conn.execute("CREATE SCHEMA staging")
        conn.execute("CREATE SCHEMA marts")
        conn.execute("""
            CREATE TABLE marts.country_rankings (
                country_code VARCHAR,
                health_score DOUBLE,
                ipv6_score DOUBLE,
                https_score DOUBLE,
                dnssec_score DOUBLE,
                roa_score DOUBLE,
                date DATE
            )
        """)
        conn.execute("""
            CREATE TABLE marts.internet_health_summary (
                date DATE,
                country_code VARCHAR,
                ipv6_score DOUBLE,
                https_score DOUBLE,
                dnssec_score DOUBLE,
                roa_score DOUBLE,
                health_score DOUBLE
            )
        """)
        conn.execute("""
            CREATE TABLE staging.https_combined (
                date DATE,
                https_score DOUBLE,
                country_code VARCHAR
            )
        """)
        conn.execute("""
            CREATE TABLE staging.dnssec_combined (
                date DATE,
                dnssec_score DOUBLE,
                country_code VARCHAR
            )
        """)
        conn.execute("""
            CREATE TABLE staging.roa_combined (
                date DATE,
                roa_score DOUBLE,
                country_code VARCHAR
            )
        """)
        conn.execute("""
            CREATE TABLE staging.ipv6_combined (
                date DATE,
                ipv6_score DOUBLE,
                country_code VARCHAR
            )
        """)
        conn.close()
        yield Path(db_path)
'''
    (ROOT / "tests" / "conftest.py").write_text(content)
    print(f"Generated tests/conftest.py ({n} countries).")


# ---------------------------------------------------------------------------
# Drift detection
# ---------------------------------------------------------------------------


def check_drift(countries: dict[str, str]) -> bool:
    """Return True if any generated file differs from constants.

    Args:
        countries: A dictionary mapping country codes to country names.

    Returns:
        True if any generated file is stale or missing, False otherwise.
    """
    stale = False

    for metric_dir, source_table_metric, raw_metric_name in METRIC_SUBDIRS:
        subdir = INGESTION_DIR / metric_dir
        for cc in countries:
            expected = f"{source_table_metric}:{cc}"
            path = subdir / f"{raw_metric_name}_{cc}.asset.yml"
            if not path.exists():
                print(f"  MISSING: {path}", file=sys.stderr)
                stale = True
                continue
            data = yaml.safe_load(path.read_text())
            actual = data["parameters"]["source_table"]
            if actual != expected:
                print(
                    f"  STALE: {path} — source_table is {actual}, expected {expected}",
                    file=sys.stderr,
                )
                stale = True

    return stale


# ---------------------------------------------------------------------------
# Add/Remove country
# ---------------------------------------------------------------------------


def _add_country_to_constants(cc: str, name: str, iso_alpha3: str) -> bool:
    """Append a new country to config/countries.yaml, preserving comments.

    Args:
        cc: The two-letter country code.
        name: The full country name.
        iso_alpha3: The ISO alpha-3 country code.

    Returns:
        True if the country was added, False if it was already present.
    """
    src = CONFIG_YAML.read_text()
    if f'  "{cc}":\n' in src or f"  {cc}:\n" in src:
        return False
    if not src.endswith("\n"):
        src += "\n"
    src += f'  "{cc}":\n    name: {name}\n    iso_alpha3: {iso_alpha3}\n'
    CONFIG_YAML.write_text(src)
    return True


def _remove_country_from_yaml(cc: str) -> tuple[str, str]:
    """Remove a country from config/countries.yaml.

    Uses text-based removal to preserve YAML comments.
    Handles both quoted and unquoted keys.

    Args:
        cc: The two-letter country code to remove.

    Returns:
        A tuple of (name, iso_alpha3) for the removed country.

    Raises:
        ValueError: If the country is not found in config/countries.yaml.
    """
    src = CONFIG_YAML.read_text()
    data = yaml.safe_load(src)
    tracked = data.get("TRACKED_COUNTRIES", {})
    if cc not in tracked:
        raise ValueError(f"Country code {cc} not found in config/countries.yaml")
    name = tracked[cc]["name"]
    iso_alpha3 = tracked[cc]["iso_alpha3"]

    pattern = f'  "?{re.escape(cc)}"?:\\n    name: .+\\n    iso_alpha3: .+\\n'
    new_src = re.sub(pattern, "", src)
    CONFIG_YAML.write_text(new_src)
    return name, iso_alpha3


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pipeline assets from constants.")
    parser.add_argument(
        "--add",
        nargs="+",
        metavar="CC",
        help="Add one or more countries to config/countries.yaml (e.g., MA PT DK)",
    )
    parser.add_argument(
        "--remove",
        nargs="+",
        metavar="CC",
        help="Remove one or more countries from config/countries.yaml (e.g., MA PT DK)",
    )
    parser.add_argument("--check", action="store_true", help="Exit 1 if generated files are stale")
    args = parser.parse_args()

    if args.add:
        codes = [c.upper() for c in args.add]
        seen = set()
        added_codes: list[str] = []
        for cc in codes:
            if cc in seen:
                continue
            seen.add(cc)
            if len(cc) != 2 or not cc.isalpha():
                print(f"Skipping invalid code: {cc} (must be 2 letters)", file=sys.stderr)
                continue
            try:
                country = pycountry.countries.get(alpha_2=cc)
                name = country.name
                iso_alpha3 = country.alpha_3
            except AttributeError:
                print(f"Unknown country code: {cc} — skipping", file=sys.stderr)
                continue
            added = _add_country_to_constants(cc, name, iso_alpha3)
            if added:
                print(f"Added {cc} ({name}, {iso_alpha3}) to config/countries.yaml")
                added_codes.append(cc)
            else:
                print(f"Skipping {cc} — already tracked.")

        for cc in added_codes:
            for metric_dir, source_table_metric, raw_metric_name in METRIC_SUBDIRS:
                subdir = INGESTION_DIR / metric_dir
                subdir.mkdir(parents=True, exist_ok=True)
                source_table = f"{source_table_metric}:{cc}"
                content = INGESTION_TPL.substitute(
                    metric_name=raw_metric_name,
                    cc=cc,
                    source_table=source_table,
                )
                (subdir / f"{raw_metric_name}_{cc}.asset.yml").write_text(content)
        if added_codes:
            print(f"  Created {len(added_codes) * 5} ingestion assets.")

        countries, _iso = load_constants()
        _regenerate_shared(countries)
        return

    if args.remove:
        codes = [c.upper() for c in args.remove]
        seen = set()
        for cc in codes:
            if cc in seen:
                continue
            seen.add(cc)
            if len(cc) != 2 or not cc.isalpha():
                print(f"Skipping invalid code: {cc} (must be 2 letters)", file=sys.stderr)
                continue
            try:
                name, iso_alpha3 = _remove_country_from_yaml(cc)
            except ValueError as e:
                print(f"{e} — skipping", file=sys.stderr)
                continue
            print(f"Removed {cc} ({name}, {iso_alpha3}) from config/countries.yaml")
            for metric_dir, _source_table_metric, raw_metric_name in METRIC_SUBDIRS:
                path = INGESTION_DIR / metric_dir / f"{raw_metric_name}_{cc}.asset.yml"
                if path.exists():
                    path.unlink()
        countries, _iso = load_constants()
        _regenerate_shared(countries)
        return

    if args.check:
        countries, _iso = load_constants()
        if check_drift(countries):
            sys.exit(1)
        print("No drift detected.")
    else:
        countries, _iso = load_constants()
        n = len(countries)
        print(f"Generating assets for {n} countries: {sorted(countries)}")

        generate_ingestion_assets(countries)
        generate_combined_sql(TRANSFORM_DIR / "ipv6_combined.sql", "ipv6", "ipv6_score", countries)
        generate_combined_sql(
            TRANSFORM_DIR / "https_combined.sql", "https", "https_score", countries
        )
        generate_combined_sql(
            TRANSFORM_DIR / "dnssec_validation_combined.sql",
            "dnssec_validation",
            "dnssec_score",
            countries,
        )
        generate_roa_combined_sql(TRANSFORM_DIR / "roa_combined.sql", countries)
        generate_pipeline_yml(countries)

        scores = generate_conftest_data(countries)
        generate_conftest(countries, scores)


if __name__ == "__main__":
    main()
