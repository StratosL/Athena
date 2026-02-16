"""Phase 2c: Create tools, MCP connector, and agent in Kibana Agent Builder."""

import json
from pathlib import Path

import httpx
from rich.console import Console

from .config import SetupConfig

console = Console()

TOOLS_DIR = Path(__file__).parent.parent / "agent-config" / "tools"
SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "agent-config" / "system-prompt.md"

MCP_TOOL_NAMES = [
    "vault_query",
    "vault_read",
    "vault_manage",
    "artemis_create_task",
    "artemis_list_tasks",
    "artemis_complete_task",
    "artemis_get_daily_plan",
    "artemis_assign_to_plan",
    "artemis_get_analytics",
    "artemis_start_pomodoro",
    "save_conversation_summary",
    "web_search",
    "fetch_url",
]


def _kibana_headers(cfg: SetupConfig) -> dict[str, str]:
    """Standard headers for Kibana API requests."""
    return {
        "Authorization": f"ApiKey {cfg.elastic_api_key}",
        "kbn-xsrf": "true",
        "Content-Type": "application/json",
    }


def _is_already_exists(r: httpx.Response) -> bool:
    """Check if an API error indicates the resource already exists."""
    if r.status_code == 409:
        return True
    if r.status_code == 400:
        try:
            msg = r.json().get("message", "")
        except Exception:
            msg = r.text
        return "already exists" in msg.lower()
    return False


def _create_esql_tools(cfg: SetupConfig, client: httpx.Client) -> list[str]:
    """Create ES|QL and index_search tools from JSON files. Returns list of tool IDs."""
    tool_ids: list[str] = []
    json_files = sorted(TOOLS_DIR.glob("*.json"))

    if not json_files:
        console.print("  [red]\u2717[/] No tool JSON files found in agent-config/tools/")
        return tool_ids

    for f in json_files:
        tool_def = json.loads(f.read_text())
        tool_id = tool_def.get("id", f.stem)

        # Try to create
        r = client.post(
            f"{cfg.kibana_url}/api/agent_builder/tools",
            headers=_kibana_headers(cfg),
            json=tool_def,
        )

        if r.status_code in (200, 201):
            tool_ids.append(tool_id)
            console.print(f"    [green]\u2713[/] {tool_id} ({tool_def.get('type', 'unknown')})")
        elif _is_already_exists(r):
            # Already exists — try PUT update (without id in body)
            update_body = {k: v for k, v in tool_def.items() if k != "id"}
            r2 = client.put(
                f"{cfg.kibana_url}/api/agent_builder/tools/{tool_id}",
                headers=_kibana_headers(cfg),
                json=update_body,
            )
            if r2.status_code in (200, 201):
                tool_ids.append(tool_id)
                console.print(f"    [green]\u2713[/] {tool_id} (updated)")
            else:
                # Exists but can't update — still usable
                tool_ids.append(tool_id)
                console.print(f"    [yellow]\u26a0[/] {tool_id} (exists)")
        else:
            console.print(f"    [red]\u2717[/] {tool_id}: HTTP {r.status_code}")
            try:
                console.print(f"      {r.json().get('message', r.text[:200])}")
            except Exception:
                console.print(f"      {r.text[:200]}")

    return tool_ids


def _check_mcp_reachable(cfg: SetupConfig, client: httpx.Client) -> bool:
    """Check if MCP server is reachable at the ngrok domain."""
    if not cfg.ngrok_domain:
        return False
    try:
        url = f"https://{cfg.ngrok_domain}/"
        r = client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "setup-check", "version": "0.1"},
                },
            },
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def _create_mcp_connector(cfg: SetupConfig, client: httpx.Client) -> str | None:
    """Create or find existing MCP connector. Returns connector ID or None."""
    server_url = f"https://{cfg.ngrok_domain}"

    # Check if connector already exists by listing connectors
    r = client.get(
        f"{cfg.kibana_url}/api/actions/connectors",
        headers=_kibana_headers(cfg),
    )
    if r.status_code == 200:
        for conn in r.json():
            if conn.get("connector_type_id") == ".mcp":
                existing_url = conn.get("config", {}).get("serverUrl", "")
                if existing_url.rstrip("/") == server_url.rstrip("/"):
                    console.print(f"    [green]\u2713[/] MCP connector exists ({conn['id'][:8]}...)")
                    return conn["id"]

    # Create new connector
    r = client.post(
        f"{cfg.kibana_url}/api/actions/connector",
        headers=_kibana_headers(cfg),
        json={
            "name": "Athena MCP Server",
            "connector_type_id": ".mcp",
            "config": {"serverUrl": server_url},
            "secrets": {},
        },
    )
    if r.status_code in (200, 201):
        connector_id = r.json().get("id", "")
        console.print(f"    [green]\u2713[/] MCP connector created ({connector_id[:8]}...)")
        return connector_id

    console.print(f"    [red]\u2717[/] Failed to create MCP connector: HTTP {r.status_code}")
    try:
        console.print(f"      {r.json().get('message', r.text[:200])}")
    except Exception:
        console.print(f"      {r.text[:200]}")
    return None


