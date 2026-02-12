# Feature: Indexer Core — Obsidian Vault → Elasticsearch Sync

The following plan should be complete, but its important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Build the indexer CLI tool that parses Obsidian vault `.md` files (with YAML frontmatter), computes checksums for deduplication, and bulk indexes them into Elasticsearch. The CLI provides three commands: `setup-indices` (create ES indices), `index` (bulk index vault), and `watch` (live filesystem sync).

## User Story

As a knowledge worker using Athena,
I want my Obsidian vault notes indexed in Elasticsearch with semantic search,
So that the Athena agent can search my notes by meaning, not just keywords.

## Problem Statement

The Elasticsearch indices (`athena-notes`, `athena-conversations`) are created and mapped, but there's no code to parse vault notes and push them into ES. Without the indexer, the agent has no knowledge base to search.

## Solution Statement

Implement 4 files: `parser.py` (parse markdown + frontmatter → Pydantic model), `indexer.py` (bulk index to ES with checksum dedup), `cli.py` (argparse CLI with rich output), `watcher.py` (watchdog live sync). Each builds on the previous.

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**: `indexer/src/` (4 files)
**Dependencies**: elasticsearch[async], python-frontmatter, watchdog, pydantic, rich (all in pyproject.toml)

---

## CONTEXT REFERENCES

### Relevant Codebase Files — MUST READ BEFORE IMPLEMENTING

- `indexer/src/config.py` — Complete. `IndexerSettings` class with fields: `elastic_url`, `elastic_api_key`, `notes_index`, `conversations_index`, `vault_path`, `log_level`. Use `get_settings()` factory.
- `indexer/src/mappings.py` — Complete. `NOTES_INDEX_MAPPING` and `CONVERSATIONS_INDEX_MAPPING` dicts with full ES mapping definitions. The `content_semantic` field uses `semantic_text` type with `inference_id: ".elser-2-elastic"`.
- `indexer/pyproject.toml` — CLI entry point: `athena-index = "src.cli:main"`. Dependencies list. ruff config (py312, line-length 100, S324 bandit rule active).
- `.env` — `ELASTIC_URL` is the Elasticsearch Serverless endpoint URL (renamed from `ELASTIC_CLOUD_ID` in Task 0).
- `reference/obsidian-ai-agent/app/shared/vault/vault_manager.py` (lines 55-131) — Frontmatter parsing pattern: `frontmatter.load()`, tags as str or list, date parsing with `fromisoformat`, title fallback to filename stem.
- `reference/obsidian-ai-agent/app/shared/vault/vault_models.py` — `Frontmatter`, `Note`, `VaultPath` Pydantic models. Path validation with `startswith()` check.

### New Files to Create

- `indexer/src/parser.py` — `ParsedNote` model + `parse_note()` + `parse_vault()` functions
- `indexer/src/indexer.py` — `VaultIndexer` class + `IndexResult` dataclass
- `indexer/src/cli.py` — `main()` entry point with argparse subcommands + rich output
- `indexer/src/watcher.py` — `VaultEventHandler` + `start_watcher()` function

### Relevant Documentation

