"""Database query functions for the dashboard.

This module provides functions to query data from the DuckDB database
for use in the Dash dashboard visualizations.

Usage:
    from dashboard.data import get_global_health_summary, get_country_health_scores

Example:
    >>> df = get_global_health_summary()
    >>> print(df)
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

DB_PATH = Path(__file__).parent.parent.parent / "data" / "internet_health.db"

VALID_METRICS: frozenset[str] = frozenset({"ipv6", "https", "dnssec", "roa"})

METRIC_TABLES: dict[str, str] = {
    "ipv6": "staging.ipv6_combined",
    "https": "staging.https_combined",
    "dnssec": "staging.dnssec_combined",
    "roa": "staging.roa_combined",
}


@contextmanager
def _db_connection() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """Establish a connection to the DuckDB database.

    Yields:
        A DuckDB connection object.

    Raises:
        FileNotFoundError: If the database file does not exist at the expected path.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run the pipeline first.")
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        yield conn
    finally:
        conn.close()


def get_global_health_summary() -> pd.DataFrame:
    """Get global health summary with all metrics averaged across countries.

    Returns:
        A DataFrame containing:
        - ipv6_score: Average IPv6 adoption score (float)
        - https_score: Average HTTPS adoption score (float)
        - dnssec_score: Average DNSSEC validation score (float)
        - roa_score: Average ROA/RPKI score (float)
        - global_health_score: Weighted composite score (float)
    """
    with _db_connection() as conn:
        query = """
        SELECT
            AVG(ipv6_score) as ipv6_score,
            AVG(https_score) as https_score,
            AVG(dnssec_score) as dnssec_score,
            AVG(roa_score) as roa_score,
            AVG(
                (COALESCE(ipv6_score, 0) * 0.25) +
                (COALESCE(https_score, 0) * 0.25) +
                (COALESCE(dnssec_score, 0) * 0.25) +
                (COALESCE(roa_score, 0) * 0.25)
            ) as global_health_score
        FROM marts.country_rankings
        """
        df = conn.execute(query).df()
    return df


def get_country_health_scores() -> pd.DataFrame:
    """Get health scores for all countries.

    Returns:
        A DataFrame containing one row per country with columns:
        - country_code: ISO 3166-1 alpha-2 country code (str)
        - health_score: Composite health score (float)
        - ipv6_score: IPv6 adoption score (float)
        - https_score: HTTPS adoption score (float)
        - dnssec_score: DNSSEC validation score (float)
        - roa_score: ROA/RPKI score (float)
        - date: Data date (date)
    """
    with _db_connection() as conn:
        query = """
        SELECT
            country_code,
            health_score,
            ipv6_score,
            https_score,
            dnssec_score,
            roa_score,
            date
        FROM marts.country_rankings
        ORDER BY health_score DESC
        """
        df = conn.execute(query).df()
    return df


def get_country_list() -> list[str]:
    """Get list of country codes from the database.

    Returns:
        A sorted list of ISO 3166-1 alpha-2 country codes.
    """
    with _db_connection() as conn:
        query = "SELECT DISTINCT country_code FROM marts.country_rankings ORDER BY country_code"
        df = conn.execute(query).df()
    return df["country_code"].tolist()


def get_daily_metric_timeseries(metric: str, country_code: str | None = None) -> pd.DataFrame:
    """Get daily-resolution time series for a specific metric.

    Queries the individual combined tables directly to preserve daily resolution
    for https, dnssec, and roa (which are aggregated to monthly in internet_health_summary).
    IPv6 is monthly only (API provides no daily data).

    Args:
        metric: Metric name ('ipv6', 'https', 'dnssec', 'roa').
        country_code: ISO 3166-1 alpha-2 country code to filter by.
            If None, returns all countries.

    Returns:
        A DataFrame with columns:
        - date: Date of the observation (date)
        - country_code: Country code (str)
        - {metric}_score: Metric value (float)
    """
    if metric not in VALID_METRICS:
        return pd.DataFrame()

    table = METRIC_TABLES[metric]

    with _db_connection() as conn:
        if country_code:
            query = f"""
            SELECT date, country_code, {metric}_score
            FROM {table}
            WHERE country_code = ?
            ORDER BY date
            """
            df = conn.execute(query, [country_code]).df()
        else:
            query = f"""
            SELECT date, country_code, {metric}_score
            FROM {table}
            ORDER BY date
            """
            df = conn.execute(query).df()
    return df


