/* @bruin

name: transform.internet_health_summary
type: duckdb.sql
materialization:
  type: table
depends:
 - transform.ipv6_combined
 - transform.https_combined
 - transform.dnssec_combined
 - transform.roa_combined
columns:
  - name: date
    type: date
  - name: country_code
    type: varchar
  - name: ipv6_score
    type: float
  - name: https_score
    type: float
  - name: dnssec_score
    type: float
  - name: roa_score
    type: float

@bruin */

SELECT
    ipv6.date,
    ipv6.country_code,
    ipv6.ipv6_score,
    monthly_https.https_score,
    monthly_dnssec.dnssec_score,
    monthly_roa.roa_score
FROM transform.ipv6_combined ipv6
LEFT JOIN (
    SELECT
        DATE_TRUNC('month', date) AS date,
        country_code,
        AVG(https_score) AS https_score
    FROM transform.https_combined
    GROUP BY DATE_TRUNC('month', date), country_code
) monthly_https
    ON ipv6.date = monthly_https.date
    AND ipv6.country_code = monthly_https.country_code
LEFT JOIN (
    SELECT
        DATE_TRUNC('month', date) AS date,
        country_code,
        AVG(dnssec_score) AS dnssec_score
    FROM transform.dnssec_combined
    GROUP BY DATE_TRUNC('month', date), country_code
) monthly_dnssec
    ON ipv6.date = monthly_dnssec.date
    AND ipv6.country_code = monthly_dnssec.country_code
LEFT JOIN (
    SELECT
        DATE_TRUNC('month', date) AS date,
        country_code,
        AVG(roa_score) AS roa_score
    FROM transform.roa_combined
    GROUP BY DATE_TRUNC('month', date), country_code
) monthly_roa
    ON ipv6.date = monthly_roa.date
    AND ipv6.country_code = monthly_roa.country_code
