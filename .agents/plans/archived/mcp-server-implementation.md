# Feature: MCP Server — Unified Tool Server with SSE Transport

The following plan should be complete, but its important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Build the unified MCP server that Agent Builder connects to via SSE transport. This is the central piece — it hosts all 13 MCP tools across 4 groups (vault, Artemis, knowledge, research) and adapts 3 external systems (Obsidian vault filesystem, Artemis REST API, Elasticsearch) through dedicated client/manager classes.

The MCP server is the **only new runtime** Athena introduces. Everything else is either configuration (Agent Builder, ES|QL tools) or already built (indexer, sample vault). Without this server, the agent has no tools.

## User Story

As a knowledge worker using Athena via Agent Builder,
I want a single MCP server that exposes vault access, task management, knowledge persistence, and web research tools,
So that the Athena agent can search my notes, create tasks, save conversations, and research topics through one connection.

## Problem Statement

The MCP server directory has config, Dockerfile, and docstring stubs — but zero functional code. Agent Builder cannot call any tools until this server is running with SSE transport and all tools registered.

## Solution Statement

Implement 7 files in dependency order: `vault_manager.py` (filesystem CRUD), `artemis_client.py` (httpx wrapper), `es_client.py` (ES write-back), then `tools/vault.py` (3 tools), `tools/artemis.py` (7 tools), `tools/knowledge.py` (1 tool), `tools/research.py` (2 tools), and finally `server.py` (FastMCP with SSE transport that wires everything together).

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: High
**Primary Systems Affected**: `mcp-server/src/` (7 files to implement, 1 to update)
**Dependencies**: `mcp[cli]>=1.3.0`, `httpx>=0.27.0`, `elasticsearch[async]>=8.17.0`, `python-frontmatter>=1.1.0`, `pydantic>=2.7.0`, `pydantic-settings>=2.5.0`, `html2text>=2024.2.26`

---

## CONTEXT REFERENCES

### Relevant Codebase Files — MUST READ BEFORE IMPLEMENTING

**Existing implemented code (patterns to follow):**

- `indexer/src/config.py` — pydantic-settings pattern: `BaseSettings` with `model_config`, `get_settings()` factory. Mirror this style.
- `indexer/src/parser.py` (lines 91-155) — Frontmatter parsing pattern with `python-frontmatter`: `frontmatter.load(f)`, tag handling (str or list), date parsing, path validation.
- `indexer/src/indexer.py` (lines 39-43) — ES client creation pattern: `AsyncElasticsearch(hosts=[url], api_key=key)`.
- `indexer/src/watcher.py` — Shows how existing code handles async patterns, logging, error handling.

**MCP server stubs (replace these):**

- `mcp-server/src/config.py` — **Already implemented.** `ServerSettings` with all fields: `vault_path`, `artemis_base_url`, `elastic_url`, `elastic_api_key`, `conversations_index`, `mcp_server_port`, `tavily_api_key`, `brave_api_key`, `log_level`.
- `mcp-server/src/server.py` — Docstring stub only. Replace entirely.
- `mcp-server/src/vault_manager.py` — Docstring stub only. Replace entirely.
- `mcp-server/src/artemis_client.py` — Docstring stub only. Replace entirely.
- `mcp-server/src/es_client.py` — Docstring stub only. Replace entirely.
- `mcp-server/src/tools/vault.py` — Docstring stub only. Replace entirely.
- `mcp-server/src/tools/artemis.py` — Docstring stub only. Replace entirely.
- `mcp-server/src/tools/knowledge.py` — Docstring stub only. Replace entirely.
- `mcp-server/src/tools/research.py` — Docstring stub only. Replace entirely.
- `mcp-server/Dockerfile` — **Already implemented.** Multi-stage uv build, `CMD ["python", "-m", "src.server"]`.

