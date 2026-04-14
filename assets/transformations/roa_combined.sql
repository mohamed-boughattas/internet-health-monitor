/* @bruin

name: transform.roa_combined
type: duckdb.sql
materialization:
  type: table
depends:
 - raw.roa_4_US
 - raw.roa_4_DE
 - raw.roa_4_BR
 - raw.roa_4_IN
 - raw.roa_4_JP
 - raw.roa_6_US
 - raw.roa_6_DE
 - raw.roa_6_BR
 - raw.roa_6_IN
 - raw.roa_6_JP
columns:
  - name: date
    type: date
  - name: roa_score
    type: float
  - name: country_code
    type: varchar

@bruin */

SELECT date, (ipv4_value + ipv6_value) / 2 * 100 AS roa_score, country_code FROM (
    SELECT date, 'US' AS country_code,
           (SELECT value FROM raw.roa_4_US WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_US WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_US) d
    UNION ALL
    SELECT date, 'DE' AS country_code,
           (SELECT value FROM raw.roa_4_DE WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_DE WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_DE) d
    UNION ALL
    SELECT date, 'BR' AS country_code,
           (SELECT value FROM raw.roa_4_BR WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_BR WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_BR) d
    UNION ALL
    SELECT date, 'IN' AS country_code,
           (SELECT value FROM raw.roa_4_IN WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_IN WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_IN) d
    UNION ALL
    SELECT date, 'JP' AS country_code,
           (SELECT value FROM raw.roa_4_JP WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_JP WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_JP) d
)