def get_top_bottom_countries(n: int = 5) -> dict[str, list[dict[str, Any]]]:
    """Get top and bottom N countries by health score.

    Args:
        n: Number of countries to return for top and bottom lists.

    Returns:
        A dictionary with 'top' and 'bottom' lists.
    """
    with _db_connection() as conn:
        query = """
        SELECT country_code, health_score
        FROM marts.country_rankings
        ORDER BY health_score DESC
        """
        df = conn.execute(query).df()
    return {
        "top": df.head(n).to_dict("records"),
        "bottom": df.tail(n).to_dict("records"),
    }


def get_net_loss_data() -> pd.DataFrame:
    """Get internet shutdown data across all countries.

    Returns:
        A DataFrame containing:
        - date: Date of the observation (date)
        - country: Country name (str)
        - duration: Shutdown duration in hours (float)
        - shutdown__gdp: GDP impact (float)
        - freedom_score: Computed freedom score (float)
    """
    with _db_connection() as conn:
        query = """
        SELECT date, country, duration, shutdown__gdp, freedom_score
        FROM staging.net_loss_combined
        ORDER BY date DESC, country
        """
        df = conn.execute(query).df()
    return df


def get_shutdown_summary() -> dict[str, Any]:
    """Get aggregate shutdown statistics.

    Returns:
        A dictionary with:
        - total_shutdowns: Total number of shutdown events (int)
        - avg_duration: Average shutdown duration in hours (float)
        - total_gdp_impact: Sum of GDP impact in arbitrary units (float)
        - avg_freedom_score: Average freedom score across all events (float)
    """
    with _db_connection() as conn:
        query = """
        SELECT
            COUNT(*) as total_shutdowns,
            AVG(duration) as avg_duration,
            SUM(shutdown__gdp) as total_gdp_impact,
            AVG(freedom_score) as avg_freedom_score
        FROM staging.net_loss_combined
        """
        row = conn.execute(query).fetchone()
    if not row:
        return {
            "total_shutdowns": 0,
            "avg_duration": 0.0,
            "total_gdp_impact": 0.0,
            "avg_freedom_score": 100.0,
        }
    return {
        "total_shutdowns": int(row[0]) if row[0] is not None else 0,
        "avg_duration": float(row[1]) if row[1] is not None else 0.0,
        "total_gdp_impact": float(row[2]) if row[2] is not None else 0.0,
        "avg_freedom_score": float(row[3]) if row[3] is not None else 100.0,
    }


def get_shutdown_events() -> pd.DataFrame:
    """Get all shutdown events with full details.

    Returns:
        A DataFrame containing all shutdown events with columns:
        - date: Date of the event (date)
        - country: Country name (str)
        - country_code: ISO 3166-1 alpha-2 code (str)
        - duration: Duration in hours (float)
        - shutdown__gdp: GDP impact (float)
        - freedom_score: Computed freedom score (float)
    """
    from dashboard.constants import TRACKED_COUNTRIES

    country_code_map = {v: k for k, v in TRACKED_COUNTRIES.items()}
    with _db_connection() as conn:
        query = """
        SELECT date, country, duration, shutdown__gdp, freedom_score
        FROM staging.net_loss_combined
        ORDER BY date DESC, country
        """
        df = conn.execute(query).df()
    df["country_code"] = df["country"].map(country_code_map)
    return df


def get_last_updated() -> str:
    """Get the most recent data update timestamp.

    Returns:
        A formatted date string (YYYY-MM-DD) of the most recent
        date in the internet_health_summary table, or "Never" if no data.
    """
    try:
        with _db_connection() as conn:
            result = conn.execute("SELECT MAX(date) FROM marts.internet_health_summary").fetchone()
        if result and result[0]:
            return str(result[0])
    except (FileNotFoundError, Exception):
        pass
    return "Never"