**Reference implementations (READ-ONLY — study patterns, don't copy verbatim):**

- `reference/obsidian-ai-agent/app/shared/vault/vault_manager.py` — Primary blueprint for VaultManager: path validation via resolve() + startswith(), frontmatter parsing, CRUD operations, search scoring (filename=100, title=50, content=1).
- `reference/obsidian-ai-agent/app/shared/vault/vault_models.py` — Pydantic models: `Frontmatter`, `Note`, `VaultPath` with `validate_within_vault()`.
- `reference/obsidian-ai-agent/app/features/obsidian_note_manager_tool/obsidian_note_manager_tool.py` — 12-operation dispatch pattern via `Literal` type, `confirm_destructive` gate for deletes, structured result model with `success`, `message`, `fix_suggestion`.
- `reference/obsidian-ai-agent/app/features/obsidian_query_vault_tool/obsidian_query_vault_tool.py` — Query dispatch, `response_format` parameter (concise/detailed), `SearchFilters` model.
- `reference/obsidian-ai-agent/app/features/obsidian_get_context_tool/obsidian_get_context_tool.py` — Read dispatch, daily note discovery with multiple path conventions, token estimation.
- `reference/obsidian-productivity-agent/backend_agent_api/tools.py` — Brave Search implementation: `https://api.search.brave.com/res/v1/web/search` with `X-Subscription-Token` header.

**Artemis API (verified against actual code):**

- `POST /tasks` — body: `{title (str, 1-200 chars), quadrant (int 1-4), description? (str, max 2000), due_date? (ISO datetime)}` → 201 + `TaskResponse`
- `GET /tasks?quadrant=&status=&limit=100&offset=0` → `{items: TaskResponse[], total: int}`
- `POST /tasks/{task_id}/complete` → `TaskResponse` (status="completed"). Error: 404.
- `GET /daily-plans/today` → `DailyPlanResponse` (auto-creates if missing). Includes expanded `major_task`, `medium_tasks[]`, `small_tasks[]` as `TaskInfo` objects.
- `POST /daily-plans/{plan_id}/tasks` — body: `{task_id (str), slot ("major"|"medium"|"small")}` → `DailyPlanResponse`. Errors: 400 (slot full, task invalid), 404 (plan not found), 409 (already assigned).
- `GET /analytics/summary?period=day|week|month` → `AnalyticsSummary` with `daily_plan_stats` and `productivity_score`.
- `POST /pomodoro/start` — body: `{task_id? (str), duration_minutes? (int, 1-90, default 25)}` → 201 + `PomodoroSessionResponse`. Error: 409 (session already active). Note: service hardcodes 25 min.
- `GET /health` → `{status, version, database}`

**Elasticsearch conversations index mapping** (from `indexer/src/mappings.py`):

```
athena-conversations:
  summary: text
  summary_semantic: semantic_text (ELSER)
  topics: keyword[]
  extracted_tasks: text[]
  task_ids_created: keyword[]
  timestamp: date
```

### New Files to Create

| File | Purpose | Lines (est.) |
|------|---------|-------------|
| `mcp-server/src/vault_manager.py` | VaultManager class — filesystem CRUD, path validation, frontmatter | ~250 |
| `mcp-server/src/artemis_client.py` | ArtemisClient class — httpx wrapper for Artemis REST API | ~130 |
| `mcp-server/src/es_client.py` | KnowledgeStore class — ES client for conversation write-back | ~60 |
| `mcp-server/src/tools/vault.py` | 3 vault MCP tools (query, read, manage) | ~200 |
| `mcp-server/src/tools/artemis.py` | 7 Artemis MCP tools | ~200 |
| `mcp-server/src/tools/knowledge.py` | 1 knowledge MCP tool (save_conversation_summary) | ~50 |
| `mcp-server/src/tools/research.py` | 2 research MCP tools (web_search, fetch_url) | ~120 |
| `mcp-server/src/server.py` | FastMCP server with SSE transport, wires all tools | ~80 |

### Relevant Documentation — READ BEFORE IMPLEMENTING

- [MCP Python SDK — FastMCP](https://github.com/modelcontextprotocol/python-sdk)
  - `FastMCP("name")` creates server. `@mcp.tool()` registers tools (must use parentheses).
  - `mcp.run(transport="sse", host="0.0.0.0", port=8001)` starts SSE server.
  - Tools return `str` → `TextContent`. Exceptions caught → `isError=True` response.
  - `Context` parameter auto-excluded from schema. Use for logging: `ctx.info()`, `ctx.warning()`.
- [python-frontmatter docs](https://python-frontmatter.readthedocs.io/)
  - `frontmatter.load(f)` → `Post` with `.metadata` dict and `.content` str.
  - `frontmatter.Post(content, **metadata)` → create, `frontmatter.dumps(post)` → serialize.
- [httpx async client](https://www.python-httpx.org/async/)
  - `async with httpx.AsyncClient(base_url=url, timeout=30.0) as client:`
  - `client.get()`, `client.post(json=...)`, `response.raise_for_status()`, `response.json()`
- [Brave Search API](https://api.search.brave.com/app/documentation/web-search/get-started)
  - `GET https://api.search.brave.com/res/v1/web/search?q=query&count=5`
  - Header: `X-Subscription-Token: <api_key>`
- [Tavily Search API](https://docs.tavily.com/documentation/api-reference/search)
  - `POST https://api.tavily.com/search` body: `{api_key, query, max_results: 5}`
- [html2text](https://github.com/Alir3z4/html2text/)
  - `html2text.html2text(html_string)` → clean markdown text

### Patterns to Follow

**MCP tool registration** (FastMCP):
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Athena")

@mcp.tool()
async def tool_name(param: str, optional_param: int = 5) -> str:
    """Tool description shown to the LLM.

    Args:
        param: Description of param.
        optional_param: Description with default.
    """
    try:
        result = await do_something(param)
        return json.dumps(result)
    except Exception as e:
        return f"Error: {e}"
```

**Error handling (CLAUDE.md rule):** Return error messages as strings, never crash. Every tool wraps in try/except:
```python
try:
    # ... work ...
    return json.dumps({"success": True, ...})
except FileNotFoundError:
    return json.dumps({"error": f"Note not found: {path}"})
except Exception as e:
    return json.dumps({"error": f"Failed: {e}"})
```

**Path validation** (from reference vault_manager.py):
```python
def _validate_path(self, relative_path: str) -> Path:
    abs_path = (self.vault_root / relative_path).resolve()
    if not str(abs_path).startswith(str(self.vault_root)):
        raise ValueError(f"Path escapes vault root: {relative_path}")
    return abs_path
```

**Frontmatter write** (from reference):
```python
import frontmatter
post = frontmatter.Post(content, title=title, tags=tags, created=date_str, updated=date_str)
file_path.write_text(frontmatter.dumps(post), encoding="utf-8")
```

**httpx async client pattern:**
```python
class ArtemisClient:
    def __init__(self, base_url: str) -> None:
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def close(self) -> None:
        await self.client.aclose()

    async def create_task(self, title: str, quadrant: int, ...) -> dict:
        resp = await self.client.post("/tasks", json={...})
        resp.raise_for_status()
        return resp.json()
```

**Logging pattern** (consistent with indexer):
```python
import logging
logger = logging.getLogger(__name__)
```

**Naming conventions:** snake_case functions, CamelCase classes, ALL_CAPS constants. `ruff` with py312 target, 100-char line length.

---

## IMPLEMENTATION PLAN

### Phase 1: Adapter Classes (No MCP dependency)

Build the three adapter classes that wrap external systems. These are pure Python with no MCP coupling — they can be tested independently.

**Order**: VaultManager → ArtemisClient → KnowledgeStore

1. `vault_manager.py` — Filesystem CRUD with path validation, frontmatter parsing, search, and security. Largest and most complex piece. Directly inspired by the reference obsidian-ai-agent VaultManager.
2. `artemis_client.py` — Thin httpx async wrapper over 7 Artemis endpoints. Straightforward request/response mapping.
3. `es_client.py` — Minimal ES async client for indexing conversation summaries. Single method.

### Phase 2: MCP Tools

Build the 4 tool modules. Each registers tools on a shared `FastMCP` instance using `@mcp.tool()`. Tools delegate to adapter classes from Phase 1.

**Order**: Artemis tools (P0) → Vault tools (P0/P1) → Knowledge tools (P0) → Research tools (P2)

4. `tools/artemis.py` — 7 tools proxying to ArtemisClient. Most demo-critical.
5. `tools/vault.py` — 3 consolidated tools dispatching to VaultManager operations.
6. `tools/knowledge.py` — 1 tool writing to KnowledgeStore.
7. `tools/research.py` — 2 tools for web search and URL fetch. Lowest priority.

### Phase 3: Server Wiring

Wire everything together in `server.py` — create FastMCP instance, initialize adapters, import tool modules, run SSE transport.

8. `server.py` — Entry point. Creates FastMCP, initializes adapter singletons, imports tool modules, runs SSE.

### Phase 4: Validation

Lint, smoke test, Docker build, MCP Inspector verification.

---

## STEP-BY-STEP TASKS

### Task 1: CREATE `mcp-server/src/vault_manager.py`

Replace the docstring stub with a full VaultManager implementation.

**Pydantic models** (define at top of file):

```python
class NoteSummary(BaseModel):
    """Lightweight note info for list/search results."""
    path: str              # vault-relative path
    title: str
    tags: list[str] = Field(default_factory=list)
    note_type: str = "note"
    word_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

class NoteContent(BaseModel):
    """Full note content with frontmatter."""
    path: str              # vault-relative path
    title: str
    content: str           # markdown body (no frontmatter)
    tags: list[str] = Field(default_factory=list)
    note_type: str = "note"
    word_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)  # all frontmatter key-value pairs
```

**VaultManager class methods:**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `__init__` | `(vault_path: str \| Path)` | Resolve root, validate exists + is dir |
| `_validate_path` | `(relative_path: str) -> Path` | Resolve, check startswith vault_root. Raises `ValueError` |
| `_parse_frontmatter` | `(file_path: Path) -> tuple[dict, str]` | `frontmatter.load()`, return (metadata_dict, content). On error: return ({}, raw_text) |
| `_note_summary` | `(file_path: Path) -> NoteSummary` | Parse frontmatter, build NoteSummary |
| `_note_type_from_path` | `(rel_path: str) -> str` | Same `NOTE_TYPE_FOLDER_MAP` as indexer parser |
| `read_note` | `(relative_path: str) -> NoteContent` | Read file, parse frontmatter, return full content |
| `read_multiple` | `(paths: list[str]) -> list[NoteContent]` | Read multiple notes, skip errors with warnings |
| `daily_note` | `(date: str \| None = None) -> NoteContent` | Try `Daily Notes/{date}.md` then `daily/{date}.md` then `{date}.md`. Default date = today |
| `write_note` | `(relative_path: str, content: str, tags: list[str] \| None, metadata: dict \| None) -> NoteContent` | Create .md with frontmatter (title, tags, created, updated). Auto-create parent dirs. Raise if exists |
| `append_to_note` | `(relative_path: str, content: str) -> NoteContent` | Read existing, append content, preserve frontmatter, write back |
| `edit_note` | `(relative_path: str, old_text: str, new_text: str) -> NoteContent` | str_replace: must match exactly once. Raise ValueError if 0 or >1 matches |
| `delete_note` | `(relative_path: str, confirm_destructive: bool) -> bool` | Delete file. Return False if confirm_destructive != True |
| `move_note` | `(source: str, destination: str) -> NoteContent` | Move file, auto-create dest parent dirs |
| `create_folder` | `(relative_path: str) -> bool` | Create folder(s) with exist_ok=True |
| `list_notes` | `(folder: str \| None = None, recursive: bool = False) -> list[NoteSummary]` | List .md files, skip hidden dirs |
| `search_content` | `(query: str, limit: int = 10) -> list[NoteSummary]` | Case-insensitive keyword search across title + content. Score: filename=100, title=50, content=1 |
| `search_by_metadata` | `(tags: list[str] \| None, folder: str \| None, date_range_days: int \| None) -> list[NoteSummary]` | Filter notes by tag intersection, folder prefix, modified-within-N-days |
| `get_recent_notes` | `(limit: int = 10) -> list[NoteSummary]` | Sort all notes by mtime descending, return top N |

**SECURITY**: `_validate_path()` is called as the first line of every public method that accepts a path parameter. No exceptions.

**PATTERN**: Mirror frontmatter parsing from `indexer/src/parser.py` lines 91-155 and `reference/obsidian-ai-agent/app/shared/vault/vault_manager.py`.

**GOTCHA**: Use same `NOTE_TYPE_FOLDER_MAP` as indexer parser (projects→project, ideas→idea, etc.) — define locally, don't import cross-project.

**GOTCHA**: `search_content` must be synchronous filesystem search (no ES). It's the fallback when ES is unavailable.

**GOTCHA**: `append_to_note` must preserve existing frontmatter. Read with `frontmatter.load()`, append to content, write back with `frontmatter.dumps()`.

**GOTCHA**: `edit_note` — count occurrences of `old_text` in content. If 0: raise `ValueError("Text not found")`. If >1: raise `ValueError("Text matches multiple locations — provide more context")`. If 1: replace and write back.

**IMPORTS**: `pathlib.Path`, `logging`, `datetime`, `frontmatter`, `pydantic.BaseModel`, `pydantic.Field`

**VALIDATE**: `cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/vault_manager.py`

---

### Task 2: CREATE `mcp-server/src/artemis_client.py`

Replace the docstring stub with an httpx async client wrapper for Artemis.

**ArtemisClient class:**

```python
class ArtemisClient:
    """Async HTTP client for the Artemis REST API."""

    def __init__(self, base_url: str) -> None:
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def close(self) -> None:
        await self.client.aclose()
```

**Methods:**

| Method | Signature | Artemis Endpoint |
|--------|-----------|-----------------|
| `create_task` | `(title: str, quadrant: int, description: str \| None = None, due_date: str \| None = None) -> dict` | `POST /tasks` |
| `list_tasks` | `(quadrant: int \| None = None, status: str \| None = None, limit: int = 100, offset: int = 0) -> dict` | `GET /tasks` |
| `complete_task` | `(task_id: str) -> dict` | `POST /tasks/{task_id}/complete` |
| `get_daily_plan` | `() -> dict` | `GET /daily-plans/today` |
| `assign_to_plan` | `(plan_id: str, task_id: str, slot: str) -> dict` | `POST /daily-plans/{plan_id}/tasks` |
| `get_analytics` | `(period: str = "week") -> dict` | `GET /analytics/summary` |
| `start_pomodoro` | `(task_id: str \| None = None, duration_minutes: int = 25) -> dict` | `POST /pomodoro/start` |
| `health_check` | `() -> dict` | `GET /health` |

**Each method pattern:**
```python
async def create_task(self, title: str, quadrant: int, ...) -> dict:
    body = {"title": title, "quadrant": quadrant}
    if description:
        body["description"] = description
    if due_date:
        body["due_date"] = due_date
    resp = await self.client.post("/tasks", json=body)
    resp.raise_for_status()
    return resp.json()
```

**GOTCHA**: `list_tasks` uses query params, not body. Build params dict, exclude None values.
**GOTCHA**: `assign_to_plan` slot must be exactly `"major"`, `"medium"`, or `"small"`.
**GOTCHA**: `start_pomodoro` body can be empty (all fields optional). Send `{}` if no task_id.
**GOTCHA**: `httpx.HTTPStatusError` is raised by `raise_for_status()` — callers (tools) must catch this.

**IMPORTS**: `httpx`, `logging`

**VALIDATE**: `cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/artemis_client.py`

---

### Task 3: CREATE `mcp-server/src/es_client.py`

Replace the docstring stub with a minimal ES async client for conversation write-back.

**KnowledgeStore class:**

```python
class KnowledgeStore:
    """Elasticsearch client for writing conversation summaries."""

    def __init__(self, elastic_url: str, api_key: str, conversations_index: str) -> None:
        self.es = AsyncElasticsearch(hosts=[elastic_url], api_key=api_key)
        self.conversations_index = conversations_index

    async def close(self) -> None:
        await self.es.close()

    async def save_conversation(
        self,
        summary: str,
        topics: list[str],
        extracted_tasks: list[str] | None = None,
        task_ids_created: list[str] | None = None,
    ) -> str:
        """Index a conversation summary. Returns the document ID."""
        doc = {
            "summary": summary,
            "summary_semantic": summary,  # ELSER embeds at index time
            "topics": topics,
            "extracted_tasks": extracted_tasks or [],
            "task_ids_created": task_ids_created or [],
            "timestamp": datetime.now(UTC).isoformat(),
        }
        result = await self.es.index(index=self.conversations_index, document=doc)
        return result["_id"]
```

**PATTERN**: Match ES client creation from `indexer/src/indexer.py` lines 39-43.
**GOTCHA**: `summary_semantic` = same as `summary` (ELSER handles embedding at index time, same pattern as `content_semantic` in indexer).
**GOTCHA**: If ES credentials are empty (optional for dev), skip initialization and return error strings from tools.

**IMPORTS**: `elasticsearch.AsyncElasticsearch`, `datetime`, `logging`

**VALIDATE**: `cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/es_client.py`

---

### Task 4: CREATE `mcp-server/src/tools/artemis.py`

Replace the docstring stub with 7 MCP tools that proxy to ArtemisClient.

**Architecture**: Each tool receives its parameters from the LLM, delegates to `artemis_client`, and returns a JSON string result. Import the shared `mcp` instance and `artemis_client` from `server.py` module.

**Tools to implement:**

```python
@mcp.tool()
async def artemis_create_task(
    title: str,
    quadrant: int,
    description: str = "",
    due_date: str = "",
) -> str:
    """Create a new task in Artemis with Eisenhower Matrix classification.

    Args:
        title: Task title (1-200 chars).
        quadrant: Eisenhower quadrant (1=urgent+important, 2=not-urgent+important, 3=urgent+not-important, 4=not-urgent+not-important).
        description: Optional task description.
        due_date: Optional due date in ISO format (e.g. 2026-02-20).
    """
```

| Tool | Parameters | Notes |
|------|-----------|-------|
| `artemis_create_task` | title, quadrant, description="", due_date="" | Convert empty strings to None before passing |
| `artemis_list_tasks` | quadrant: int = 0, status: str = "" | 0/empty = no filter |
| `artemis_complete_task` | task_id: str | Simple proxy |
| `artemis_get_daily_plan` | (none) | Returns today's plan with expanded tasks |
| `artemis_assign_to_plan` | plan_id: str, task_id: str, slot: str | slot: "major", "medium", "small" |
| `artemis_get_analytics` | period: str = "week" | "day", "week", "month" |
| `artemis_start_pomodoro` | task_id: str = "" | Empty = unlinked session |

**Error handling pattern** (every tool):
```python
try:
    result = await artemis_client.create_task(...)
    return json.dumps(result)
except httpx.HTTPStatusError as e:
    error_body = e.response.text
    return json.dumps({"error": f"Artemis returned {e.response.status_code}: {error_body}"})
except httpx.ConnectError:
    return json.dumps({"error": "Cannot connect to Artemis. Is it running?"})
except Exception as e:
    return json.dumps({"error": f"Unexpected error: {e}"})
```

**GOTCHA**: MCP tool parameters must have type annotations. Use `str` with empty string defaults instead of `str | None` for optional params — LLMs handle empty strings better than null.
**GOTCHA**: `quadrant` default of 0 means "no filter" for list_tasks. Convert to None before passing to client.
**GOTCHA**: `artemis_assign_to_plan` slot must be validated: if slot not in ("major", "medium", "small"), return error.

**IMPORTS**: `json`, `httpx`, `logging`

**VALIDATE**: `cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/tools/artemis.py`

---

### Task 5: CREATE `mcp-server/src/tools/vault.py`

Replace the docstring stub with 3 consolidated vault MCP tools.

**Architecture**: 3 tools with `operation` Literal parameter, dispatching to VaultManager methods. Import shared `mcp` instance and `vault_manager` from `server.py` module.

**Tool 1: `vault_query`** — Discovery operations (read-only)

```python
@mcp.tool()
async def vault_query(
    operation: str,
    query: str = "",
    folder: str = "",
    tags: str = "",
    date_range_days: int = 0,
    limit: int = 10,
    recursive: bool = False,
) -> str:
    """Search and discover notes in the Obsidian vault.

    Args:
        operation: One of: list_structure, search_content, search_by_metadata, recent_changes.
        query: Search query text (for search_content).
        folder: Folder path to scope (for list_structure, search_by_metadata).
        tags: Comma-separated tag filter (for search_by_metadata).
        date_range_days: Only notes modified within N days (for search_by_metadata).
        limit: Max results to return (default 10).
        recursive: Include subfolders (for list_structure).
    """
```

Operations dispatch:
- `list_structure` → `vault_manager.list_notes(folder or None, recursive)`
- `search_content` → `vault_manager.search_content(query, limit)`
- `search_by_metadata` → `vault_manager.search_by_metadata(tag_list, folder or None, date_range_days or None)`
- `recent_changes` → `vault_manager.get_recent_notes(limit)`

**Tool 2: `vault_read`** — Read full note content

```python
@mcp.tool()
async def vault_read(
    operation: str,
    path: str = "",
    paths: str = "",
    date: str = "",
) -> str:
    """Read full content of notes from the Obsidian vault.

    Args:
        operation: One of: read_note, read_multiple, daily_note.
        path: Vault-relative path to a note (for read_note).
        paths: Comma-separated vault-relative paths (for read_multiple).
        date: Date string YYYY-MM-DD (for daily_note, defaults to today).
    """
```

Operations dispatch:
- `read_note` → `vault_manager.read_note(path)`
- `read_multiple` → `vault_manager.read_multiple(paths.split(","))`
- `daily_note` → `vault_manager.daily_note(date or None)`

**Tool 3: `vault_manage`** — Write operations

```python
@mcp.tool()
async def vault_manage(
    operation: str,
    path: str = "",
    content: str = "",
    tags: str = "",
    metadata: str = "",
    source: str = "",
    destination: str = "",
    old_text: str = "",
    new_text: str = "",
    confirm_destructive: bool = False,
) -> str:
    """Create, edit, and organize notes in the Obsidian vault.

    IMPORTANT: Delete operations require confirm_destructive=true.

    Args:
        operation: One of: create_note, append_note, edit_note, move_note, delete_note, create_folder.
        path: Target note/folder path (for create, append, edit, delete, create_folder).
        content: Note content in markdown (for create_note, append_note).
        tags: Comma-separated tags (for create_note).
        metadata: JSON string of additional frontmatter key-value pairs (for create_note).
        source: Source path (for move_note).
        destination: Destination path (for move_note).
        old_text: Text to find (for edit_note).
        new_text: Replacement text (for edit_note).
        confirm_destructive: Must be true for delete operations.
    """
```

Operations dispatch:
- `create_note` → `vault_manager.write_note(path, content, tag_list, metadata_dict)`
- `append_note` → `vault_manager.append_to_note(path, content)`
- `edit_note` → `vault_manager.edit_note(path, old_text, new_text)`
- `move_note` → `vault_manager.move_note(source, destination)`
- `delete_note` → `vault_manager.delete_note(path, confirm_destructive)`
- `create_folder` → `vault_manager.create_folder(path)`

**GOTCHA**: `tags` parameter is a comma-separated string, not a list — MCP tools work best with primitive types. Parse: `[t.strip() for t in tags.split(",") if t.strip()]`.
**GOTCHA**: `paths` for read_multiple is also comma-separated. Same parsing.
**GOTCHA**: `metadata` for create_note is a JSON string. Parse with `json.loads()`, catch `json.JSONDecodeError`.
**GOTCHA**: Every operation must validate required params and return clear error if missing (e.g., "search_content requires 'query' parameter").
**GOTCHA**: Return `json.dumps(note.model_dump(), default=str)` for NoteContent/NoteSummary results. The `default=str` handles datetime serialization.

**IMPORTS**: `json`, `logging`

**VALIDATE**: `cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/tools/vault.py`

---

### Task 6: CREATE `mcp-server/src/tools/knowledge.py`

Replace the docstring stub with 1 MCP tool for conversation persistence.

```python
@mcp.tool()
async def save_conversation_summary(
    summary: str,
    topics: str,
    extracted_tasks: str = "",
    task_ids_created: str = "",
) -> str:
    """Save a conversation summary to Elasticsearch for future recall.

    Call this after productive conversations to preserve context for future sessions.

    Args:
        summary: A concise summary of the conversation and key decisions.
        topics: Comma-separated topic keywords (e.g. "api-refactoring, task-planning").
        extracted_tasks: Comma-separated task descriptions that were identified.
        task_ids_created: Comma-separated Artemis task IDs that were created.
    """
```

**GOTCHA**: If `knowledge_store` is None (ES not configured), return an error message instead of crashing.
**GOTCHA**: Parse comma-separated strings to lists, same pattern as vault tools.

**IMPORTS**: `json`, `logging`

**VALIDATE**: `cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/tools/knowledge.py`

---

### Task 7: CREATE `mcp-server/src/tools/research.py`

Replace the docstring stub with 2 MCP tools for web research.

**Tool 1: `web_search`**

```python
@mcp.tool()
async def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for information on a topic.

    Args:
        query: Search query.
        max_results: Number of results to return (default 5).
    """
```

Implementation:
- If `tavily_api_key` is set: `POST https://api.tavily.com/search` with `{api_key, query, max_results}`
- Elif `brave_api_key` is set: `GET https://api.search.brave.com/res/v1/web/search?q={query}&count={max_results}` with `X-Subscription-Token` header
- Else: return error "No search API key configured. Set TAVILY_API_KEY or BRAVE_API_KEY."

**Tool 2: `fetch_url`**

```python
@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch a web page and extract its text content.

    Args:
        url: The URL to fetch.
    """
```

Implementation:
- `httpx.AsyncClient().get(url, follow_redirects=True, timeout=30.0)`
- Convert HTML to markdown: `html2text.html2text(response.text)`
- Truncate to 5000 chars if longer (prevent context overload)
- Return the extracted text

**GOTCHA**: Use a fresh `httpx.AsyncClient()` for external requests (not the Artemis client).
**GOTCHA**: `html2text` is synchronous — that's fine, it's CPU-only and fast.
**GOTCHA**: Set a `User-Agent` header for URL fetching to avoid 403s: `"Athena/0.1 (research assistant)"`.
**GOTCHA**: Handle non-HTML responses (PDF, etc.) gracefully — return first 2000 chars of raw text.

**IMPORTS**: `json`, `httpx`, `html2text`, `logging`

**VALIDATE**: `cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/tools/research.py`

---

### Task 8: CREATE `mcp-server/src/server.py`

Replace the docstring stub with the FastMCP server that wires everything together.

**Architecture**: Module-level singletons for adapter classes + FastMCP instance. Tool modules import both `mcp` and the adapters they need. Server entry point initializes everything and runs SSE.

```python
"""MCP server setup with SSE transport.

This is the main entry point for the Athena MCP server.
Initializes adapter classes and registers all tools via FastMCP.
"""

import logging

from mcp.server.fastmcp import FastMCP

from src.config import get_settings

# Initialize settings and logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("elastic_transport").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Athena")

# Initialize adapter classes
from src.vault_manager import VaultManager
from src.artemis_client import ArtemisClient

vault_manager = VaultManager(settings.vault_path)
artemis_client = ArtemisClient(settings.artemis_base_url)

# ES knowledge store (optional — may not have credentials)
knowledge_store = None
if settings.elastic_url and settings.elastic_api_key:
    from src.es_client import KnowledgeStore
    knowledge_store = KnowledgeStore(
        settings.elastic_url, settings.elastic_api_key, settings.conversations_index
    )

# Register all tools (imports trigger @mcp.tool() decorators)
import src.tools.artemis   # noqa: F401
import src.tools.vault     # noqa: F401
import src.tools.knowledge # noqa: F401
import src.tools.research  # noqa: F401

if __name__ == "__main__":
    logger.info("Starting Athena MCP server on port %d", settings.mcp_server_port)
    mcp.run(transport="sse", host="0.0.0.0", port=settings.mcp_server_port)
```

**How tool modules access adapters**: Each tool module imports from `src.server`:
```python
# In tools/vault.py:
from src.server import mcp, vault_manager
```

**GOTCHA**: Circular import risk. `server.py` imports `src.tools.vault`, which imports `from src.server import mcp, vault_manager`. This works because by the time `src.tools.vault` is imported, `mcp` and `vault_manager` are already defined as module-level variables in `server.py`. The tool module imports happen after adapter initialization.

**GOTCHA**: `mcp.run()` blocks — it starts uvicorn internally. Do NOT call from async context. The `if __name__ == "__main__"` guard is essential.

**GOTCHA**: Store research config on module level so tools can access:
```python
# Research config (for tools/research.py)
tavily_api_key = settings.tavily_api_key
brave_api_key = settings.brave_api_key
```

**VALIDATE**: `cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/server.py`

---

### Task 9: UPDATE `mcp-server/src/tools/__init__.py`

Replace the comment stub. Keep it minimal — just document the module:

```python
"""MCP tool definitions for the Athena server.

Each module registers tools on the shared FastMCP instance via @mcp.tool() decorators.
Tools are imported by server.py at startup to trigger registration.
"""
```

**VALIDATE**: `cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/tools/__init__.py`

---

### Task 10: Install dependencies and verify imports

```bash
cd /home/stardust/Athena/mcp-server && uv sync
```

Then verify all imports resolve:
```bash
cd /home/stardust/Athena && uv run --project mcp-server python -c "
from src.config import get_settings
from src.vault_manager import VaultManager, NoteContent, NoteSummary
from src.artemis_client import ArtemisClient
from src.es_client import KnowledgeStore
print('All imports OK')
"
```

---

### Task 11: Lint all files

```bash
cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/
cd /home/stardust/Athena && uv run --project mcp-server ruff format --check mcp-server/src/
```

Fix any issues before proceeding.

---

### Task 12: Smoke test — VaultManager against sample vault

```bash
cd /home/stardust/Athena && uv run --project mcp-server python -c "
from src.vault_manager import VaultManager
vm = VaultManager('/home/stardust/Athena/sample-vault')

# List structure
notes = vm.list_notes(recursive=True)
print(f'Total notes: {len(notes)}')

# Read a note
note = vm.read_note('Projects/API Refactoring.md')
print(f'Title: {note.title}, Words: {note.word_count}, Tags: {note.tags}')

# Search content
results = vm.search_content('authentication', limit=3)
for r in results:
    print(f'  Found: {r.path} ({r.title})')

# Recent notes
recent = vm.get_recent_notes(limit=3)
for r in recent:
    print(f'  Recent: {r.path}')

print('VaultManager smoke test passed')
"
```

---

### Task 13: Smoke test — MCP server starts

```bash
cd /home/stardust/Athena && timeout 5 uv run --project mcp-server python -m src.server 2>&1 || true
```

Expected: Server starts, prints "Starting Athena MCP server on port 8001", then times out after 5 seconds (that's fine — it means it started). If it crashes immediately, fix the error.

---

## TESTING STRATEGY

### Unit Tests (deferred — hackathon velocity)

Key testable components if time allows:

**VaultManager:**
- `_validate_path()` — path within vault returns Path, path outside raises ValueError
- `read_note()` — returns NoteContent with correct fields
- `write_note()` — creates file with frontmatter, raises if exists
- `search_content()` — returns scored results
- `edit_note()` — replaces text, errors on 0 or >1 matches

**ArtemisClient:**
- Mock httpx responses, verify correct URL/body construction
- Verify error handling for 404, 409, connection errors

### Integration Tests (manual — requires running services)

- Start MCP server, connect with MCP Inspector
- Call each tool, verify responses
- Test vault tools against sample vault
- Test Artemis tools against running Artemis backend

---

## VALIDATION COMMANDS

### Level 1: Syntax & Style

```bash
cd /home/stardust/Athena && uv run --project mcp-server ruff check mcp-server/src/
cd /home/stardust/Athena && uv run --project mcp-server ruff format --check mcp-server/src/
```

### Level 2: Import Verification

```bash
cd /home/stardust/Athena && uv run --project mcp-server python -c "
from src.vault_manager import VaultManager
from src.artemis_client import ArtemisClient
from src.es_client import KnowledgeStore
print('All adapter imports OK')
"
```

### Level 3: VaultManager Smoke Test

```bash
cd /home/stardust/Athena && uv run --project mcp-server python -c "
from src.vault_manager import VaultManager
vm = VaultManager('/home/stardust/Athena/sample-vault')
notes = vm.list_notes(recursive=True)
assert len(notes) == 17, f'Expected 17, got {len(notes)}'
note = vm.read_note('Projects/API Refactoring.md')
assert 'API' in note.title
print(f'VaultManager OK: {len(notes)} notes, read \"{note.title}\"')
"
```

### Level 4: Server Startup Test

```bash
cd /home/stardust/Athena && timeout 5 uv run --project mcp-server python -m src.server 2>&1 || true
```

Expected: Starts without crash, prints startup message, times out after 5s.

### Level 5: Docker Build

```bash
cd /home/stardust/Athena/mcp-server && docker build -t athena-mcp .
```

---

## ACCEPTANCE CRITERIA

- [ ] `vault_manager.py` — VaultManager class with path validation, frontmatter CRUD, search, security
- [ ] `artemis_client.py` — ArtemisClient with 7 async methods + health_check + close
- [ ] `es_client.py` — KnowledgeStore with save_conversation + close
- [ ] `tools/vault.py` — 3 MCP tools (vault_query, vault_read, vault_manage) with operation dispatch
- [ ] `tools/artemis.py` — 7 MCP tools proxying to ArtemisClient
- [ ] `tools/knowledge.py` — 1 MCP tool for conversation persistence
- [ ] `tools/research.py` — 2 MCP tools (web_search, fetch_url) with Tavily/Brave support
- [ ] `server.py` — FastMCP with SSE transport, initializes all adapters, imports all tools
- [ ] All files pass `ruff check` and `ruff format --check`
- [ ] All imports resolve without errors
- [ ] VaultManager reads 17 notes from sample vault
- [ ] Server starts on port 8001 without crashing
- [ ] Docker image builds successfully
- [ ] No secrets or credentials in committed code
- [ ] Path validation blocks directory traversal (`../` attacks)
- [ ] Delete operations require `confirm_destructive=True`
- [ ] All tools return JSON strings, never crash

---

## COMPLETION CHECKLIST

- [ ] All 9 tasks completed in order
- [ ] Each task validation passed immediately
- [ ] All validation commands executed successfully (Level 1-5)
- [ ] VaultManager smoke test passes (17 notes, read, search)
- [ ] Server starts and listens on port 8001
- [ ] No linting errors
- [ ] Acceptance criteria all met

---

## NOTES

- **Circular imports**: `server.py` defines `mcp`, `vault_manager`, `artemis_client`, `knowledge_store` at module level. Tool modules import these. The tool module imports happen AFTER the adapters are initialized, so this is safe. If it becomes a problem, extract the `mcp` instance to a separate `app.py` module.
- **No tests in this phase**: Hackathon velocity. Manual validation via smoke tests and MCP Inspector. Tests can be added later.
- **VaultManager is synchronous**: All filesystem operations are synchronous (blocking). This is fine for a single-user hackathon demo. The MCP tool functions are `async` but the underlying VaultManager calls are sync. For production, wrap in `asyncio.to_thread()`.
- **ES knowledge store is optional**: If `ELASTIC_URL` or `ELASTIC_API_KEY` are empty, `knowledge_store` is `None`. The knowledge tool returns an error message. This allows the MCP server to run without ES for vault + Artemis testing.
- **Research tools are P2**: If time is tight, skip `tools/research.py` — it's not in the core demo flow. The server will still work with the other 11 tools.
- **`html2text` truncation**: Fetched URLs are truncated to 5000 chars. This prevents a single URL fetch from consuming the entire LLM context window.
- **Brave vs Tavily**: Both are free tier. Tavily preferred (simpler API, purpose-built for AI agents). Brave as fallback if Tavily quota is exhausted.
- **MCP tool parameter types**: Use `str` with empty string defaults for optional parameters instead of `str | None`. LLMs handle empty strings more reliably than null values in tool calls. Parse empty strings to None inside the tool function.
