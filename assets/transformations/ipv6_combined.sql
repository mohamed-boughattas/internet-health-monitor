/* @bruin

name: staging.ipv6_combined
type: duckdb.sql
materialization:
  type: table
depends:
  - raw.ipv6_AE
  - raw.ipv6_AU
  - raw.ipv6_BE
  - raw.ipv6_BR
  - raw.ipv6_CA
  - raw.ipv6_CH
  - raw.ipv6_CN
  - raw.ipv6_DE
  - raw.ipv6_DK
  - raw.ipv6_DZ
  - raw.ipv6_ES
  - raw.ipv6_FI
  - raw.ipv6_FR
  - raw.ipv6_GB
  - raw.ipv6_HR
  - raw.ipv6_ID
  - raw.ipv6_IN
  - raw.ipv6_IT
  - raw.ipv6_JP
  - raw.ipv6_LU
  - raw.ipv6_MA
  - raw.ipv6_NL
  - raw.ipv6_NO
  - raw.ipv6_PT
  - raw.ipv6_QA
  - raw.ipv6_RU
  - raw.ipv6_SA
  - raw.ipv6_SE
  - raw.ipv6_TN
  - raw.ipv6_US
  - raw.ipv6_ZA

@bruin */

SELECT date, value * 100 AS ipv6_score, 'AE' AS country_code FROM raw.ipv6_AE
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'AU' AS country_code FROM raw.ipv6_AU
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'BE' AS country_code FROM raw.ipv6_BE
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'BR' AS country_code FROM raw.ipv6_BR
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'CA' AS country_code FROM raw.ipv6_CA
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'CH' AS country_code FROM raw.ipv6_CH
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'CN' AS country_code FROM raw.ipv6_CN
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'DE' AS country_code FROM raw.ipv6_DE
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'DK' AS country_code FROM raw.ipv6_DK
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'DZ' AS country_code FROM raw.ipv6_DZ
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'ES' AS country_code FROM raw.ipv6_ES
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'FI' AS country_code FROM raw.ipv6_FI
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'FR' AS country_code FROM raw.ipv6_FR
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'GB' AS country_code FROM raw.ipv6_GB
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'HR' AS country_code FROM raw.ipv6_HR
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'ID' AS country_code FROM raw.ipv6_ID
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'IN' AS country_code FROM raw.ipv6_IN
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'IT' AS country_code FROM raw.ipv6_IT
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'JP' AS country_code FROM raw.ipv6_JP
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'LU' AS country_code FROM raw.ipv6_LU
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'MA' AS country_code FROM raw.ipv6_MA
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'NL' AS country_code FROM raw.ipv6_NL
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'NO' AS country_code FROM raw.ipv6_NO
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'PT' AS country_code FROM raw.ipv6_PT
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'QA' AS country_code FROM raw.ipv6_QA
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'RU' AS country_code FROM raw.ipv6_RU
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'SA' AS country_code FROM raw.ipv6_SA
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'SE' AS country_code FROM raw.ipv6_SE
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'TN' AS country_code FROM raw.ipv6_TN
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'US' AS country_code FROM raw.ipv6_US
UNION ALL
SELECT date, value * 100 AS ipv6_score, 'ZA' AS country_code FROM raw.ipv6_ZA
