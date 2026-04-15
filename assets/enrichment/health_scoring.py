"""@bruin
name: marts.health_scoring
type: python
image: python:3.12
connection: duckdb-default
materialization:
  type: table
  strategy: create+replace

depends:
   - marts.country_rankings

columns:
  - name: country_code
    type: string
    primary_key: true
  - name: ipv6_score
    type: float
  - name: https_score
    type: float
  - name: dnssec_score
    type: float
  - name: roa_score
    type: float
  - name: health_score
    type: float
@bruin"""

import duckdb
import pandas as pd


def materialize(**kwargs: object) -> pd.DataFrame:
    """Materialize the health_scoring table from DuckDB.

    Computes per-country averages of all four metric scores and their
    weighted composite health score (25% each).

    Args:
        kwargs: Keyword arguments passed by the Bruin pipeline (unused).

    Returns:
        A DataFrame with one row per country containing country_code,
        ipv6_score, https_score, dnssec_score, roa_score, and health_score.
    """
    conn = duckdb.connect("data/internet_health.db")

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
    FROM marts.country_rankings
    GROUP BY country_code
    ORDER BY health_score DESC
    """

    df = conn.execute(query).df()
    conn.close()

    return df
