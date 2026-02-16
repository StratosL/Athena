# Multi-stage build for Athena Heartbeat Service
# Scheduled agent check-ins via APScheduler + Kibana converse API

# --- Builder stage ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Copy source code
COPY src/ src/

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# --- Runtime stage ---
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy only the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Ensure venv binaries are on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Vault will be mounted at /vault by docker-compose
ENV VAULT_PATH=/vault

# exec form so Python is PID 1 and receives SIGTERM directly
CMD ["python", "-m", "src"]
