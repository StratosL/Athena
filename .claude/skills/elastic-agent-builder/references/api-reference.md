# Elastic Agent Builder API Reference

Comprehensive reference for all Agent Builder REST API endpoints, schemas, and gotchas.

## Table of Contents

- [Authentication](#authentication)
- [Agents API](#agents-api)
- [Tools API](#tools-api)
- [Connectors API](#connectors-api)
- [Converse API](#converse-api)
- [MCP Integration](#mcp-integration)
- [ES|QL Tool Patterns](#esql-tool-patterns)
- [Index Search Tool Pattern](#index-search-tool-pattern)
- [Field Name Gotchas](#field-name-gotchas)
- [Error Patterns](#error-patterns)
- [Elasticsearch Index Management](#elasticsearch-index-management)

---

## Authentication

All Agent Builder API calls go through Kibana (not the ES endpoint).

```
Base URL:  https://<deployment>.kb.<region>.gcp.elastic.cloud:443
Auth:      Authorization: ApiKey <ELASTIC_API_KEY>
Required:  kbn-xsrf: true
Content:   Content-Type: application/json
```

**URL derivation:** If ES URL is `https://foo.es.europe-west3.gcp.elastic.cloud:443`, Kibana URL is `https://foo.kb.europe-west3.gcp.elastic.cloud:443`.

The same `ELASTIC_API_KEY` used for Elasticsearch works for Kibana API calls.

---

## Agents API

### Create Agent

```
POST /api/agent_builder/agents
```

**Request body:**
```json
{
  "id": "my-agent",
  "name": "My Agent",
  "description": "What this agent does",
  "configuration": {
    "instructions": "Full system prompt text...",
    "tools": [
      {
        "tool_ids": [
          "namespace.tool1",
          "namespace.tool2",
          "connector_prefix.mcp_tool_name"
        ]
      }
    ]
  }
}
```

**Required fields:** `id`, `name`, `description`, `configuration.instructions`, `configuration.tools`

**Do NOT include:** `type` (auto-set to `"chat"`)

### Get Agent

```
GET /api/agent_builder/agents/{id}
```

**Response:** Full agent object including `id`, `type`, `name`, `description`, `configuration`, `readonly`.

### Update Agent

```
PUT /api/agent_builder/agents/{id}
```

**Request body:** Same as create, but **without `id`** (it's in the URL path).

```json
{
  "name": "My Agent",
  "description": "Updated description",
  "configuration": {
    "instructions": "Updated system prompt...",
    "tools": [{"tool_ids": ["tool1", "tool2"]}]
  }
}
```

**CRITICAL:** Including `id` in the body returns `400: definition for this key is missing`. The `id` goes ONLY in the URL.

**CRITICAL:** Always include `configuration.tools` when updating — omitting it may clear the tool assignments.

### Delete Agent

```
DELETE /api/agent_builder/agents/{id}
```

### List Agents

```
GET /api/agent_builder/agents
```

---

## Tools API

### Tool Types

| Type | Purpose | Key config |
|------|---------|------------|
| `esql` | ES\|QL query with parameters | `configuration.query`, `configuration.params` |
| `index_search` | Dynamic natural-language search | `configuration.pattern`, `configuration.row_limit`, `configuration.custom_instructions` |
| `mcp` | MCP server tool proxy | `configuration.connector_id`, `configuration.tool_name` |

### Create Tool

```
POST /api/agent_builder/tools
```

**ES|QL tool body:**
```json
{
  "id": "namespace.tool_name",
  "type": "esql",
  "description": "What this tool does and when to use it",
  "tags": ["category1", "category2"],
  "configuration": {
    "query": "FROM index METADATA _score | WHERE MATCH(field, ?param) | LIMIT ?limit",
    "params": {
      "param": {
        "type": "string",
        "description": "What this parameter controls"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum results"
      }
    }
  }
}
```

**Parameter types allowed:** `string`, `integer`, `float`, `boolean`, `date`, `array`

**NOT allowed:** `keyword`, `text`, `long`, `double` — these all return validation errors.

**Index search tool body:**
```json
{
  "id": "namespace.tool_name",
  "type": "index_search",
  "description": "Dynamic search description",
  "tags": ["search"],
  "configuration": {
    "pattern": "index-name",
    "row_limit": 10,
    "custom_instructions": "Description of index fields and how to search them..."
  }
}
```

**MCP tool body:**
```json
{
  "id": "prefix.tool_name",
  "type": "mcp",
  "description": "Auto-discovered from MCP server",
  "tags": ["mcp"],
  "configuration": {
    "connector_id": "connector-uuid",
    "tool_name": "tool_name_from_mcp_server"
  }
}
```

### Get / Update / Delete Tool

```
GET    /api/agent_builder/tools/{id}
PUT    /api/agent_builder/tools/{id}    (body same as create, without id)
DELETE /api/agent_builder/tools/{id}
```

### List Tools

```
GET /api/agent_builder/tools
```

---

## Connectors API

Connectors are managed through the Kibana Actions API, not the Agent Builder API.

### Create MCP Connector

```
POST /api/actions/connector
```

```json
{
  "name": "My MCP Server",
  "connector_type_id": ".mcp",
  "config": {
    "serverUrl": "https://your-mcp-server-url.example.com"
  },
  "secrets": {}
}
```

**CRITICAL:** The URL field is `serverUrl` (camelCase), NOT `url` or `server_url`.

**Response:** `{ "id": "uuid-of-connector", ... }`

Save the connector `id` — needed for registering MCP tools.

### Update MCP Connector

```
PUT /api/actions/connector/{id}
```

```json
{
  "name": "My MCP Server",
  "config": {
    "serverUrl": "https://new-url.example.com"
  },
  "secrets": {}
}
```

### Test Connector

```
POST /api/actions/connector/{id}/_execute
```

```json
{
  "params": {
    "subAction": "test"
  }
}
```

---

## Converse API

Chat with an agent programmatically.

```
POST /api/agent_builder/converse
```

**Request:**
```json
{
  "input": "User message text",
  "agent_id": "agent-id",
  "conversation_id": "optional-existing-conversation-id",
  "configuration_overrides": {
    "systemPromptAddition": "Optional per-request context injected after the main system prompt"
  }
}
```

**Response:**
```json
{
  "response": {
    "message": "Agent's text response here"
  },
  "conversation_id": "conversation-uuid"
}
```

**CRITICAL:** The agent message is at `response.response.message`, NOT `response.response`. The `response` field contains an object with a `message` key.

**`configuration_overrides.systemPromptAddition`** is useful for injecting per-request context (user profile, memory, session state) without modifying the stored system prompt.

---

## MCP Integration

### MCP Server Requirements

Elastic Agent Builder requires:
- **Streamable HTTP** transport (NOT SSE, NOT stdio)
- POST to root path `/` (set `streamable_http_path="/"` in FastMCP)
- Public HTTPS URL (via ngrok, Railway, or similar)

FastMCP configuration:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "ServerName",
    host="0.0.0.0",
    port=8001,
    streamable_http_path="/",  # Elastic POSTs to /
)
```

### Registering MCP Tools

After creating the MCP connector, tools are discovered automatically. Register each as a tool:

```json
{
  "id": "prefix.tool_name",
  "type": "mcp",
  "description": "Copied from MCP tool description",
  "tags": ["mcp"],
  "configuration": {
    "connector_id": "5cbb794c-fc8d-49d8-adb2-b9c9a07c37f1",
    "tool_name": "vault_query"
  }
}
```

The `tool_name` must match exactly what the MCP server reports in `tools/list`.

---

## ES|QL Tool Patterns

### Hybrid Semantic + Full-text Search

```sql
FROM athena-notes METADATA _score
| WHERE MATCH(content_semantic, ?query, {"boost": 0.7})
    OR MATCH(content, ?query, {"boost": 0.3})
| KEEP title, vault_relative_path, tags, note_type, word_count, updated_at, _score
| SORT _score DESC
| LIMIT ?limit
```

### Tag Filter with Multi-value Expansion

```sql
FROM athena-notes
| MV_EXPAND tags
| WHERE tags == ?tag
| KEEP title, vault_relative_path, tags, note_type, updated_at
| SORT updated_at DESC
| LIMIT 20
```

`MV_EXPAND` is required before filtering on keyword array fields.

### Tag Aggregation

```sql
FROM athena-notes
| MV_EXPAND tags
| STATS note_count = COUNT(*) BY tags
| SORT note_count DESC
| LIMIT 20
```

### Temporal Filter

```sql
FROM athena-notes
| WHERE updated_at >= NOW() - TO_TIMEDURATION(?time_range)
| KEEP title, vault_relative_path, tags, note_type, updated_at
| SORT updated_at DESC
| LIMIT ?limit
```

Parameter: `time_range` with type `string` (e.g., `"7d"`, `"30d"`).

### Semantic Search on Conversations

```sql
FROM athena-conversations METADATA _score
| WHERE MATCH(summary_semantic, ?topic)
| KEEP summary, topics, extracted_tasks, task_ids_created, timestamp, _score
| SORT _score DESC
| LIMIT ?limit
```

---

## Index Search Tool Pattern

For dynamic, natural-language-driven searches that go beyond predefined ES|QL templates:

```json
{
  "id": "namespace.semantic_search",
  "type": "index_search",
  "configuration": {
    "pattern": "index-name",
    "row_limit": 10,
    "custom_instructions": "Describe the index schema here: field names, types, and search guidance. Tell the LLM which fields to use for semantic vs keyword search."
  }
}
```

---

## Field Name Gotchas

Consolidated list of field names that differ from what you'd expect:

| Context | Expected | Actual | Notes |
|---------|----------|--------|-------|
| Agent system prompt | `system_prompt` | `instructions` | Inside `configuration` object |
| Agent update body | `id` in body | Omit `id` | 400 error: "definition for this key is missing" |
| Agent body | `type` field | Omit `type` | Auto-set to "chat" |
| MCP connector URL | `url` | `serverUrl` | camelCase, inside `config` |
| ES\|QL param type | `keyword` | `string` | Only: string, integer, float, boolean, date, array |
| Converse response | `response` (string) | `response.message` | Response is an object, not a string |
| Connector API path | `/api/agent_builder/connectors` | `/api/actions/connector` | Uses the Actions API |

---

## Error Patterns

| HTTP Code | Error Message | Cause | Fix |
|-----------|--------------|-------|-----|
| 400 | `definition for this key is missing` | Unknown field in request body | Remove `id` from PUT body, or remove `type` from agent body |
| 400 | `expected value of type [string]` | Wrong parameter type in ES\|QL tool | Use `string` instead of `keyword` |
| 404 | `Not Found` | Wrong URL path or resource doesn't exist | Check endpoint path, verify resource ID |
| 409 | `version conflict` | Concurrent update | GET latest version, retry PUT |
| 502 | MCP connector timeout | MCP server unreachable | Check ngrok tunnel, verify server is running |
