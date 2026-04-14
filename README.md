# Internet Health Monitor

An interactive dashboard for visualizing internet health metrics for 5 countries (US, DE, BR, IN, JP), built with Bruin, DuckDB, and Dash.

## Overview

This project ingests internet health data from the [Internet Society Pulse API](https://pulse.internetsociety.org/) and transforms it into an interactive web dashboard. It covers 4 scored metrics plus internet shutdown data:

| Metric                  | Description                                                 | Data Frequency |
| ----------------------- | ----------------------------------------------------------- | -------------- |
| **IPv6 Adoption**       | Percentage of users who can access the network via IPv6     | Monthly        |
| **HTTPS Adoption**      | Percentage of web traffic using encrypted HTTPS connections | Daily          |
| **DNSSEC Validation**   | Percentage of TLDs with valid DNSSEC                        | Daily          |
| **ROA/RPKI**            | Route origin authorization coverage (IPv4 + IPv6 average)   | Daily          |
| **Net Loss / Shutdown** | Internet shutdown events and GDP impact                     | Event-based    |

The composite **Health Score** combines IPv6, HTTPS, DNSSEC, and ROA with equal 25% weights. Net loss data is displayed as "Internet Freedom" but is not part of the health score.

The dashboard provides five views: global overview with choropleth map, country comparison charts, time-series trends, metric detail analysis, and a dedicated internet shutdowns page.

## Architecture

```mermaid
graph LR
    A["🌐 ISOC Pulse API"] -->|ingestr| B["🥉 Bronze (raw)<br/>30 ingestion tables"]
    B -->|cleansed, UNIONed| C["🥈 Silver (staging)<br/>5 combined tables"]
    C -->|monthly aggregation| D["🥇 Gold (marts)<br/>3 business tables"]
    D -->|queries| E["📊 Dash Dashboard<br/>5 interactive pages"]

    subgraph DuckDB["DuckDB"]
        B
        C
        D
    end
```

## Tech Stack

| Layer              | Tool             | Version             |
| ------------------ | ---------------- | ------------------- |
| Pipeline Framework | Bruin            | latest              |
| Data Warehouse     | DuckDB           | >=1.0.0             |
| Language           | Python           | 3.12                |
| Package Manager    | uv               | latest              |
| Linter/Formatter   | ruff             | >=0.3.0             |
| Type Checker       | ty               | >=0.0.29            |
| Dashboard          | Dash + Plotly    | >=2.14.0 / >=5.18.0 |
| Task Runner        | just             | latest              |
| Testing            | pytest           | >=7.4.0             |
| Containerization   | Docker + Compose | -                   |

## Quick Commands

```bash
# Setup
just setup                    # Install deps + validate pipeline

# Development
just install                  # Install dependencies
just lint                     # Run ruff linter
just format                   # Run ruff formatter
just typecheck                # Run ty type checker
just test                     # Run pytest
just test-cov                 # Run pytest with coverage
just ci                       # Run all CI checks

# Pipeline
just run-pipeline             # Run Bruin pipeline (ingest + transform)
just validate                 # Validate pipeline assets

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
```

## Countries

Data is tracked for 5 countries (the only ones with data in the ISOC Pulse API):

| Code | Country       |
| ---- | ------------- |
| US   | United States |
| DE   | Germany       |
| BR   | Brazil        |
| IN   | India         |
| JP   | Japan         |

## Dashboard Pages

1. **Overview** (`/`) — 7 KPI cards (Global Health, IPv6, HTTPS, DNSSEC, ROA/RPKI, Internet Freedom, Countries Tracked) + interactive choropleth map + country rankings; KPI cards auto-color by score threshold
2. **Compare** (`/compare`) — Radar chart (4-axis, filled), grouped bar chart (4 metrics), detailed metrics table (6 columns); reference lines at 50% and 80%
3. **Trends** (`/trends`) — Single country trend + multi-country comparison; metric selector offers IPv6/HTTPS/DNSSEC/ROA-RPKI; **daily resolution preserved** for HTTPS/DNSSEC/ROA trend lines; CSV download available
4. **Detail** (`/detail`) — Geographic map + country rankings + distribution; metric selector offers IPv6/HTTPS/DNSSEC/ROA-RPKI; reference line at 50%
5. **Shutdowns** (`/shutdowns`) — KPI summary (total events, avg duration, GDP impact, avg freedom) + Gantt-style timeline + GDP impact chart + events table; CSV download available

## Configuration

Environment variables (set in `.env`):

```bash
cp .env.example .env  # Then add your ISOC_PULSE_TOKEN
```

| Variable                    | Description                                | Required |
| --------------------------- | ------------------------------------------ | -------- |
| `ISOC_PULSE_TOKEN`          | API token for Internet Society Pulse       | Yes      |
| `TELEMETRY_OPTOUT`          | Set to `true` to disable Bruin telemetry   | No       |
| `INGESTR_DISABLE_TELEMETRY` | Set to `true` to disable ingestr telemetry | No       |

## Prerequisites

- [Python](https://www.python.org/) 3.12
- [uv](https://docs.astral.sh/uv/) — `pip install uv`
- [Bruin CLI](https://bruin-data.github.io/bruin/) — `curl -fsSL https://raw.githubusercontent.com/bruin-data/bruin/main/install.sh | sh`
- [just](https://github.com/casey/just) — `brew install just` (macOS) or `cargo install just`
- [Docker](https://docs.docker.com/get-docker/) — optional, for dashboard container
- `ISOC_PULSE_TOKEN` — get one at [pulse.internetsociety.org](https://pulse.internetsociety.org/)

## Running Locally

```bash
# 1. Install dependencies
just install

# 2. Set up environment
cp .env.example .env  # Add your ISOC_PULSE_TOKEN

# 3. Run the pipeline
just run-pipeline

# 4. Launch the dashboard
just dashboard
```

**Pipeline behavior:** The first run ingests all historical data. Subsequent runs use **incremental loading** — only new data since the last recorded date is fetched from the API, making runs faster and reducing API calls.

Open [http://localhost:8050](http://localhost:8050) in your browser.

## Running with Docker

```bash
# Start dashboard (uses existing data in ./data directory)
just docker-up

# Dashboard available at http://localhost:8050

# Stop services
just docker-down

# Rebuild if needed
just docker-build && just docker-up
```

**Note**: The pipeline runs locally via `just run-pipeline` (requires `ISOC_PULSE_TOKEN`). Docker is for the dashboard only.

## Testing

```bash
just test              # Run all 138 tests
just test-cov          # Run with coverage report (93%)
```

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_health_scoring.py` | Health score formula and SQL validation | `assets/enrichment/` |
| `test_dashboard.py` | Components, constants, navbar, layouts | `dashboard/` |
| `test_queries.py` | All 8 DuckDB query functions + edge cases | `dashboard/data/` |
| `test_chart_functions.py` | Radar, bar, timeseries, distribution charts | `dashboard/layouts/` |
| `test_layout_errors.py` | Layout error handling (mocked) | `dashboard/layouts/` |
| `test_app.py` | Dash callbacks, routing, helpers | `dashboard/app.py` |

## Health Score Calculation

The composite health score is an equally-weighted average of 4 scored metrics:

```
health_score = (ipv6_score × 0.25) + (https_score × 0.25) + (dnssec_score × 0.25) + (roa_score × 0.25)
```

**Net loss / freedom_score is NOT part of the health score** — it is displayed as "Internet Freedom" on the Overview page only.

All scores are on a 0-100 scale (percentage).

## Known Limitations

- **ISOC Pulse API only has data for 5 countries** (US, DE, BR, IN, JP). Other G20 countries return 0 rows.
- **IPv6 is monthly while other metrics are daily** — IPv6 is the driving table in the summary JOIN. HTTPS, DNSSEC, and ROA are aggregated from daily to monthly via `DATE_TRUNC('month', date) + AVG()` in `internet_health_summary`. However, trend lines on the Trends page **preserve daily granularity** by querying the individual `*_combined` tables directly.
- **Net loss data is event-based** — Internet shutdown events are sporadic and not part of the health score.