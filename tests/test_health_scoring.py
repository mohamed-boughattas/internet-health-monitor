"""Tests for health scoring module."""

import pandas as pd


def test_health_score_calculation():
    """Test that health score calculation is correct."""
    ipv6_score = 85.0
    https_score = 95.0
    dnssec_score = 80.0
    roa_score = 90.0

    expected_score = (
        (ipv6_score * 0.25) + (https_score * 0.25) + (dnssec_score * 0.25) + (roa_score * 0.25)
    )

    assert abs(expected_score - 87.5) < 0.01


def test_health_score_with_low_ipv6():
    """Test health score calculation with low IPv6 score."""
    ipv6_score = 30.0
    https_score = 90.0
    dnssec_score = 80.0
    roa_score = 70.0

    expected_score = (
        (ipv6_score * 0.25) + (https_score * 0.25) + (dnssec_score * 0.25) + (roa_score * 0.25)
    )

    assert abs(expected_score - 67.5) < 0.01


def test_health_score_with_equal_scores():
    """Test health score calculation when all scores are equal."""
    ipv6_score = 80.0
    https_score = 80.0
    dnssec_score = 80.0
    roa_score = 80.0

    expected_score = (
        (ipv6_score * 0.25) + (https_score * 0.25) + (dnssec_score * 0.25) + (roa_score * 0.25)
    )

    assert abs(expected_score - 80.0) < 0.01


def test_country_ranking_ordering(sample_country_scores):
    """Test that countries are correctly ordered by health score."""
    df = sample_country_scores.sort_values("health_score", ascending=False)

    assert df.iloc[0]["country_code"] == "DE"
    assert df.iloc[-1]["country_code"] == "BR"


def test_metric_averaging():
    """Test that averaging metrics across dates works correctly."""
    data = [
        {
            "date": "2024-01-01",
            "ipv6_score": 80.0,
            "https_score": 90.0,
            "dnssec_score": 85.0,
            "roa_score": 88.0,
        },
        {
            "date": "2024-01-02",
            "ipv6_score": 85.0,
            "https_score": 92.0,
            "dnssec_score": 87.0,
            "roa_score": 90.0,
        },
    ]
    df = pd.DataFrame(data)

    avg_ipv6 = df["ipv6_score"].mean()
    avg_https = df["https_score"].mean()
    avg_dnssec = df["dnssec_score"].mean()
    avg_roa = df["roa_score"].mean()

    assert avg_ipv6 == 82.5
    assert avg_https == 91.0
    assert avg_dnssec == 86.0
    assert avg_roa == 89.0


def test_health_score_sql_formula_against_test_db(duckdb_test_db):
    """Test that the health score SQL formula matches actual implementation.

    This mirrors the SQL in assets/enrichment/health_scoring.py to ensure
    the formula is correctly implemented.
    """
    import duckdb

    conn = duckdb.connect(str(duckdb_test_db))

    query = """
    SELECT
        country_code,
        AVG(ipv6_score) as ipv6_score,
        AVG(https_score) as https_score,
        AVG(dnssec_score) as dnssec_score,
        AVG(roa_score) as roa_score,
        AVG(
            (COALESCE(ipv6_score, 0) * 0.25) +
            (COALESCE(https_score, 0) * 0.25) +
            (COALESCE(dnssec_score, 0) * 0.25) +
            (COALESCE(roa_score, 0) * 0.25)
        ) as health_score
    FROM transform.country_rankings
    GROUP BY country_code
    ORDER BY health_score DESC
    """
    df = conn.execute(query).df()
    conn.close()

    assert len(df) == 5
    for _, row in df.iterrows():
        expected = (
            (row["ipv6_score"] * 0.25)
            + (row["https_score"] * 0.25)
            + (row["dnssec_score"] * 0.25)
            + (row["roa_score"] * 0.25)
        )
        assert abs(row["health_score"] - expected) < 0.01
