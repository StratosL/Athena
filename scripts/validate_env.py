"""Phase 1: Validate environment variables and service connectivity."""

import sys

import httpx
from rich.console import Console

from .config import SetupConfig

console = Console()


def _check_var(cfg: SetupConfig, name: str, attr: str) -> bool:
    """Check that an env var is set (non-empty)."""
    val = getattr(cfg, attr, "")
    if val:
        console.print(f"  [green]\u2713[/] {name} set")
        return True
    console.print(f"  [red]\u2717[/] {name} not set")
    return False


def _test_elasticsearch(cfg: SetupConfig) -> bool:
    """Test Elasticsearch connectivity."""
    try:
        r = httpx.get(
            f"{cfg.elastic_url}/",
            headers={"Authorization": f"ApiKey {cfg.elastic_api_key}"},
            timeout=10,
        )
        r.raise_for_status()
        console.print("  [green]\u2713[/] Elasticsearch reachable")
        return True
    except Exception as e:
        console.print(f"  [red]\u2717[/] Elasticsearch unreachable: {e}")
        console.print("    Get a free trial at https://cloud.elastic.co/registration?cta=hackathon")
        return False


def _test_supabase(cfg: SetupConfig) -> bool:
    """Test Supabase REST API connectivity."""
    try:
        r = httpx.get(
            f"{cfg.supabase_url}/rest/v1/",
            headers={
                "apikey": cfg.supabase_anon_key,
                "Authorization": f"Bearer {cfg.supabase_anon_key}",
            },
            timeout=10,
        )
        # Supabase returns 200 with an empty object for the root REST endpoint
        if r.status_code < 500:
            console.print("  [green]\u2713[/] Supabase reachable")
            return True
        console.print(f"  [red]\u2717[/] Supabase returned {r.status_code}")
        return False
    except Exception as e:
        console.print(f"  [red]\u2717[/] Supabase unreachable: {e}")
        console.print("    Create a free project at https://supabase.com/dashboard")
        return False


def _check_optional(cfg: SetupConfig) -> None:
    """Warn about missing optional variables."""
    if not cfg.openai_api_key:
        console.print("  [yellow]\u26a0[/] OPENAI_API_KEY not set (voice features disabled)")
    if not cfg.brave_api_key and not cfg.tavily_api_key:
        console.print("  [yellow]\u26a0[/] BRAVE_API_KEY / TAVILY_API_KEY not set (web search disabled)")
    if not cfg.ngrok_domain:
        console.print("  [yellow]\u26a0[/] NGROK_DOMAIN not set (Agent Builder MCP setup will be skipped)")
    if not cfg.supabase_db_url:
        console.print(
            "  [yellow]\u26a0[/] SUPABASE_DB_URL not set (database tables must be created manually)"
        )


def run(cfg: SetupConfig) -> bool:
    """Validate all required credentials and connectivity. Returns True on success."""
    console.print("\n[bold]Phase 1/3: Validating environment...[/]")

    ok = True

    # Required vars
    for name, attr in [
        ("ELASTIC_URL", "elastic_url"),
        ("ELASTIC_API_KEY", "elastic_api_key"),
        ("SUPABASE_URL", "supabase_url"),
        ("SUPABASE_ANON_KEY", "supabase_anon_key"),
    ]:
        if not _check_var(cfg, name, attr):
            ok = False

    if not ok:
        console.print("\n  [red]Missing required variables. Fill in .env and try again.[/]")
        return False

    # Connectivity
    if not _test_elasticsearch(cfg):
        ok = False
    if not _test_supabase(cfg):
        ok = False

    # Optional warnings
    _check_optional(cfg)

    if not ok:
        console.print("\n  [red]Connectivity checks failed. Fix the errors above and try again.[/]")
    return ok
