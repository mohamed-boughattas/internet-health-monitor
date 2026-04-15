/* @bruin

name: staging.https_combined
type: duckdb.sql
materialization:
  type: table
depends:
  - raw.https_AE
  - raw.https_AU
  - raw.https_BE
  - raw.https_BR
  - raw.https_CA
  - raw.https_CH
  - raw.https_CN
  - raw.https_DE
  - raw.https_DK
  - raw.https_DZ
  - raw.https_ES
  - raw.https_FI
  - raw.https_FR
  - raw.https_GB
  - raw.https_HR
  - raw.https_ID
  - raw.https_IN
  - raw.https_IT
  - raw.https_JP
  - raw.https_LU
  - raw.https_MA
  - raw.https_NL
  - raw.https_NO
  - raw.https_PT
  - raw.https_QA
  - raw.https_RU
  - raw.https_SA
  - raw.https_SE
  - raw.https_TN
  - raw.https_US
  - raw.https_ZA

@bruin */

SELECT date, value * 100 AS https_score, 'AE' AS country_code FROM raw.https_AE
UNION ALL
SELECT date, value * 100 AS https_score, 'AU' AS country_code FROM raw.https_AU
UNION ALL
SELECT date, value * 100 AS https_score, 'BE' AS country_code FROM raw.https_BE
UNION ALL
SELECT date, value * 100 AS https_score, 'BR' AS country_code FROM raw.https_BR
UNION ALL
SELECT date, value * 100 AS https_score, 'CA' AS country_code FROM raw.https_CA
UNION ALL
SELECT date, value * 100 AS https_score, 'CH' AS country_code FROM raw.https_CH
UNION ALL
SELECT date, value * 100 AS https_score, 'CN' AS country_code FROM raw.https_CN
UNION ALL
SELECT date, value * 100 AS https_score, 'DE' AS country_code FROM raw.https_DE
UNION ALL
SELECT date, value * 100 AS https_score, 'DK' AS country_code FROM raw.https_DK
UNION ALL
SELECT date, value * 100 AS https_score, 'DZ' AS country_code FROM raw.https_DZ
UNION ALL
SELECT date, value * 100 AS https_score, 'ES' AS country_code FROM raw.https_ES
UNION ALL
SELECT date, value * 100 AS https_score, 'FI' AS country_code FROM raw.https_FI
UNION ALL
SELECT date, value * 100 AS https_score, 'FR' AS country_code FROM raw.https_FR
UNION ALL
SELECT date, value * 100 AS https_score, 'GB' AS country_code FROM raw.https_GB
UNION ALL
SELECT date, value * 100 AS https_score, 'HR' AS country_code FROM raw.https_HR
UNION ALL
SELECT date, value * 100 AS https_score, 'ID' AS country_code FROM raw.https_ID
UNION ALL
SELECT date, value * 100 AS https_score, 'IN' AS country_code FROM raw.https_IN
UNION ALL
SELECT date, value * 100 AS https_score, 'IT' AS country_code FROM raw.https_IT
UNION ALL
SELECT date, value * 100 AS https_score, 'JP' AS country_code FROM raw.https_JP
UNION ALL
SELECT date, value * 100 AS https_score, 'LU' AS country_code FROM raw.https_LU
UNION ALL
SELECT date, value * 100 AS https_score, 'MA' AS country_code FROM raw.https_MA
UNION ALL
SELECT date, value * 100 AS https_score, 'NL' AS country_code FROM raw.https_NL
UNION ALL
SELECT date, value * 100 AS https_score, 'NO' AS country_code FROM raw.https_NO
UNION ALL
SELECT date, value * 100 AS https_score, 'PT' AS country_code FROM raw.https_PT
UNION ALL
SELECT date, value * 100 AS https_score, 'QA' AS country_code FROM raw.https_QA
UNION ALL
SELECT date, value * 100 AS https_score, 'RU' AS country_code FROM raw.https_RU
UNION ALL
SELECT date, value * 100 AS https_score, 'SA' AS country_code FROM raw.https_SA
UNION ALL
SELECT date, value * 100 AS https_score, 'SE' AS country_code FROM raw.https_SE
UNION ALL
SELECT date, value * 100 AS https_score, 'TN' AS country_code FROM raw.https_TN
UNION ALL
SELECT date, value * 100 AS https_score, 'US' AS country_code FROM raw.https_US
UNION ALL
SELECT date, value * 100 AS https_score, 'ZA' AS country_code FROM raw.https_ZA
