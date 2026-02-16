---
name: elastic-agent-builder
description: >
  Manage Elastic Agent Builder resources via the Kibana REST API — agents, tools (ES|QL, index_search, MCP), connectors, and the converse API. Use this skill when:
  (1) Creating, updating, or reading agents in Elastic Agent Builder
  (2) Syncing system prompts or tool configurations to Kibana
  (3) Registering or updating MCP connectors
  (4) Creating or modifying ES|QL or index search tools
  (5) Chatting with an agent via the converse API
  (6) Troubleshooting Agent Builder API errors or field name issues
  (7) Any Kibana API interaction related to Agent Builder
  Triggers on: "sync to agent builder", "update the agent", "register MCP", "create ES|QL tool", "converse API", "Kibana API", "agent builder API", "update system prompt in elastic"
---

# Elastic Agent Builder API

Procedural knowledge for managing Elastic Agent Builder resources via the Kibana REST API.

## Authentication & URL

All requests use the same pattern:

```
URL:     https://<deployment>.kb.<region>.gcp.elastic.cloud:443/api/agent_builder/<resource>
Auth:    Authorization: ApiKey <ELASTIC_API_KEY>
Headers: kbn-xsrf: true, Content-Type: application/json
```

**Deriving Kibana URL from ES URL:** Replace `.es.` with `.kb.` in the Elasticsearch URL.

The ES API key works for Kibana API calls — no separate Kibana credentials needed.

## Quick Reference

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List agents | GET | `/api/agent_builder/agents` |
| Get agent | GET | `/api/agent_builder/agents/{id}` |
| Create agent | POST | `/api/agent_builder/agents` |
| Update agent | PUT | `/api/agent_builder/agents/{id}` |
| Delete agent | DELETE | `/api/agent_builder/agents/{id}` |
| List tools | GET | `/api/agent_builder/tools` |
| Get tool | GET | `/api/agent_builder/tools/{id}` |
| Create tool | POST | `/api/agent_builder/tools` |
| Update tool | PUT | `/api/agent_builder/tools/{id}` |
| Delete tool | DELETE | `/api/agent_builder/tools/{id}` |
| Converse | POST | `/api/agent_builder/converse` |

## Workflow: Determine Operation Type

1. **Updating an agent's system prompt** → Read `agent-config/system-prompt.md`, PUT to agents endpoint
2. **Creating/updating tools** → Read tool JSON from `agent-config/tools/`, POST or PUT to tools endpoint
3. **Registering MCP connector** → POST to connectors API with `serverUrl`
4. **Chatting with agent** → POST to converse endpoint with `input` and `agent_id`
5. **Debugging** → GET the resource first to inspect current state

For detailed API schemas, field names, and gotchas, see [references/api-reference.md](references/api-reference.md).

## Critical Gotchas

These field name mismatches cause silent failures or 400 errors:

| What you'd expect | Actual field name | Context |
|-------------------|-------------------|---------|
| `system_prompt` | `instructions` | Agent creation/update, inside `configuration` |
| `url` | `serverUrl` | MCP connector configuration |
| `keyword` | `string` | ES|QL tool parameter types |
| `id` in PUT body | Omit it | Agent PUT — `id` goes in URL path only |
| `type` in agent body | Omit it | Auto-set by the API |

## Python Pattern for API Calls

Use `urllib.request` (stdlib) or `httpx` — avoid adding dependencies. Read credentials from `.env`:

```python
import json, urllib.request, ssl

# Read from .env or environment
KIBANA_URL = "https://...kb.<region>.gcp.elastic.cloud:443"
API_KEY = "..."

def agent_builder_request(method, path, body=None):
    """Make an authenticated Agent Builder API request."""
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"{KIBANA_URL}/api/agent_builder/{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"ApiKey {API_KEY}",
            "kbn-xsrf": "true",
            "Content-Type": "application/json",
        },
    )
    ctx = ssl.create_default_context()
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {error_body}")
```

## Common Operations

### Update Agent System Prompt

```python
with open("agent-config/system-prompt.md") as f:
    instructions = f.read()

result = agent_builder_request("PUT", f"agents/{agent_id}", {
    "name": "Athena",
    "description": "...",
    "configuration": {
        "instructions": instructions,
        "tools": [{"tool_ids": ["tool.id1", "tool.id2", ...]}],
    },
})
```

**Key:** Do NOT include `id` or `type` in the PUT body. Include the full `configuration` with both `instructions` and `tools` — partial updates may clear fields.

### Create ES|QL Tool

POST the JSON file from `agent-config/tools/` directly:

```python
with open("agent-config/tools/search-notes.json") as f:
    tool_def = json.load(f)

result = agent_builder_request("POST", "tools", tool_def)
```

ES|QL tool JSON schema:
```json
{
  "id": "namespace.tool_name",
  "type": "esql",
  "description": "...",
  "tags": ["tag1"],
  "configuration": {
    "query": "FROM index METADATA _score | WHERE ... | LIMIT ?limit",
    "params": {
      "param_name": {
        "type": "string",  // ONLY: string, integer, float, boolean, date, array
        "description": "..."
      }
    }
  }
}
```

### Converse with Agent

```python
payload = {
    "input": "What are my notes about API refactoring?",
    "agent_id": "athena",
    # Optional: continue existing conversation
    "conversation_id": "existing-conv-id",
    # Optional: inject additional system context
    "configuration_overrides": {
        "systemPromptAddition": "Extra context injected per-request...",
    },
}

result = agent_builder_request("POST", "converse", payload)
# Response: { "response": { "message": "..." }, "conversation_id": "..." }
```

**Response structure:** `result["response"]["message"]` contains the agent's text reply. NOT `result["response"]` directly.
