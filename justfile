# Justfile for Internet Health Monitor

# Load environment variables from .env file
set dotenv-load

start_date := "2026-03-01"

# Show available commands
help:
    @just --list

# Install dependencies (including dev tools)
install:
    uv sync --group dev

# Run linter
lint:
    uv run ruff check .

# Run formatter
format:
    uv run ruff format .

# Run type checker
typecheck:
    uv run pyrefly check dashboard/ tests/ assets/enrichment/

# Run tests
test:
    uv run pytest tests/ -v

# Run tests with coverage
test-cov:
    uv run pytest tests/ -v --cov=dashboard --cov-report=html --cov-report=term

# Run Bruin pipeline
run-pipeline:
    TELEMETRY_OPTOUT=true INGESTR_DISABLE_TELEMETRY=true bruin run . --start-date {{ start_date }}

# Validate Bruin pipeline
validate:
    TELEMETRY_OPTOUT=true bruin validate .

# Launch dashboard
dashboard:
    uv run python -m dashboard.app

# Full setup (install + validate)
setup: install validate
    @echo "Setup complete!"

# Clean generated files
clean:
    rm -rf __pycache__ */__pycache__ */*/__pycache__
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -f .coverage
    rm -f data/internet_health.db
    @echo "Clean complete!"

# Clean DuckDB database only
clean-db:
    rm -f data/internet_health.db
    @echo "Database deleted!"

# Regenerate all pipeline assets from countries.yaml
generate:
    uv run python scripts/generate_assets.py

# Add one or more countries then regenerate all pipeline assets
add-country +CODES:
    uv run python scripts/generate_assets.py --add {{ CODES }}

# Remove one or more countries then regenerate pipeline assets
remove-country +CODES:
    uv run python scripts/generate_assets.py --remove {{ CODES }}

# Search for a country by name (case-insensitive substring match)
search-country QUERY:
    uv run python scripts/countries.py search "{{ QUERY }}"

# List all 249 ISO countries
list-countries:
    uv run python scripts/countries.py list

# List all countries currently tracked in the pipeline
list-tracked:
    uv run python scripts/countries.py tracked

# Check if generated files are in sync with constants (CI drift check)
check-drift:
    uv run python scripts/generate_assets.py --check

# Lock dependencies
lock:
    uv lock

# Build Docker images (dashboard)
docker-build:
    docker compose build dashboard

# Start dashboard in Docker (detached)
docker-up:
    docker compose up --build -d

# Stop all services
docker-down:
    docker compose down

# Tail logs from dashboard
docker-logs:
    docker compose logs -f

# CI check (install + lint + typecheck + format + test + validate + drift-check)
ci: install lint typecheck format test validate check-drift
    @echo "CI checks passed!"
