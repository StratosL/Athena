"""Phase 3: End-to-end health checks after setup."""

import httpx
from rich.console import Console
from rich.table import Table

from .config import SetupConfig

console = Console()


def _check(
    label: str, fn: callable, results: list[tuple[str, str, str]]
) -> None:
    """Run a check function and record the result."""
    try:
        ok, detail = fn()
        if ok:
            results.append((label, "[green]\u2713 pass[/]", detail))
        else:
            results.append((label, "[red]\u2717 fail[/]", detail))
    except Exception as e:
        results.append((label, "[red]\u2717 error[/]", str(e)[:80]))


def run(cfg: SetupConfig) -> bool:
    """Run all health checks. Returns True if all pass."""
    console.print("\n[bold]Phase 3/3: Verifying...[/]")

    results: list[tuple[str, str, str]] = []
    headers_es = {"Authorization": f"ApiKey {cfg.elastic_api_key}"}
    headers_sb = {
        "apikey": cfg.supabase_anon_key,
        "Authorization": f"Bearer {cfg.supabase_anon_key}",
    }
    headers_kb = {
        "Authorization": f"ApiKey {cfg.elastic_api_key}",
        "kbn-xsrf": "true",
    }

    # Supabase tables
    def check_supabase() -> tuple[bool, str]:
        tables_ok = 0
        for table in ["tasks", "daily_plans", "pomodoro_sessions"]:
            r = httpx.get(
                f"{cfg.supabase_url}/rest/v1/{table}?limit=0",
                headers=headers_sb,
                timeout=10,
            )
            if r.status_code == 200:
                tables_ok += 1
        return tables_ok == 3, f"{tables_ok}/3 tables accessible"

    _check("Supabase tables", check_supabase, results)

    # ES indices
    def check_es_index() -> tuple[bool, str]:
        r = httpx.get(
            f"{cfg.elastic_url}/{cfg.notes_index}/_count",
            headers=headers_es,
            timeout=10,
        )
        if r.status_code == 200:
            count = r.json().get("count", 0)
            return count > 0, f"{count} notes indexed"
        return False, f"HTTP {r.status_code}"

    _check("Elasticsearch index", check_es_index, results)

    # Agent Builder tools
    def check_tools() -> tuple[bool, str]:
        r = httpx.get(
            f"{cfg.kibana_url}/api/agent_builder/tools",
            headers=headers_kb,
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            # API returns {"results": [...]}
            tools = data.get("results", []) if isinstance(data, dict) else data
            # Filter to non-builtin tools
            custom = [t for t in tools if t.get("type") != "builtin"]
            return len(custom) >= 6, f"{len(custom)} custom tools registered"
        return False, f"HTTP {r.status_code}"

    _check("Agent Builder tools", check_tools, results)

    # Agent exists
    def check_agent() -> tuple[bool, str]:
        r = httpx.get(
            f"{cfg.kibana_url}/api/agent_builder/agents/athena",
            headers=headers_kb,
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            config = data.get("configuration", {})
            tool_count = sum(
                len(g.get("tool_ids", [])) for g in config.get("tools", [])
            )
            return True, f"ready ({tool_count} tools)"
        return False, f"HTTP {r.status_code}"

    _check("Athena agent", check_agent, results)

    # MCP connector (if ngrok set)
    if cfg.ngrok_domain:
        def check_mcp() -> tuple[bool, str]:
            r = httpx.get(
                f"{cfg.kibana_url}/api/actions/connectors",
                headers=headers_kb,
                timeout=10,
            )
            if r.status_code == 200:
                for conn in r.json():
                    if conn.get("connector_type_id") == ".mcp":
                        return True, f"connector {conn['id'][:8]}..."
            return False, "no MCP connector found"

        _check("MCP connector", check_mcp, results)

    # Docker services (if running)
    def check_docker_artemis() -> tuple[bool, str]:
        try:
            r = httpx.get("http://localhost:8000/health", timeout=3)
            return r.status_code == 200, "healthy"
        except Exception:
            return False, "not running (optional)"

    def check_docker_voice() -> tuple[bool, str]:
        try:
            r = httpx.get("http://localhost:3001/api/health", timeout=3)
            return r.status_code == 200, "healthy"
        except Exception:
            return False, "not running (optional)"

    _check("Artemis backend", check_docker_artemis, results)
    _check("Voice proxy", check_docker_voice, results)

    # Print results table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Details", style="dim")

    all_pass = True
    for label, status, detail in results:
        table.add_row(label, status, detail)
        if "fail" in status and "optional" not in detail:
            all_pass = False

    console.print(table)
    return all_pass
