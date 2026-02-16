---
name: add-integration
description: >
  Step-by-step guide for adding a new external service integration to Athena.
  Creates the client adapter, MCP tool module, config, and registration.
---

# Adding a New Service Integration

Follow these steps to integrate a new external service (e.g., calendar, email, Slack) into Athena as MCP tools.

## Step 1: Create Client Adapter

Create `mcp-server/src/{service}_client.py`:

```python
"""Client adapter for {Service} API."""

import logging
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class {Service}Client:
    """Async client for {Service} REST API."""

    def __init__(self, base_url: str, api_key: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an authenticated request to {Service}."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method, f"{self.base_url}{path}", headers=headers, **kwargs
            )
            resp.raise_for_status()
            return resp.json()
```

**Pattern:** Follow `artemis_client.py` for the request pattern. Use `httpx` for async HTTP.

## Step 2: Create Tool Module

Create `mcp-server/src/tools/{service}.py`:

```python
"""MCP tools for {Service} integration."""

import json
import logging
from src.server import mcp, {service}_client

logger = logging.getLogger(__name__)

@mcp.tool()
async def {service}_do_thing(param: str) -> str:
    """Description of what this tool does.

    Args:
        param: What this parameter controls.
    """
    try:
        result = await {service}_client.do_thing(param)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"{service} error: {e}"})
```

**Pattern:** Follow `tools/artemis.py` for individual tools or `tools/vault.py` for operation-based dispatch.

## Step 3: Update Config

Add settings to `mcp-server/src/config.py`:

```python
# In the Settings class:
{service}_base_url: str = ""
{service}_api_key: str = ""
```

Add corresponding entries to `.env.example`.

## Step 4: Register in Server

Edit `mcp-server/src/server.py`:

1. Initialize the client adapter (after existing adapters):
   ```python
   from src.{service}_client import {Service}Client
   {service}_client = {Service}Client(settings.{service}_base_url, settings.{service}_api_key)
   ```

2. Register the tool module (in the imports block):
   ```python
   import src.tools.{service}  # noqa: E402, F401
   ```

## Step 5: Update System Prompt

Edit `agent-config/system-prompt.md`:

1. Add a `### MCP Tools — {Service}` section under Available Tools
2. Add rows to the Tool Selection Guide table
3. Add a workflow pattern if the integration enables a new multi-step flow

## Step 6: Sync to Agent Builder

Use the `/elastic-agent-builder` skill to update the agent configuration in Kibana.

## Verification Checklist

- [ ] `ruff check mcp-server/src/{service}_client.py` — no lint errors
- [ ] `ruff check mcp-server/src/tools/{service}.py` — no lint errors
- [ ] MCP server starts without errors
- [ ] New tools appear in `tools/list` response
- [ ] Tool calls return expected results
- [ ] Error cases return JSON error messages (no crashes)
