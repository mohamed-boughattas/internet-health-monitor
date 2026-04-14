/* @bruin

name: transform.country_rankings
type: duckdb.sql
materialization:
  type: table
depends:
 - transform.internet_health_summary
columns:
  - name: country_code
    type: varchar
  - name: date
    type: date
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

@bruin */

SELECT
    country_code,
    date,
    ipv6_score,
    https_score,
    dnssec_score,
    roa_score,
    (
        (COALESCE(ipv6_score, 0) * 0.25) +
        (COALESCE(https_score, 0) * 0.25) +
        (COALESCE(dnssec_score, 0) * 0.25) +
        (COALESCE(roa_score, 0) * 0.25)
    ) AS health_score
FROM transform.internet_health_summary
ORDER BY country_code, date DESC
