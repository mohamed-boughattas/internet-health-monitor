/* @bruin

name: staging.dnssec_combined
type: duckdb.sql
materialization:
  type: table
depends:
 - raw.dnssec_validation_US
 - raw.dnssec_validation_DE
 - raw.dnssec_validation_BR
 - raw.dnssec_validation_IN
 - raw.dnssec_validation_JP
columns:
  - name: date
    type: date
  - name: dnssec_score
    type: float
  - name: country_code
    type: varchar

@bruin */

SELECT date, value * 100 AS dnssec_score, 'US' AS country_code FROM raw.dnssec_validation_US
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'DE' AS country_code FROM raw.dnssec_validation_DE
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'BR' AS country_code FROM raw.dnssec_validation_BR
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'IN' AS country_code FROM raw.dnssec_validation_IN
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'JP' AS country_code FROM raw.dnssec_validation_JP
