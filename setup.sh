#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Check .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found."
    echo "Run: cp .env.example .env"
    echo "Then fill in your credentials and run this script again."
    exit 1
fi

# Check Python 3.12+
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 not found. Install from https://www.python.org/downloads/"
    exit 1
fi

# Check uv
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found. Install from https://docs.astral.sh/uv/"
    exit 1
fi

# Install setup script dependencies
uv sync --project scripts

# Run the setup
uv run --project scripts python -m scripts.setup "$@"
