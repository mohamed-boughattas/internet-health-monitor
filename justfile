# Justfile for Internet Health Monitor

# Load environment variables from .env file
set dotenv-load

# Show available commands
help:
    @just --list

# Install dependencies (including dev tools)
install:
    uv sync --extra dev

# Run linter
lint:
    uv run ruff check .

# Run formatter
format:
    uv run ruff format .

# Run type checker
typecheck:
    uv run ty check dashboard/ tests/ assets/enrichment/

# Run tests
test:
    uv run pytest tests/ -v

# Run tests with coverage
test-cov:
    uv run pytest tests/ -v --cov=dashboard --cov-report=html --cov-report=term

# Run Bruin pipeline
run-pipeline:
    TELEMETRY_OPTOUT=true INGESTR_DISABLE_TELEMETRY=true bruin run .

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
    rm -f internet_health.db
    rm -f test_internet_health.db
    @echo "Clean complete!"

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

# CI check (install + lint + typecheck + format + test + validate)
ci: install lint typecheck format test validate
    @echo "CI checks passed!"
