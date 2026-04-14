/* @bruin

name: staging.ipv6_combined
type: duckdb.sql
materialization:
  type: table
depends:
 - raw.ipv6_US
 - raw.ipv6_DE
 - raw.ipv6_BR
 - raw.ipv6_IN
 - raw.ipv6_JP
columns:
  - name: date
    type: date
  - name: ipv6_score
    type: float
  - name: country_code
    type: varchar

@bruin */

SELECT date, value * 100 AS ipv6_score, 'US' AS country_code FROM raw.ipv6_US
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'DE' AS country_code FROM raw.ipv6_DE
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'BR' AS country_code FROM raw.ipv6_BR
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'IN' AS country_code FROM raw.ipv6_IN
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'JP' AS country_code FROM raw.ipv6_JP