def _register_mcp_tools(
    cfg: SetupConfig, client: httpx.Client, connector_id: str
) -> list[str]:
    """Register MCP tools in Agent Builder. Returns list of tool IDs."""
    tool_ids: list[str] = []

    for tool_name in MCP_TOOL_NAMES:
        tool_id = f"athena.{tool_name}"
        tool_def = {
            "id": tool_id,
            "type": "mcp",
            "description": f"MCP tool: {tool_name}",
            "configuration": {
                "connector_id": connector_id,
                "tool_name": tool_name,
            },
        }

        r = client.post(
            f"{cfg.kibana_url}/api/agent_builder/tools",
            headers=_kibana_headers(cfg),
            json=tool_def,
        )

        if r.status_code in (200, 201):
            tool_ids.append(tool_id)
        elif _is_already_exists(r):
            # Already exists — update connector reference
            update_body = {k: v for k, v in tool_def.items() if k != "id"}
            r2 = client.put(
                f"{cfg.kibana_url}/api/agent_builder/tools/{tool_id}",
                headers=_kibana_headers(cfg),
                json=update_body,
            )
            tool_ids.append(tool_id)
            if r2.status_code not in (200, 201):
                console.print(f"    [yellow]\u26a0[/] {tool_id} exists (update returned {r2.status_code})")
        else:
            console.print(f"    [red]\u2717[/] {tool_id}: HTTP {r.status_code}")

    if tool_ids:
        console.print(f"    [green]\u2713[/] {len(tool_ids)} MCP tools registered")
    return tool_ids


def _create_agent(cfg: SetupConfig, client: httpx.Client, tool_ids: list[str]) -> bool:
    """Create or update the Athena agent."""
    if not SYSTEM_PROMPT_PATH.exists():
        console.print(f"  [red]\u2717[/] System prompt not found: {SYSTEM_PROMPT_PATH}")
        return False

    instructions = SYSTEM_PROMPT_PATH.read_text()
    agent_body = {
        "name": "Athena",
        "description": "Second brain orchestrator \u2014 bridges your Obsidian vault with Artemis productivity",
        "configuration": {
            "instructions": instructions,
            "tools": [{"tool_ids": tool_ids}],
        },
    }

    # Check if agent already exists
    r = client.get(
        f"{cfg.kibana_url}/api/agent_builder/agents/athena",
        headers=_kibana_headers(cfg),
    )

    if r.status_code == 200:
        # Update existing agent (no id in body)
        r2 = client.put(
            f"{cfg.kibana_url}/api/agent_builder/agents/athena",
            headers=_kibana_headers(cfg),
            json=agent_body,
        )
        if r2.status_code in (200, 201):
            console.print(
                f"  [green]\u2192[/] Athena agent updated "
                f"({len(tool_ids)} tools, {len(instructions)} char system prompt)"
            )
            return True
        console.print(f"  [red]\u2717[/] Agent update failed: HTTP {r2.status_code}")
        try:
            console.print(f"    {r2.json().get('message', r2.text[:200])}")
        except Exception:
            console.print(f"    {r2.text[:200]}")
        return False
    else:
        # Create new agent (include id)
        agent_body["id"] = "athena"
        r2 = client.post(
            f"{cfg.kibana_url}/api/agent_builder/agents",
            headers=_kibana_headers(cfg),
            json=agent_body,
        )
        if r2.status_code in (200, 201):
            console.print(
                f"  [green]\u2192[/] Athena agent created "
                f"({len(tool_ids)} tools, {len(instructions)} char system prompt)"
            )
            return True
        console.print(f"  [red]\u2717[/] Agent creation failed: HTTP {r2.status_code}")
        try:
            console.print(f"    {r2.json().get('message', r2.text[:200])}")
        except Exception:
            console.print(f"    {r2.text[:200]}")
        return False


def run(cfg: SetupConfig) -> bool:
    """Create all Agent Builder resources. Returns True on success."""
    console.print("\n  [bold][2c] Agent Builder (Kibana)...[/]")

    all_tool_ids: list[str] = []

    with httpx.Client(timeout=30) as client:
        # 1. ES|QL + index search tools
        esql_ids = _create_esql_tools(cfg, client)
        all_tool_ids.extend(esql_ids)
        if esql_ids:
            console.print(f"  [green]\u2192[/] {len(esql_ids)} ES|QL/index tools created")

        # 2. MCP connector + tools (optional)
        if cfg.ngrok_domain:
            if _check_mcp_reachable(cfg, client):
                connector_id = _create_mcp_connector(cfg, client)
                if connector_id:
                    mcp_ids = _register_mcp_tools(cfg, client, connector_id)
                    all_tool_ids.extend(mcp_ids)
            else:
                console.print(
                    f"  [yellow]\u26a0[/] MCP server not reachable at https://{cfg.ngrok_domain}"
                )
                console.print("    Run: docker compose --profile tunnel up --build")
                console.print("    Then re-run: ./setup.sh --phase agent-builder")
        else:
            console.print("  [yellow]\u26a0[/] NGROK_DOMAIN not set — skipping MCP connector + tools")

        # 3. Create/update agent
        if not all_tool_ids:
            console.print("  [red]\u2717[/] No tools registered — cannot create agent")
            return False

        return _create_agent(cfg, client, all_tool_ids)
