# Multi-stage build for Athena Voice Proxy
# Pattern: same uv builder as mcp-server, single-file app (serve.py) + static assets

# --- Builder stage ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Copy application files
COPY serve.py ./
COPY index.html style.css voice.js ./
COPY athena-logo.svg athena-logo.jpg ./

# --- Runtime stage ---
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy virtual environment and app files from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/serve.py /app/
COPY --from=builder /app/index.html /app/style.css /app/voice.js /app/
COPY --from=builder /app/athena-logo.svg /app/athena-logo.jpg /app/

# Ensure venv binaries are on PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 3001

CMD ["python", "serve.py"]
