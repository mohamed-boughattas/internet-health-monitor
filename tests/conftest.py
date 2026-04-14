"""Pytest configuration and fixtures.

This module contains shared pytest fixtures for the test suite,
including sample data and test database setup.

Fixtures are automatically available to all tests via pytest's fixture
discovery. No import is needed - pytest injects them by name.
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
        A DataFrame with sample health metric data for 5 countries
        including all required columns for testing.
    """
    return pd.DataFrame(
        {
            "country_code": ["US", "DE", "JP", "IN", "BR"],
            "health_score": [59.2, 80.1, 59.0, 65.7, 54.9],
            "ipv6_score": [53.4, 64.0, 53.7, 72.4, 49.7],
            "https_score": [94.8, 89.5, 91.3, 43.8, 82.5],
            "dnssec_score": [36.6, 79.6, 13.7, 56.6, 51.4],
            "roa_score": [51.9, 87.5, 77.1, 90.0, 36.2],
            "date": pd.to_datetime(["2024-01-01"] * 5),
        }
    )


@pytest.fixture(scope="session")
def duckdb_test_db():
    """Create a temporary DuckDB database with test data.

    This fixture creates a session-scoped temporary DuckDB database
    populated with realistic test data matching the pipeline schema.
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
        country_data = [
            ("US", 59.2, 53.4, 94.8, 36.6, 51.9, "2024-01-01"),
            ("DE", 80.1, 64.0, 89.5, 79.6, 87.5, "2024-01-01"),
            ("BR", 54.9, 49.7, 82.5, 51.4, 36.2, "2024-01-01"),
            ("IN", 65.7, 72.4, 43.8, 56.6, 90.0, "2024-01-01"),
            ("JP", 59.0, 53.7, 91.3, 13.7, 77.1, "2024-01-01"),
        ]
        for row in country_data:
            conn.execute(
                "INSERT INTO marts.country_rankings VALUES (?, ?, ?, ?, ?, ?, ?)",
                row,
            )

        conn.execute("""
            CREATE TABLE staging.https_combined (
                date DATE,
                https_score DOUBLE,
                country_code VARCHAR
            )
        """)
        https_data = []
        for date in ["2024-01-01", "2024-01-02", "2024-01-03"]:
            for cc, score in [("US", 94.8), ("DE", 89.5), ("BR", 82.5), ("IN", 43.8), ("JP", 91.3)]:
                https_data.append((date, score, cc))
        for row in https_data:
            conn.execute(
                "INSERT INTO staging.https_combined VALUES (?, ?, ?)",
                row,
            )

        conn.execute("""
            CREATE TABLE staging.dnssec_combined (
                date DATE,
                dnssec_score DOUBLE,
                country_code VARCHAR
            )
        """)
        dnssec_data = []
        for date in ["2024-01-01", "2024-01-02", "2024-01-03"]:
            for cc, score in [("US", 36.6), ("DE", 79.6), ("BR", 51.4), ("IN", 56.6), ("JP", 13.7)]:
                dnssec_data.append((date, score, cc))
        for row in dnssec_data:
            conn.execute(
                "INSERT INTO staging.dnssec_combined VALUES (?, ?, ?)",
                row,
            )

        conn.execute("""
            CREATE TABLE staging.roa_combined (
                date DATE,
                roa_score DOUBLE,
                country_code VARCHAR
            )
        """)
        roa_data = []
        for date in ["2024-01-01", "2024-01-02", "2024-01-03"]:
            for cc, score in [("US", 51.9), ("DE", 87.5), ("BR", 36.2), ("IN", 90.0), ("JP", 77.1)]:
                roa_data.append((date, score, cc))
        for row in roa_data:
            conn.execute(
                "INSERT INTO staging.roa_combined VALUES (?, ?, ?)",
                row,
            )

        conn.execute("""
            CREATE TABLE staging.ipv6_combined (
                date DATE,
                ipv6_score DOUBLE,
                country_code VARCHAR
            )
        """)
        ipv6_data = [
            ("2024-01-01", 53.4, "US"),
            ("2024-01-01", 64.0, "DE"),
            ("2024-01-01", 49.7, "BR"),
            ("2024-01-01", 72.4, "IN"),
            ("2024-01-01", 53.7, "JP"),
        ]
        for row in ipv6_data:
            conn.execute(
                "INSERT INTO staging.ipv6_combined VALUES (?, ?, ?)",
                row,
            )

        conn.execute("""
            CREATE TABLE staging.net_loss_combined (
                date DATE,
                country VARCHAR,
                duration DOUBLE,
                shutdown__gdp DOUBLE,
                freedom_score DOUBLE
            )
        """)
        net_loss_data = [
            ("2024-01-15", "United States", 72.0, 500.0, 50.0),
            ("2024-02-20", "Germany", 0.0, 0.0, 100.0),
            ("2024-03-10", "India", 48.0, 200.0, 60.0),
        ]
        for row in net_loss_data:
            conn.execute(
                "INSERT INTO staging.net_loss_combined VALUES (?, ?, ?, ?, ?)",
                row,
            )

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
        summary_data = [
            ("2024-01-01", "US", 53.4, 94.8, 36.6, 51.9, 59.2),
            ("2024-01-01", "DE", 64.0, 89.5, 79.6, 87.5, 80.1),
            ("2024-01-01", "BR", 49.7, 82.5, 51.4, 36.2, 54.9),
            ("2024-01-01", "IN", 72.4, 43.8, 56.6, 90.0, 65.7),
            ("2024-01-01", "JP", 53.7, 91.3, 13.7, 77.1, 59.0),
        ]
        for row in summary_data:
            conn.execute(
                "INSERT INTO marts.internet_health_summary VALUES (?, ?, ?, ?, ?, ?, ?)",
                row,
            )

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
            CREATE TABLE staging.net_loss_combined (
                date DATE,
                country VARCHAR,
                duration DOUBLE,
                shutdown__gdp DOUBLE,
                freedom_score DOUBLE
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
