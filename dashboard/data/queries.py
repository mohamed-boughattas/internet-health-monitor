"""Database query functions for the dashboard.

This module provides functions to query data from the DuckDB database
for use in the Dash dashboard visualizations.

Functions:
    get_global_health_summary: Get global health summary with all metrics averaged.
    get_country_health_scores: Get health scores for all countries (latest date).
    get_country_list: Get list of tracked country codes.
    get_daily_metric_timeseries: Get daily-resolution time series for a specific metric.
    get_top_bottom_countries: Get top and bottom N countries by health score.
    get_last_updated: Get the most recent data update timestamp.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

DB_PATH: Path = Path(__file__).parent.parent.parent / "data" / "internet_health.db"

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
            AVG(roa_score) as roa_score
        FROM marts.country_rankings
        """
        df = conn.execute(query).df()

    score_cols = ["ipv6_score", "https_score", "dnssec_score", "roa_score"]
    weights = [0.25, 0.25, 0.25, 0.25]
    global_scores = []
    for _, row in df.iterrows():
        scores = [row[col] for col in score_cols]
        health = sum(s * w for s, w in zip(scores, weights, strict=True) if pd.notna(s))
        count = sum(1 for s in scores if pd.notna(s))
        if count > 0:
            health = health / sum(weights[:count])
        else:
            health = float("nan")
        global_scores.append(health)

    df = df.copy()
    df["global_health_score"] = global_scores
    return df


def get_country_health_scores() -> pd.DataFrame:
    """Get health scores for all countries (latest date per country).

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
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY country_code
                    ORDER BY date DESC
                ) AS rn
            FROM marts.country_rankings
        )
        WHERE rn = 1
        ORDER BY health_score DESC
        """
        df = conn.execute(query).df()
    return df


def get_country_list() -> list[str]:
    """Get list of tracked country codes.

    Returns:
        A sorted list of ISO 3166-1 alpha-2 country codes.
    """
    from dashboard.constants import TRACKED_COUNTRIES

    return sorted(TRACKED_COUNTRIES.keys())


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
    return {  # pyrefly: ignore[bad-return]
        "top": df.head(n).to_dict("records"),
        "bottom": df.tail(n).to_dict("records"),
    }


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
    except Exception:
        pass
    return "Never"
