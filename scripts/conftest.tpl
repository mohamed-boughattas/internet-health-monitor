"""Pytest configuration and fixtures.

Auto-generated from dashboard/constants.py by scripts/generate_assets.py.
DO NOT EDIT MANUALLY — run `just generate` after changing TRACKED_COUNTRIES.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import duckdb
import pandas as pd
import pytest

# Country codes list - replaced by generator
COUNTRY_CODES = []

# Score lists - replaced by generator
HEALTH_SCORES = []
IPV6_SCORES = []
HTTPS_SCORES = []
DNSSEC_SCORES = []
ROA_SCORES = []


@pytest.fixture
def sample_country_scores() -> pd.DataFrame:
    """Provide sample country health scores for testing."""
    return pd.DataFrame(
        {
            "country_code": COUNTRY_CODES,
            "health_score": HEALTH_SCORES,
            "ipv6_score": IPV6_SCORES,
            "https_score": HTTPS_SCORES,
            "dnssec_score": DNSSEC_SCORES,
            "roa_score": ROA_SCORES,
            "date": pd.to_datetime(["2024-01-01"] * len(COUNTRY_CODES)),
        }
    )


@pytest.fixture(scope="session")
def duckdb_test_db():
    """Create a temporary DuckDB database with test data."""
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
        # INSERT statements injected by generator

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

        conn.close()
        yield Path(db_path)


@pytest.fixture(scope="session")
def duckdb_empty_db():
    """Create an empty DuckDB database with transform tables but no data."""
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
