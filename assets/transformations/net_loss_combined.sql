/* @bruin

name: transform.net_loss_combined
type: duckdb.sql
materialization:
  type: table
depends:
 - raw.net_loss_shutdown_US
 - raw.net_loss_shutdown_DE
 - raw.net_loss_shutdown_BR
 - raw.net_loss_shutdown_IN
 - raw.net_loss_shutdown_JP
columns:
  - name: date
    type: date
  - name: country
    type: varchar
  - name: duration
    type: float
  - name: shutdown__gdp
    type: float
  - name: freedom_score
    type: float

@bruin */

SELECT
    date,
    country,
    duration,
    shutdown__gdp,
    CASE WHEN risk IS NULL THEN 100.0 ELSE (100.0 - risk) END AS freedom_score
FROM raw.net_loss_shutdown_US
WHERE date >= '2024-01-01'
UNION ALL
SELECT
    date,
    country,
    duration,
    shutdown__gdp,
    CASE WHEN risk IS NULL THEN 100.0 ELSE (100.0 - risk) END AS freedom_score
FROM raw.net_loss_shutdown_DE
WHERE date >= '2024-01-01'
UNION ALL
SELECT
    date,
    country,
    duration,
    shutdown__gdp,
    CASE WHEN risk IS NULL THEN 100.0 ELSE (100.0 - risk) END AS freedom_score
FROM raw.net_loss_shutdown_BR
WHERE date >= '2024-01-01'
UNION ALL
SELECT
    date,
    country,
    duration,
    shutdown__gdp,
    CASE WHEN risk IS NULL THEN 100.0 ELSE (100.0 - risk) END AS freedom_score
FROM raw.net_loss_shutdown_IN
WHERE date >= '2024-01-01'
UNION ALL
SELECT
    date,
    country,
    duration,
    shutdown__gdp,
    100.0 AS freedom_score
FROM raw.net_loss_shutdown_JP
WHERE date >= '2024-01-01'
