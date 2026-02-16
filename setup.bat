@echo off
setlocal

cd /d "%~dp0"

:: Check .env exists
if not exist .env (
    echo ERROR: .env file not found.
    echo Run: copy .env.example .env
    echo Then fill in your credentials and run this script again.
    exit /b 1
)

:: Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://www.python.org/downloads/
    exit /b 1
)

:: Check uv
where uv >nul 2>nul
if errorlevel 1 (
    echo ERROR: uv not found. Install from https://docs.astral.sh/uv/
    exit /b 1
)

:: Install setup script dependencies
uv sync --project scripts

:: Run the setup — pass all arguments through
uv run --project scripts python -m scripts.setup %*
