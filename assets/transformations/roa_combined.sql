/* @bruin

name: staging.roa_combined
type: duckdb.sql
materialization:
  type: table
depends:
  - raw.roa_4_AE
  - raw.roa_4_AU
  - raw.roa_4_BE
  - raw.roa_4_BR
  - raw.roa_4_CA
  - raw.roa_4_CH
  - raw.roa_4_CN
  - raw.roa_4_DE
  - raw.roa_4_DK
  - raw.roa_4_DZ
  - raw.roa_4_ES
  - raw.roa_4_FI
  - raw.roa_4_FR
  - raw.roa_4_GB
  - raw.roa_4_HR
  - raw.roa_4_ID
  - raw.roa_4_IN
  - raw.roa_4_IT
  - raw.roa_4_JP
  - raw.roa_4_LU
  - raw.roa_4_MA
  - raw.roa_4_NL
  - raw.roa_4_NO
  - raw.roa_4_PT
  - raw.roa_4_QA
  - raw.roa_4_RU
  - raw.roa_4_SA
  - raw.roa_4_SE
  - raw.roa_4_TN
  - raw.roa_4_US
  - raw.roa_4_ZA
  - raw.roa_6_AE
  - raw.roa_6_AU
  - raw.roa_6_BE
  - raw.roa_6_BR
  - raw.roa_6_CA
  - raw.roa_6_CH
  - raw.roa_6_CN
  - raw.roa_6_DE
  - raw.roa_6_DK
  - raw.roa_6_DZ
  - raw.roa_6_ES
  - raw.roa_6_FI
  - raw.roa_6_FR
  - raw.roa_6_GB
  - raw.roa_6_HR
  - raw.roa_6_ID
  - raw.roa_6_IN
  - raw.roa_6_IT
  - raw.roa_6_JP
  - raw.roa_6_LU
  - raw.roa_6_MA
  - raw.roa_6_NL
  - raw.roa_6_NO
  - raw.roa_6_PT
  - raw.roa_6_QA
  - raw.roa_6_RU
  - raw.roa_6_SA
  - raw.roa_6_SE
  - raw.roa_6_TN
  - raw.roa_6_US
  - raw.roa_6_ZA

@bruin */

SELECT date, (ipv4_value + ipv6_value) / 2 * 100 AS roa_score, country_code FROM (
    SELECT date, 'AE' AS country_code,
           (SELECT value FROM raw.roa_4_AE WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_AE WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_AE) d
    UNION ALL
    SELECT date, 'AU' AS country_code,
           (SELECT value FROM raw.roa_4_AU WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_AU WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_AU) d
    UNION ALL
    SELECT date, 'BE' AS country_code,
           (SELECT value FROM raw.roa_4_BE WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_BE WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_BE) d
    UNION ALL
    SELECT date, 'BR' AS country_code,
           (SELECT value FROM raw.roa_4_BR WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_BR WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_BR) d
    UNION ALL
    SELECT date, 'CA' AS country_code,
           (SELECT value FROM raw.roa_4_CA WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_CA WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_CA) d
    UNION ALL
    SELECT date, 'CH' AS country_code,
           (SELECT value FROM raw.roa_4_CH WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_CH WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_CH) d
    UNION ALL
    SELECT date, 'CN' AS country_code,
           (SELECT value FROM raw.roa_4_CN WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_CN WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_CN) d
    UNION ALL
    SELECT date, 'DE' AS country_code,
           (SELECT value FROM raw.roa_4_DE WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_DE WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_DE) d
    UNION ALL
    SELECT date, 'DK' AS country_code,
           (SELECT value FROM raw.roa_4_DK WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_DK WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_DK) d
    UNION ALL
    SELECT date, 'DZ' AS country_code,
           (SELECT value FROM raw.roa_4_DZ WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_DZ WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_DZ) d
    UNION ALL
    SELECT date, 'ES' AS country_code,
           (SELECT value FROM raw.roa_4_ES WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_ES WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_ES) d
    UNION ALL
    SELECT date, 'FI' AS country_code,
           (SELECT value FROM raw.roa_4_FI WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_FI WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_FI) d
    UNION ALL
    SELECT date, 'FR' AS country_code,
           (SELECT value FROM raw.roa_4_FR WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_FR WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_FR) d
    UNION ALL
    SELECT date, 'GB' AS country_code,
           (SELECT value FROM raw.roa_4_GB WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_GB WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_GB) d
    UNION ALL
    SELECT date, 'HR' AS country_code,
           (SELECT value FROM raw.roa_4_HR WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_HR WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_HR) d
    UNION ALL
    SELECT date, 'ID' AS country_code,
           (SELECT value FROM raw.roa_4_ID WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_ID WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_ID) d
    UNION ALL
    SELECT date, 'IN' AS country_code,
           (SELECT value FROM raw.roa_4_IN WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_IN WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_IN) d
    UNION ALL
    SELECT date, 'IT' AS country_code,
           (SELECT value FROM raw.roa_4_IT WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_IT WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_IT) d
    UNION ALL
    SELECT date, 'JP' AS country_code,
           (SELECT value FROM raw.roa_4_JP WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_JP WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_JP) d
    UNION ALL
    SELECT date, 'LU' AS country_code,
           (SELECT value FROM raw.roa_4_LU WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_LU WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_LU) d
    UNION ALL
    SELECT date, 'MA' AS country_code,
           (SELECT value FROM raw.roa_4_MA WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_MA WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_MA) d
    UNION ALL
    SELECT date, 'NL' AS country_code,
           (SELECT value FROM raw.roa_4_NL WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_NL WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_NL) d
    UNION ALL
    SELECT date, 'NO' AS country_code,
           (SELECT value FROM raw.roa_4_NO WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_NO WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_NO) d
    UNION ALL
    SELECT date, 'PT' AS country_code,
           (SELECT value FROM raw.roa_4_PT WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_PT WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_PT) d
    UNION ALL
    SELECT date, 'QA' AS country_code,
           (SELECT value FROM raw.roa_4_QA WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_QA WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_QA) d
    UNION ALL
    SELECT date, 'RU' AS country_code,
           (SELECT value FROM raw.roa_4_RU WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_RU WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_RU) d
    UNION ALL
    SELECT date, 'SA' AS country_code,
           (SELECT value FROM raw.roa_4_SA WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_SA WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_SA) d
    UNION ALL
    SELECT date, 'SE' AS country_code,
           (SELECT value FROM raw.roa_4_SE WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_SE WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_SE) d
    UNION ALL
    SELECT date, 'TN' AS country_code,
           (SELECT value FROM raw.roa_4_TN WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_TN WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_TN) d
    UNION ALL
    SELECT date, 'US' AS country_code,
           (SELECT value FROM raw.roa_4_US WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_US WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_US) d
    UNION ALL
    SELECT date, 'ZA' AS country_code,
           (SELECT value FROM raw.roa_4_ZA WHERE date = d.date) AS ipv4_value,
           (SELECT value FROM raw.roa_6_ZA WHERE date = d.date) AS ipv6_value
    FROM (SELECT DISTINCT date FROM raw.roa_4_ZA) d
)
