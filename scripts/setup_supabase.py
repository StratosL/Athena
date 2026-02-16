"""Phase 2a: Create Supabase database tables via direct Postgres connection."""

from pathlib import Path

import httpx
from rich.console import Console

from .config import SetupConfig

console = Console()

MIGRATION_PATH = Path(__file__).parent.parent / "supabase" / "migrations" / "001_initial_schema.sql"


def _run_migration(cfg: SetupConfig) -> bool:
    """Execute the SQL migration against Supabase Postgres."""
    sql = MIGRATION_PATH.read_text()

    if not cfg.supabase_db_url:
        console.print("  [yellow]\u26a0[/] SUPABASE_DB_URL not set — cannot auto-create tables.")
        console.print("    Paste the following SQL into the Supabase SQL Editor:")
        console.print(f"    Open: {cfg.supabase_url}/project/default/sql/new")
        console.print()
        console.print(f"    File: {MIGRATION_PATH}")
        return True  # Not a fatal error — user can do it manually

    try:
        import psycopg  # noqa: F811

        with psycopg.connect(cfg.supabase_db_url) as conn:
            conn.execute(sql)
            conn.commit()
        console.print("  [green]\u2192[/] Tables created (or already exist)")
        return True
    except Exception as e:
        console.print(f"  [red]\u2717[/] Postgres migration failed: {e}")
        console.print("    Check SUPABASE_DB_URL in .env (Settings \u2192 Database \u2192 URI)")
        return False


def _verify_tables(cfg: SetupConfig) -> bool:
    """Verify tables exist via Supabase REST API."""
    headers = {
        "apikey": cfg.supabase_anon_key,
        "Authorization": f"Bearer {cfg.supabase_anon_key}",
    }
    tables = ["tasks", "daily_plans", "pomodoro_sessions"]
    all_ok = True
    for table in tables:
        try:
            r = httpx.get(
                f"{cfg.supabase_url}/rest/v1/{table}?limit=0",
                headers=headers,
                timeout=10,
            )
            if r.status_code == 200:
                console.print(f"    [green]\u2713[/] {table}")
            else:
                console.print(f"    [red]\u2717[/] {table} (HTTP {r.status_code})")
                all_ok = False
        except Exception as e:
            console.print(f"    [red]\u2717[/] {table} ({e})")
            all_ok = False
    return all_ok


def run(cfg: SetupConfig) -> bool:
    """Create database tables and verify. Returns True on success."""
    console.print("\n  [bold][2a] Supabase database...[/]")

    if not _run_migration(cfg):
        return False

    console.print("  Verifying tables...")
    return _verify_tables(cfg)
