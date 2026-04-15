/* @bruin

name: staging.dnssec_validation_combined
type: duckdb.sql
materialization:
  type: table
depends:
  - raw.dnssec_validation_AE
  - raw.dnssec_validation_AU
  - raw.dnssec_validation_BE
  - raw.dnssec_validation_BR
  - raw.dnssec_validation_CA
  - raw.dnssec_validation_CH
  - raw.dnssec_validation_CN
  - raw.dnssec_validation_DE
  - raw.dnssec_validation_DK
  - raw.dnssec_validation_DZ
  - raw.dnssec_validation_ES
  - raw.dnssec_validation_FI
  - raw.dnssec_validation_FR
  - raw.dnssec_validation_GB
  - raw.dnssec_validation_HR
  - raw.dnssec_validation_ID
  - raw.dnssec_validation_IN
  - raw.dnssec_validation_IT
  - raw.dnssec_validation_JP
  - raw.dnssec_validation_LU
  - raw.dnssec_validation_MA
  - raw.dnssec_validation_NL
  - raw.dnssec_validation_NO
  - raw.dnssec_validation_PT
  - raw.dnssec_validation_QA
  - raw.dnssec_validation_RU
  - raw.dnssec_validation_SA
  - raw.dnssec_validation_SE
  - raw.dnssec_validation_TN
  - raw.dnssec_validation_US
  - raw.dnssec_validation_ZA

@bruin */

SELECT date, value * 100 AS dnssec_score, 'AE' AS country_code FROM raw.dnssec_validation_AE
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'AU' AS country_code FROM raw.dnssec_validation_AU
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'BE' AS country_code FROM raw.dnssec_validation_BE
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'BR' AS country_code FROM raw.dnssec_validation_BR
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'CA' AS country_code FROM raw.dnssec_validation_CA
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'CH' AS country_code FROM raw.dnssec_validation_CH
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'CN' AS country_code FROM raw.dnssec_validation_CN
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'DE' AS country_code FROM raw.dnssec_validation_DE
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'DK' AS country_code FROM raw.dnssec_validation_DK
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'DZ' AS country_code FROM raw.dnssec_validation_DZ
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'ES' AS country_code FROM raw.dnssec_validation_ES
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'FI' AS country_code FROM raw.dnssec_validation_FI
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'FR' AS country_code FROM raw.dnssec_validation_FR
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'GB' AS country_code FROM raw.dnssec_validation_GB
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'HR' AS country_code FROM raw.dnssec_validation_HR
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'ID' AS country_code FROM raw.dnssec_validation_ID
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'IN' AS country_code FROM raw.dnssec_validation_IN
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'IT' AS country_code FROM raw.dnssec_validation_IT
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'JP' AS country_code FROM raw.dnssec_validation_JP
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'LU' AS country_code FROM raw.dnssec_validation_LU
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'MA' AS country_code FROM raw.dnssec_validation_MA
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'NL' AS country_code FROM raw.dnssec_validation_NL
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'NO' AS country_code FROM raw.dnssec_validation_NO
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'PT' AS country_code FROM raw.dnssec_validation_PT
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'QA' AS country_code FROM raw.dnssec_validation_QA
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'RU' AS country_code FROM raw.dnssec_validation_RU
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'SA' AS country_code FROM raw.dnssec_validation_SA
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'SE' AS country_code FROM raw.dnssec_validation_SE
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'TN' AS country_code FROM raw.dnssec_validation_TN
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'US' AS country_code FROM raw.dnssec_validation_US
UNION ALL
SELECT date, value * 100 AS dnssec_score, 'ZA' AS country_code FROM raw.dnssec_validation_ZA
