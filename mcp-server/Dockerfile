# Multi-stage build for Athena MCP Server
# Pattern borrowed from obsidian-ai-agent — uv for fast installs, slim runtime image

# --- Builder stage ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Install dependencies first (cached layer)
COPY pyproject.toml ./
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

EXPOSE 8001

CMD ["python", "-m", "src.server"]
