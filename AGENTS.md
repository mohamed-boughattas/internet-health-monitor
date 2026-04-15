# Internet Health Monitor - Agent Instructions

## Project Overview

This is a **Bruin-based data pipeline** that ingests internet health metrics from the **Internet Society Pulse API** for 47 countries into **DuckDB**, with SQL transformations, Python enrichment, and an interactive **Dash (Plotly)** visualization dashboard.

## Tech Stack

| Layer | Tool | Version |
|-------|------|---------|
| Pipeline Framework | Bruin | latest |
| Data Warehouse | DuckDB | >=1.0.0 |
| Language | Python | 3.12 |
| Package Manager | uv | latest |
| Linter/Formatter | ruff | >=0.3.0 |
| Type Checker | ty | >=0.0.29 |
| Task Runner | just | latest |
| CI/CD | GitHub Actions | - |
| Testing | pytest | >=7.4.0 |
| Dashboard | Dash + Plotly | >=2.14.0 / >=5.18.0 |
| Containerization | Docker + Compose | - |

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/) — `pip install uv`
- [Bruin CLI](https://bruin-data.github.io/bruin/) — `curl -fsSL https://raw.githubusercontent.com/bruin-data/bruin/main/install.sh | sh`
- [just](https://github.com/casey/just)
- Docker (optional, for dashboard container)
- `ISOC_PULSE_TOKEN` — get one at pulse.internetsociety.org

## Quick Commands

```bash
just                          # List all available commands

# Setup
just setup                    # Install deps + validate pipeline

# Development
just install                  # Install dependencies
just lint                     # Run ruff linter
just format                   # Run ruff formatter
just typecheck                # Run ty type checker
just test                     # Run pytest
just test-cov                 # Run pytest with coverage
just ci                       # Run all CI checks (lint + typecheck + format + test + validate)

# Pipeline
just run-pipeline             # Run Bruin pipeline
just validate                 # Validate Bruin pipeline

# Dashboard
just dashboard                # Launch Dash app (http://localhost:8050)

# Docker
just docker-up                # Start dashboard in Docker
just docker-down              # Stop all services
just docker-build             # Build dashboard image
just docker-logs              # View container logs

# Utilities
just clean                    # Clean generated files
just lock                     # Lock dependencies
just generate                 # Regenerate pipeline assets from countries.yaml
just add-country CC [CC ...] # Add countries + regenerate assets
just remove-country CC [CC]  # Remove countries + regenerate assets
just search-country QUERY     # Search countries by name
just list-countries           # List all 249 ISO countries
just list-tracked             # List tracked countries
just check-drift              # CI drift check
```

## Countries

Data is tracked for 47 countries:

| Code | Country |
|------|---------|
| US | United States |
| DE | Germany |
| BR | Brazil |
| IN | India |
| JP | Japan |
| FR | France |
| ES | Spain |
| NL | Netherlands |
| IT | Italy |
| GB | United Kingdom |
| CH | Switzerland |
| BE | Belgium |
| CA | Canada |
| CN | China |
| AR | Argentina |
| TN | Tunisia |
| DZ | Algeria |
| EG | Egypt |
| AT | Austria |
| AU | Australia |
| LU | Luxembourg |
| ZA | South Africa |
| KR | Korea, Republic of |
| SG | Singapore |
| ID | Indonesia |
| AE | United Arab Emirates |
| SA | Saudi Arabia |
| QA | Qatar |
| SE | Sweden |
| PL | Poland |
| RU | Russian Federation |
| MX | Mexico |
| NZ | New Zealand |
| FI | Finland |
| NO | Norway |
| MA | Morocco |
| PT | Portugal |
| DK | Denmark |
| CO | Colombia |
| CL | Chile |
| CM | Cameroon |
| CZ | Czechia |
| GR | Greece |
| HR | Croatia |
| HU | Hungary |
| NG | Nigeria |
| SN | Senegal |

## Metrics

| Metric | Description | ISOC Pulse Source | Data Frequency |
|--------|-------------|--------------------|----------------|
| **IPv6 Adoption** | Percentage of users who can access via IPv6 | `ipv6:<CC>` | Monthly |
| **HTTPS Adoption** | Percentage of web traffic using HTTPS | `https:<CC>` | Daily |
| **DNSSEC Validation** | Percentage of TLDs with valid DNSSEC | `dnssec_validation:<CC>` | Daily |
| **ROA/RPKI (IPv4)** | Route origin authorization coverage for IPv4 | `roa:4:<CC>` | Daily |
| **ROA/RPKI (IPv6)** | Route origin authorization coverage for IPv6 | `roa:6:<CC>` | Daily |

**Notes**:
- IPv6 is the **driving table** for the summary because it is the only monthly-frequency metric. All other scored metrics (HTTPS, DNSSEC, ROA) are **aggregated from daily to monthly** via `DATE_TRUNC('month', date) + AVG()` before joining in `internet_health_summary.sql`.
- ROA IPv4 and ROA IPv6 are **merged** in `roa_combined.sql` as `(ipv4_value + ipv6_value) / 2` to produce a single `roa_score`.
- **Daily granularity is preserved** for trend lines — `get_daily_metric_timeseries()` queries the individual `*_combined` tables directly (not `internet_health_summary`), giving daily-resolution charts for HTTPS, DNSSEC, and ROA.

## Project Structure

```
internet-health-monitor/
├── assets/
│   ├── ingestion/           # 235 ingestr asset files (47 countries × 5 metric types)
│   │   ├── ipv6/                    # 47 files
│   │   ├── https/                   # 47 files
│   │   ├── dnssec_validation/       # 47 files
│   │   ├── roa_4/                  # 47 files
│   │   └── roa_6/                  # 47 files
│   ├── transformations/     # SQL transformation assets (6 files)
│   │   ├── ipv6_combined.sql
│   │   ├── https_combined.sql
│   │   ├── dnssec_combined.sql
│   │   ├── roa_combined.sql
│   │   ├── internet_health_summary.sql
│   │   └── country_rankings.sql
│   └── enrichment/          # Python enrichment assets
│       └── health_scoring.py
├── dashboard/               # Dash visualization app
│   ├── app.py               # Main Dash app + routing + callbacks
│   ├── constants.py         # Country codes, ISO mappings, metric options
│   ├── layouts/             # 4 page layouts (overview, compare, trends, detail)
│   ├── components/          # Reusable components (map, cards, navbar)
│   └── data/                # DuckDB query functions
├── config/                   # Configuration
│   └── countries.yaml        # Single source of truth for tracked countries
├── scripts/                  # Utility scripts
│   ├── generate_assets.py    # Regenerate pipeline assets from countries.yaml
│   └── countries.py          # Country lookup CLI
├── data/                     # DuckDB database directory
├── tests/                   # pytest test suite
├── .github/workflows/       # GitHub Actions CI
├── .bruin.yml              # Bruin connections (DuckDB + ISOC Pulse, gitignored)
├── .env                    # Environment variables (gitignored)
├── pipeline.yml            # Bruin pipeline definition
├── pyproject.toml          # Project config + dependencies
├── justfile                # Task runner commands
├── README.md               # Project documentation
├── compose.yaml            # Docker Compose (dashboard only)
├── Dockerfile              # Dashboard container
```

## Bruin Asset Naming Convention

The project uses a **medallion architecture** (Bronze/Silver/Gold):

- **Bronze (raw ingestion)**: `raw.<metric>_<CC>` (e.g., `raw.ipv6_US`, `raw.https_US`, `raw.dnssec_validation_US`, `raw.roa_4_US`)
- **Silver (cleansed/staging)**: `staging.<metric>_combined` (e.g., `staging.ipv6_combined`, `staging.https_combined`, `staging.roa_combined`)
- **Gold (business/marts)**: `marts.<table>` (e.g., `marts.internet_health_summary`, `marts.country_rankings`, `marts.health_scoring`)

## Data Scale

All metric scores are stored as **percentages (0-100 scale)**. The `value * 100` conversion happens in:
- `ipv6_combined.sql` → `value * 100 AS ipv6_score`
- `https_combined.sql` → `value * 100 AS https_score`
- `dnssec_combined.sql` → `value * 100 AS dnssec_score`
- `roa_combined.sql` → `(ipv4_value + ipv6_value) / 2 * 100 AS roa_score`

## Incremental Loading

All 235 ingestion assets use **`delete+insert`** materialization with `incremental_key: date`. This means:
- **First run**: Ingests full historical data from the ISOC Pulse API
- **Subsequent runs**: Only fetches rows where `date` is newer than the last recorded date in DuckDB
- This reduces API load and makes pipeline runs significantly faster

Transform assets use **`create+replace`** materialization and re-run the full SQL logic on each pipeline execution.

## Health Score Calculation

```
health_score = (ipv6_score × 0.25) + (https_score × 0.25) + (dnssec_score × 0.25) + (roa_score × 0.25)
```

## Testing

- Run `just test` to execute the full test suite
- Run `just test-cov` to run with coverage
- Sample data fixtures are in `tests/conftest.py`
- Test files:
  - `test_health_scoring.py` - Health score calculation logic (4-metric, 25% each)
  - `test_dashboard.py` - Dashboard components, constants, and layout imports
  - `test_queries.py` - DuckDB query functions (query functions + edge cases)
  - `test_chart_functions.py` - Chart creation functions (radar, bar, timeseries, distribution)
  - `test_layout_errors.py` - Layout error handling (mocked)
  - `test_app.py` - Dash app callbacks and helper functions

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ISOC_PULSE_TOKEN` | API token for Internet Society Pulse | Yes (for pipeline) |
| `TELEMETRY_OPTOUT` | Set to `true` to disable Bruin CLI telemetry | No |
| `INGESTR_DISABLE_TELEMETRY` | Set to `true` to disable ingestr telemetry | No |

## Code Style

- **Line length**: 100 characters max
- **Formatter**: ruff with double quotes
- **Linting**: ruff with rules E, F, W, I, N, UP, B, C4
- **Python version**: 3.12 (enforced via `.python-version`)

## Database

- **Location**: `data/internet_health.db`
- **Gitignored**: Yes (contains production data)
- **Bronze (raw)**: One table per ingestion asset (235 tables total in `raw.*` schema)
- **Silver (staging)**:
  - `staging.ipv6_combined` — UNION of all 47 country IPv6 tables
  - `staging.https_combined` — UNION of all 47 country HTTPS tables
  - `staging.dnssec_combined` — UNION of all 47 country DNSSEC tables
  - `staging.roa_combined` — Merged IPv4+IPv6 ROA per country per date (daily)
- **Gold (marts)**:
  - `marts.internet_health_summary` — LEFT JOIN from monthly IPv6 + monthly aggregates
  - `marts.country_rankings` — Per-country health scores with 4-metric composite
  - `marts.health_scoring` — Country-level averages (Python enrichment output)

## Dashboard Pages

1. **Overview** (`/`) - 6 KPI cards (Global Health, IPv6, HTTPS, DNSSEC, ROA/RPKI, Countries Tracked) + choropleth map (tracked countries only) + country rankings; KPI cards auto-color by score threshold (green >=80, blue >=60, yellow >=40, red <40)
2. **Compare** (`/compare`) - Radar chart (4-axis, filled) + grouped bar chart (4 metrics) + detailed metrics table (6 columns); reference lines at 50% and 80%
3. **Trends** (`/trends`) - Single country trend + multi-country comparison; metric selector offers IPv6/HTTPS/DNSSEC/ROA-RPKI; **daily resolution preserved** for https/dnssec/roa; CSV download available
4. **Detail** (`/detail`) - Geographic map + country rankings + score breakdown; metric selector offers IPv6/HTTPS/DNSSEC/ROA-RPKI; reference line at 50%

## Common Issues

| Issue | Solution |
|-------|----------|
| `Database not found` | Run `just run-pipeline` first to create the DB |
| `ISOC_PULSE_TOKEN not set` | Set the env var or add it to GitHub secrets |
| `uv lock` fails | Ensure `uv` is installed: `pip install uv` |
| `ruff` not found | Run `uv sync` to install dev dependencies |

## Known Limitations

- **ISOC Pulse API has varying data availability** — Not all metrics are available for all countries. Data coverage depends on the source.
- **IPv6 is monthly while other metrics are daily** — IPv6 is the driving table in the summary JOIN. HTTPS, DNSSEC, and ROA are aggregated from daily to monthly via `DATE_TRUNC('month', date) + AVG()` in `internet_health_summary`. However, trend lines on the Trends page **preserve daily granularity** by querying the individual `*_combined` tables directly.

## Useful Links

- [Bruin Documentation](https://bruin-data.github.io/bruin/)
- [Internet Society Pulse](https://pulse.internetsociety.org/)
- [ingestr Telemetry Docs](https://getbruin.com/docs/ingestr/getting-started/telemetry.html)
- [Dash Documentation](https://dash.plotly.com/)
- [Plotly Express](https://plotly.com/python/plotly-express/)