- [python-frontmatter docs](https://python-frontmatter.readthedocs.io/) — `frontmatter.load(f)` returns Post with `.metadata` dict and `.content` str
- [elasticsearch-py async bulk](https://elasticsearch-py.readthedocs.io/en/stable/helpers.html#bulk-helpers) — `async_bulk(es, actions, raise_on_error=False)` returns `(success, errors)`
- [watchdog docs](https://python-watchdog.readthedocs.io/) — `Observer` + `FileSystemEventHandler` subclass

### Patterns to Follow

**Frontmatter parsing** (from reference vault_manager.py):
```python
import frontmatter
with file_path.open("r", encoding="utf-8") as f:
    post = frontmatter.load(f)
# post.metadata = dict of YAML fields, post.content = markdown body
```

**Tag handling** (handle both str and list):
```python
tags_raw = metadata.get("tags", [])
if isinstance(tags_raw, str):
    tags = [tags_raw]
elif isinstance(tags_raw, list):
    tags = [str(t) for t in tags_raw]
else:
    tags = []
```

**Path validation** (directory traversal prevention):
```python
file_path = file_path.resolve()
vault_root = vault_root.resolve()
if not str(file_path).startswith(str(vault_root)):
    raise ValueError(f"Path {file_path} is outside vault root {vault_root}")
```

**ES client creation** (direct URL):
```python
es = AsyncElasticsearch(hosts=[settings.elastic_url], api_key=settings.elastic_api_key)
```

---

## IMPLEMENTATION PLAN

### Phase 1: Parser (`parser.py`)

Zero dependencies on other new files. Foundation for everything else.

- `ParsedNote` Pydantic model matching the `athena-notes` ES mapping fields
- `compute_checksum()` — MD5 of file bytes
- `parse_note()` — parse single .md file → ParsedNote
- `parse_vault()` — iterate all .md files, return list of results with error handling

### Phase 2: Indexer (`indexer.py`)

Depends on parser.py + config.py + mappings.py.

- `IndexResult` dataclass for tracking counts/errors
- `VaultIndexer` class with ES client creation, index lifecycle, checksum dedup, bulk indexing
- `index_single_note()` and `delete_note()` methods for watcher support

### Phase 3: CLI (`cli.py`)

Depends on indexer.py. The user-facing interface.

- argparse with 3 subcommands: `setup-indices`, `index`, `watch`
- rich Console/Panel/Table for formatted output
- asyncio.run() at CLI boundary

### Phase 4: Watcher (`watcher.py`)

Depends on indexer.py. Lowest priority (PRD Phase 3), but implement now since it's straightforward.

- watchdog `FileSystemEventHandler` subclass
- Bridge watchdog sync callbacks → async ES operations via `asyncio.run_coroutine_threadsafe()`

---

## STEP-BY-STEP TASKS

### Task 0: RENAME `ELASTIC_CLOUD_ID` → `ELASTIC_URL` (prerequisite)

Rename the misleading env var across 4 files. Elasticsearch Serverless uses a direct URL, not a cloud_id.

**UPDATE `.env`:**
- `ELASTIC_CLOUD_ID=...` → `ELASTIC_URL=...`

**UPDATE `.env.example`:**
- `ELASTIC_CLOUD_ID=your-deployment-cloud-id` → `ELASTIC_URL=https://your-elasticsearch-endpoint:443`
- Update the comment from `Elasticsearch (Serverless)` section

**UPDATE `indexer/src/config.py`:**
- `elastic_cloud_id: str` → `elastic_url: str`

**UPDATE `mcp-server/src/config.py`:**
- `elastic_cloud_id: str = ""` → `elastic_url: str = ""`

**VALIDATE**: `grep -r "elastic_cloud_id\|ELASTIC_CLOUD_ID" indexer/ mcp-server/ .env .env.example` should return zero results.

### Task 1: CREATE `indexer/src/parser.py`

**ParsedNote model:**
- Fields: `title` (str), `content` (str), `content_semantic` (str), `tags` (list[str]), `note_type` (str, default "note"), `path` (str), `vault_relative_path` (str), `word_count` (int), `created_at` (datetime | None), `updated_at` (datetime | None), `indexed_at` (datetime), `checksum` (str)
- Method `to_es_document() -> dict` — model_dump() with datetime → ISO string conversion, drop None dates
- Method `es_doc_id() -> str` — SHA-256 of `vault_relative_path` (deterministic doc ID for upsert)

**NOTE_TYPE_FOLDER_MAP constant:**
```python
NOTE_TYPE_FOLDER_MAP: dict[str, str] = {
    "projects": "project",
    "ideas": "idea",
    "meeting notes": "meeting",
    "daily notes": "daily",
    "research": "research",
}
```

**Helper functions:**
- `compute_checksum(file_path: Path) -> str` — `hashlib.md5(file_path.read_bytes()).hexdigest()` with `# noqa: S324`
- `_infer_note_type(vault_relative_path: str) -> str` — first folder component → NOTE_TYPE_FOLDER_MAP lookup
- `_parse_datetime(value: object) -> datetime | None` — handle str (fromisoformat), datetime, or None

**Main functions:**
- `parse_note(file_path: Path, vault_root: Path) -> ParsedNote` — validate path within vault, parse frontmatter, extract all fields, fallback to filesystem metadata for dates/title
- `parse_vault(vault_root: Path) -> list[tuple[ParsedNote | None, str | None]]` — rglob("*.md"), skip hidden dirs, collect (note, error) pairs

**PATTERN**: Follow frontmatter parsing from `reference/obsidian-ai-agent/app/shared/vault/vault_manager.py:55-131`
**GOTCHA**: ruff S324 on `hashlib.md5()` — use `# noqa: S324`
**GOTCHA**: frontmatter tags can be str or list — handle both
**GOTCHA**: frontmatter dates can be str, datetime, or date objects — handle all
**GOTCHA**: `content_semantic` = same as `content` (ELSER embeds at index time, no client-side embedding)
**VALIDATE**: `cd /home/stardust/Athena && uv run --project indexer ruff check indexer/src/parser.py`

### Task 2: CREATE `indexer/src/indexer.py`

**IndexResult dataclass:**
- Fields: `total_files` (int), `indexed` (int), `skipped` (int), `errors` (list[str])
- Property: `failed -> int` = `len(self.errors)`

**VaultIndexer class:**
- `__init__(self, settings: IndexerSettings)` — store settings, create ES client, resolve vault_root
- `_create_es_client() -> AsyncElasticsearch` — `AsyncElasticsearch(hosts=[settings.elastic_url], api_key=settings.elastic_api_key)`
- `async close()` — `await self.es.close()`
- `async setup_indices() -> dict[str, bool]` — create indices from mappings if not existing
- `async _fetch_existing_checksums() -> dict[str, str]` — scroll API to get all (vault_relative_path, checksum) pairs
- `async index_vault() -> IndexResult` — parse_vault → fetch checksums → skip unchanged → async_bulk → return result
- `async index_single_note(file_path: Path) -> bool` — parse + index single note (for watcher)
- `async delete_note(file_path: Path) -> bool` — delete by doc ID computed from relative path

**IMPORTS**: `from elasticsearch import AsyncElasticsearch`, `from elasticsearch.helpers import async_bulk`
**PATTERN**: Scroll API for fetching checksums (handles >1000 docs)
**GOTCHA**: `async_bulk` with `raise_on_error=False` returns `(success_count, error_list)`. Error items are dicts — stringify them.
**VALIDATE**: `cd /home/stardust/Athena && uv run --project indexer ruff check indexer/src/indexer.py`

### Task 3: CREATE `indexer/src/cli.py`

Replace the existing stub with full implementation.

**Structure:**
- `_configure_logging(level: str) -> None` — basicConfig + suppress elastic_transport logs
- `async cmd_setup_indices(settings: IndexerSettings) -> None` — create indices, print rich Table
- `async cmd_index(settings: IndexerSettings) -> None` — validate vault path, run index_vault, print rich Panel + Table + errors
- `async cmd_watch(settings: IndexerSettings) -> None` — import and start watcher, handle KeyboardInterrupt
- `main() -> None` — argparse with subparsers (`setup-indices`, `index`, `watch`), load settings, configure logging, dispatch with `asyncio.run()`

**IMPORTS**: `argparse`, `asyncio`, `logging`, `sys`, `pathlib.Path`, `rich.console.Console`, `rich.panel.Panel`, `rich.table.Table`
**PATTERN**: `asyncio.run()` at CLI boundary, async functions internally
**GOTCHA**: `required=True` on subparsers so `athena-index` without a command shows help
**VALIDATE**: `cd /home/stardust/Athena && uv run --project indexer ruff check indexer/src/cli.py && uv run --project indexer athena-index --help`

### Task 4: CREATE `indexer/src/watcher.py`

**VaultEventHandler(FileSystemEventHandler):**
- `__init__(self, loop, indexer)` — store asyncio loop and VaultIndexer
- `_is_markdown(path: str) -> bool` — check `.md` suffix, skip hidden files
- `on_created`, `on_modified` — `asyncio.run_coroutine_threadsafe(indexer.index_single_note(...))`
- `on_deleted` — `asyncio.run_coroutine_threadsafe(indexer.delete_note(...))`
- `on_moved` — delete old path + index new path

**`async start_watcher(indexer, vault_path) -> None`:**
- Get running event loop
- Create Observer + schedule handler recursively
- `await asyncio.sleep(1)` loop until KeyboardInterrupt/CancelledError
- Stop observer on exit

**IMPORTS**: `watchdog.events.FileSystemEventHandler`, `watchdog.observers.Observer`, `asyncio`, `pathlib.Path`
**PATTERN**: Bridge sync watchdog thread → async ES via `asyncio.run_coroutine_threadsafe()`
**VALIDATE**: `cd /home/stardust/Athena && uv run --project indexer ruff check indexer/src/watcher.py`

### Task 5: Validate full CLI end-to-end

- Run `uv run --project indexer ruff check indexer/src/` (all files lint clean)
- Run `uv run --project indexer athena-index --help` (shows 3 subcommands)
- Run `uv run --project indexer athena-index setup-indices` (creates indices or reports existing)
- Run `VAULT_PATH=./sample-vault uv run --project indexer athena-index index` (indexes 0 files from empty vault — no errors)

---

## TESTING STRATEGY

### Unit Tests (deferred — hackathon velocity)

The parser is the most testable component. Key tests:
- `parse_note()` with full frontmatter → all fields populated
- `parse_note()` with no frontmatter → title from filename, dates from stat
- `parse_note()` with tags as string vs list
- `_infer_note_type()` for each folder name
- `compute_checksum()` determinism
- Path traversal attempt → ValueError
- `ParsedNote.to_es_document()` produces valid dict
- `ParsedNote.es_doc_id()` deterministic

### Integration Tests (manual — requires ES connection)

- `setup_indices` creates both indices
- `index_vault` on sample vault indexes correct count
- Re-run `index_vault` → all files skipped (checksum match)
- Modify a file → re-run → only that file re-indexed

---

## VALIDATION COMMANDS

### Level 1: Syntax & Style

```bash
cd /home/stardust/Athena && uv run --project indexer ruff check indexer/src/
cd /home/stardust/Athena && uv run --project indexer ruff format --check indexer/src/
```

### Level 2: CLI Smoke Test

```bash
cd /home/stardust/Athena && uv run --project indexer athena-index --help
```

### Level 3: Integration (requires .env with valid ES credentials)

```bash
cd /home/stardust/Athena && uv run --project indexer athena-index setup-indices
cd /home/stardust/Athena && VAULT_PATH=./sample-vault uv run --project indexer athena-index index
```

---

## ACCEPTANCE CRITERIA

- [ ] `parser.py` — `ParsedNote` model with all ES mapping fields, `parse_note()` and `parse_vault()` functions
- [ ] `indexer.py` — `VaultIndexer` class with setup_indices, index_vault, index_single_note, delete_note
- [ ] `cli.py` — `main()` with setup-indices, index, watch subcommands and rich output
- [ ] `watcher.py` — `VaultEventHandler` + `start_watcher()` with watchdog
- [ ] All 4 files pass `ruff check` and `ruff format --check`
- [ ] `athena-index --help` shows all 3 subcommands
- [ ] `athena-index setup-indices` succeeds against Elastic Cloud
- [ ] `athena-index index` on empty sample-vault completes without errors
- [ ] `ELASTIC_CLOUD_ID` renamed to `ELASTIC_URL` in .env, .env.example, indexer config, mcp-server config
- [ ] Checksum dedup skips unchanged files on re-index

---

## NOTES

- **ELASTIC_URL rename**: Task 0 renames `ELASTIC_CLOUD_ID` → `ELASTIC_URL` across `.env`, `.env.example`, `indexer/src/config.py`, and `mcp-server/src/config.py`. The ES client simply uses `hosts=[settings.elastic_url]`.
- **No chunking needed**: Unlike hierarchical-rag, Athena uses ES `semantic_text` field type which handles chunking automatically at index time. We just send the full content.
- **content_semantic = content**: Same string. ELSER inference endpoint (`.elser-2-elastic`) processes it at index time.
- **Sample vault is empty**: The `sample-vault/` folders contain only `.gitkeep` files. The indexer must handle zero notes gracefully. Sample notes will be created as a separate task.
- **Watcher is Phase 3 per PRD**: Implement it now since it's small, but it's not blocking demo functionality.
- **MD5 for checksum, SHA-256 for doc ID**: Two different hashes for two different purposes. MD5 for content fingerprinting (dedup), SHA-256 for document identity (ES _id).
