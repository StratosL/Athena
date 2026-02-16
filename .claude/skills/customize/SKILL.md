---
name: customize
description: >
  Teaches Claude Code how to extend Athena — add MCP tools, vault skills,
  integrations, or modify the agent's capabilities. Covers both skill layers.
---

# Extending Athena

Athena has two skill layers. Use the right one for the job:

## Layer 1: Vault Runtime Skills (for users/agent)

Stored as markdown in `Meta/Skills/` in the Obsidian vault. The Athena agent creates, loads, and executes these via the `skill_manager` MCP tool. No code changes needed.

**When to use:** Reusable multi-step workflows using existing tools (morning routine, meeting debrief, weekly review).

**How to create:**
1. Create a `.md` file in `sample-vault/Meta/Skills/` with frontmatter:
   ```yaml
   title: "Skill Name"
   tags: [skill]
   trigger_phrases: ["phrase1", "phrase2"]
   ```
2. Add `## Steps` section with numbered steps referencing existing tools
3. Add `## Expected Output` describing what the user sees

## Layer 2: Claude Code Developer Skills (for developers)

Stored in `.claude/skills/`. For extending Athena's codebase itself.

**When to use:** Adding new MCP tools, integrations, or modifying infrastructure.

## Adding a New MCP Tool

1. Create tool module: `mcp-server/src/tools/{name}.py`
   - Import `from src.server import mcp` (and any adapters needed)
   - Use `@mcp.tool()` decorator on async functions
   - Follow operation-based dispatch pattern (see `tools/vault.py`)
   - Return `json.dumps(...)` for all responses
   - Handle errors gracefully — never crash

2. Register in server: `mcp-server/src/server.py`
   - Add `import src.tools.{name}` in the tool registration block (line ~56)
   - Keep alphabetical order

3. Update system prompt: `agent-config/system-prompt.md`
   - Add tool docs in Available Tools section
   - Add row in Tool Selection Guide table
   - Add workflow pattern if applicable

4. Sync to Agent Builder (if deployed):
   - Use `/elastic-agent-builder` skill to update the agent

## Key Files

| File | Purpose |
|------|---------|
| `mcp-server/src/server.py` | MCP server setup, adapter initialization, tool registration |
| `mcp-server/src/config.py` | Settings via pydantic-settings (all secrets from .env) |
| `mcp-server/src/vault_manager.py` | Obsidian vault filesystem operations |
| `mcp-server/src/artemis_client.py` | Artemis REST API client |
| `mcp-server/src/es_client.py` | Elasticsearch knowledge store |
| `mcp-server/src/tools/*.py` | MCP tool modules (vault, artemis, knowledge, research, skills) |
| `agent-config/system-prompt.md` | Agent Builder system prompt |
| `voice-client/serve.py` | Voice proxy server (injects memory + skills into context) |
| `sample-vault/Meta/Skills/` | Runtime skill definitions |

## Coding Standards

- Python 3.12+, `uv` for package management
- `pydantic` v2 for models, `pydantic-settings` for config
- `httpx` for async HTTP, `python-frontmatter` for YAML parsing
- Type hints on all functions, docstrings on public classes
- Error handling: return error messages via `json.dumps`, never crash
