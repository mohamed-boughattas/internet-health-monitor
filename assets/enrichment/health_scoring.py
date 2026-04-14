"""@bruin
name: transform.health_scoring
type: python
image: python:3.12
connection: duckdb-default
materialization:
  type: table
  strategy: create+replace

depends:
   - transform.country_rankings

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


def materialize(**kwargs):
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
    FROM transform.country_rankings
    GROUP BY country_code
    ORDER BY health_score DESC
    """

    df = conn.execute(query).df()
    conn.close()

    return df
