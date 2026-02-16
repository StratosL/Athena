# Productivity App Backend

FastAPI backend with Vertical Slice Architecture (VSA) for the Productivity App.

## Setup

```bash
uv sync --all-extras
```

## Development

```bash
uv run uvicorn app.main:app --reload
```

## Testing

```bash
uv run pytest -v
```

## Linting

```bash
uv run ruff check . --fix
uv run ruff format .
```
