/* @bruin

name: transform.https_combined
type: duckdb.sql
materialization:
  type: table
depends:
 - raw.https_US
 - raw.https_DE
 - raw.https_BR
 - raw.https_IN
 - raw.https_JP
columns:
  - name: date
    type: date
  - name: https_score
    type: float
  - name: country_code
    type: varchar

@bruin */

SELECT date, value * 100 AS https_score, 'US' AS country_code FROM raw.https_US
UNION ALL
SELECT date, value * 100 AS https_score, 'DE' AS country_code FROM raw.https_DE
UNION ALL
SELECT date, value * 100 AS https_score, 'BR' AS country_code FROM raw.https_BR
UNION ALL
SELECT date, value * 100 AS https_score, 'IN' AS country_code FROM raw.https_IN
UNION ALL
SELECT date, value * 100 AS https_score, 'JP' AS country_code FROM raw.https_JP
