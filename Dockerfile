# Dashboard Dockerfile
# Build: docker compose build dashboard
# Run: docker compose up -d dashboard

# -----------------------------------------------------------------------------
# Stage 1: Build dependencies
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv for dependency management
RUN pip install uv

# Copy project files for dependency resolution
COPY pyproject.toml uv.lock .python-version ./

# Install dependencies into isolated virtual environment
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv sync --frozen --no-dev

# -----------------------------------------------------------------------------
# Stage 2: Production runtime
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source
COPY dashboard/ /app/dashboard/

# Copy pipeline and config files (needed for data queries)
COPY pipeline.yml /app/pipeline.yml

# Create data directory for DuckDB database
RUN mkdir -p /app/data

# Define volume for data persistence
VOLUME /app/data

# Set up Python environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose Dash port
EXPOSE 8050

# Health check (Python-based, no curl needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8050/')"

# Run the dashboard
CMD ["python", "-m", "dashboard.app"]