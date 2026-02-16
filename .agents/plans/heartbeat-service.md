# Feature: Heartbeat Service — Proactive Agent Check-ins

The following plan should be complete, but validate documentation and codebase patterns before implementing.

Pay special attention to naming of existing utils, types, and models. Import from the right files etc.

## Feature Description

A scheduled background service that periodically wakes the Athena agent to evaluate a user-defined checklist (`Meta/heartbeat.md` in the vault). The agent checks for overdue tasks, missing daily plans, approaching deadlines, and other proactive concerns. If nothing needs attention, the response is silently suppressed (`HEARTBEAT_OK`). If there's a real alert, it's logged and appended to the user's daily note.

This transforms Athena from a purely reactive assistant into a proactive partner that nudges the user about things they might have forgotten.

## User Story

As a knowledge worker,
I want Athena to proactively check on my tasks and deadlines at regular intervals,
So that I never miss an important deadline or forget to plan my day.

## Problem Statement

Athena currently only responds when the user initiates conversation. Buried deadlines, forgotten daily plans, and overdue Q1 tasks go unnoticed until the user remembers to ask. The agent has all the tools to detect these situations but no mechanism to act proactively.

## Solution Statement

A lightweight Python service using APScheduler v3 (stable) runs on a cron-like schedule (every 30 minutes during active hours). Each tick:
1. Reads `Meta/heartbeat.md` from the vault (the user-editable checklist)
2. Injects user profile + agent memory (same pattern as voice proxy)
3. Calls the Kibana converse API with a heartbeat prompt
4. Parses the agent's response — suppresses `HEARTBEAT_OK`, delivers real alerts
5. Appends alerts to the daily note for visibility in Obsidian

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**: New `heartbeat/` sub-project, `docker-compose.yml`, `sample-vault/Meta/`
**Dependencies**: APScheduler 3.x, httpx, pydantic-settings (all already used in project)

---

## CONTEXT REFERENCES

### Relevant Codebase Files — READ THESE BEFORE IMPLEMENTING

- `voice-client/serve.py` (lines 39-98) — **Primary pattern**: `VoiceSettings` config class, `_strip_frontmatter()`, `_read_memory_context()` for vault memory injection. The heartbeat service reuses this exact pattern for reading Meta files and building the `systemPromptAddition` payload.
- `voice-client/serve.py` (lines 125-169) — **Converse API call pattern**: How to POST to `{kibana_url}/api/agent_builder/converse` with `input`, `agent_id`, `conversation_id`, and `configuration_overrides.systemPromptAddition`. The heartbeat service mirrors this HTTP call.
- `mcp-server/src/tools/knowledge.py` (lines 20-57) — **Daily note append pattern**: `_append_to_daily_note()` shows how to append a block to today's daily note, creating it if missing. The heartbeat service uses the same approach for delivering alerts.
- `mcp-server/src/config.py` (lines 1-42) — **Config pattern**: `pydantic-settings` with `env_file: (".env", "../.env")`, `extra: "ignore"`. All sub-projects follow this.
- `.env.example` — All env vars documented. Heartbeat adds 3 new ones.
- `docker-compose.yml` — Docker Compose service definitions. Heartbeat service follows the same structure as `voice-proxy`.
- `sample-vault/Meta/user-profile.md` — User profile injected into heartbeat context.
- `sample-vault/Meta/memory.md` — Agent memory injected into heartbeat context.
- `decisions/003-openclaw-patterns-research.md` (lines 102-193) — Full heartbeat research: OpenClaw's 30-min cron pattern, HEARTBEAT_OK suppression, active hours, cost considerations, implementation options.
- `.claude/skills/elastic-agent-builder/references/api-reference.md` (lines 263-296) — Converse API spec: request/response schema, `configuration_overrides.systemPromptAddition`, response path `response.response.message`.

### New Files to Create

- `heartbeat/pyproject.toml` — Sub-project definition with dependencies
- `heartbeat/src/__init__.py` — Package marker
- `heartbeat/src/config.py` — HeartbeatSettings (pydantic-settings)
- `heartbeat/src/heartbeat.py` — Core logic: scheduler, tick function, alert delivery
- `heartbeat/src/__main__.py` — Entry point (`python -m src`)
- `heartbeat/Dockerfile` — Container image (mirrors mcp-server Dockerfile pattern)
- `sample-vault/Meta/heartbeat.md` — Demo checklist for the heartbeat agent

### Files to Modify

- `docker-compose.yml` — Add `heartbeat` service
- `.env.example` — Add 3 new env vars (HEARTBEAT_INTERVAL_MINUTES, HEARTBEAT_ACTIVE_HOUR_START, HEARTBEAT_ACTIVE_HOUR_END)

### Relevant Documentation

- [APScheduler v3 AsyncIOScheduler Docs](https://apscheduler.readthedocs.io/en/3.x/modules/schedulers/asyncio.html)
  - Scheduler lifecycle, signal handling
  - Why: Core scheduling mechanism
- [APScheduler v3 CronTrigger Docs](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html)
  - `hour="8-21"` range expression for active hours
  - Why: Active-hours-only scheduling without a runtime guard
- [Elastic Agent Builder Converse API](https://www.elastic.co/docs/api/doc/serverless/operation/operation-post-agent-builder-converse)
  - Request/response schema, configuration_overrides
  - Why: The HTTP call the heartbeat makes every tick

### Patterns to Follow

**Config Pattern** (from `mcp-server/src/config.py`):
```python
from pydantic_settings import BaseSettings

class HeartbeatSettings(BaseSettings):
    setting_name: str = "default"

    model_config = {
        "env_file": (".env", "../.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }
```

**Memory Injection Pattern** (from `voice-client/serve.py:75-98`):
```python
def _read_memory_context() -> str:
    vault = Path(settings.vault_path)
    sections: list[str] = []
    for filename, header in [
        ("Meta/user-profile.md", "## User Profile"),
        ("Meta/memory.md", "## Agent Memory"),
    ]:
        filepath = vault / filename
        try:
            raw = filepath.read_text(encoding="utf-8")
            content = _strip_frontmatter(raw)[:MAX_MEMORY_CHARS]
            sections.append(f"{header}\n\n{content}")
        except FileNotFoundError:
            pass
    return "\n\n".join(sections)
```

**Converse API Call Pattern** (from `voice-client/serve.py:125-169`):
```python
payload = {
    "input": input_text,
    "agent_id": settings.agent_id,
    "conversation_id": conversation_id,  # optional
    "configuration_overrides": {
        "systemPromptAddition": memory_context,
    },
}
resp = await kibana_client.post(
    f"{settings.kibana_url}/api/agent_builder/converse",
    json=payload,
)
data = resp.json()
message = data["response"]["message"]  # NOT data["response"]
```

**Daily Note Append Pattern** (from `mcp-server/src/tools/knowledge.py:20-57`):
- Builds a `## Section Header (HH:MM UTC)` block
- Tries `append_to_note()` first, catches `FileNotFoundError`, creates note if missing
- Non-fatal: failures logged but don't crash

**Logging Pattern**: `logging.getLogger(__name__)`, format: `"%(asctime)s %(levelname)-8s %(name)s — %(message)s"`

**Dockerfile Pattern** (from `mcp-server/Dockerfile`): Multi-stage with uv builder.

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation — Config, Vault Checklist, Project Scaffold

Set up the `heartbeat/` sub-project with `uv`, create the configuration module, and add the heartbeat checklist to the sample vault.

**Tasks:**
- Create `heartbeat/pyproject.toml` with APScheduler, httpx, pydantic-settings, python-frontmatter
- Create `heartbeat/src/__init__.py`
- Create `heartbeat/src/config.py` with `HeartbeatSettings`
- Create `sample-vault/Meta/heartbeat.md` with a realistic demo checklist

### Phase 2: Core Implementation — Scheduler + Tick Logic

Build the heartbeat tick function and the APScheduler loop.

**Tasks:**
- Create `heartbeat/src/heartbeat.py` with:
  - Memory reading (reuse pattern from voice proxy)
  - Heartbeat checklist reading from vault
  - Converse API call with heartbeat prompt + memory injection
  - HEARTBEAT_OK suppression logic
  - Alert delivery (daily note append + console log)
  - Conversation ID persistence (file-based)
- Create `heartbeat/src/__main__.py` entry point

### Phase 3: Docker Integration

Package as a Docker service and add to the Compose stack.

**Tasks:**
- Create `heartbeat/Dockerfile`
- Add `heartbeat` service to `docker-compose.yml`
- Update `.env.example` with new variables

### Phase 4: Validation

Test all components.

**Tasks:**
- Lint and format check
- Manual test: run single tick, verify converse API call
- Manual test: verify HEARTBEAT_OK suppression
- Manual test: verify alert delivery to daily note
- Docker build and startup test

---

## STEP-BY-STEP TASKS

### Task 1: CREATE `heartbeat/pyproject.toml`

- **IMPLEMENT**: Standard sub-project definition mirroring `mcp-server/pyproject.toml` structure
- **PATTERN**: `mcp-server/pyproject.toml` for ruff config, pytest config, dependency group format
- **DEPENDENCIES**:
  - `apscheduler>=3.10.0,<4.0` — Async scheduler (stable v3 branch)
  - `httpx>=0.27.0` — Async HTTP for converse API
  - `pydantic-settings>=2.5.0` — Config from env vars
  - `python-dotenv>=1.0.0` — .env loading
  - `python-frontmatter>=1.1.0` — Parse vault YAML frontmatter
- **DEV DEPS**: `ruff>=0.8.0`, `pyright>=1.1.390`
- **GOTCHA**: No `[build-system]` needed (not a CLI tool like indexer). But include it anyway for consistency — use hatchling like indexer.
- **VALIDATE**: `cd heartbeat && uv sync`

### Task 2: CREATE `heartbeat/src/__init__.py`

- **IMPLEMENT**: Empty file, just a package marker
- **VALIDATE**: File exists

### Task 3: CREATE `heartbeat/src/config.py`

- **IMPLEMENT**: `HeartbeatSettings` class with these fields:
  ```
  elastic_url: str = ""
  elastic_api_key: str = ""
  agent_id: str = "athena"
  vault_path: str = "/vault"
  heartbeat_interval_minutes: int = 30
  heartbeat_active_hour_start: int = 8   # 8 AM
  heartbeat_active_hour_end: int = 22    # 10 PM
  conversation_id_file: str = "/tmp/athena-heartbeat-conversation-id"
  log_level: str = "INFO"
  ```
- **PATTERN**: `mcp-server/src/config.py` — exact same `model_config` dict with `env_file`, `extra: "ignore"`
- **ADD**: `kibana_url` property that derives `.kb.` from `.es.` URL (same as `voice-client/serve.py:56-58`)
- **VALIDATE**: `cd heartbeat && uv run python -c "from src.config import HeartbeatSettings; s = HeartbeatSettings(); print(s.heartbeat_interval_minutes)"`

### Task 4: CREATE `sample-vault/Meta/heartbeat.md`

- **IMPLEMENT**: A demo heartbeat checklist following OpenClaw's pattern. Include realistic items that exercise Athena's existing tools:
  ```markdown
  ---
  title: "Heartbeat Checklist"
  tags:
    - meta
    - heartbeat
  created: 2026-02-16
  updated: 2026-02-16
  ---

  # Heartbeat Checklist

  Instructions for proactive checks. Evaluate each section, then respond HEARTBEAT_OK if nothing needs attention.

  ## Morning (before 10:00)
  - Check if today's daily plan exists. If not, remind the user to plan their day.
  - Look for any Q1 tasks with deadlines today or tomorrow. Alert if found.

  ## Throughout Day
  - Check for Q1 (urgent + important) tasks that are still pending. If any have been pending for more than 3 days, alert.
  - If a task deadline is within 2 hours, send an urgent reminder.

  ## Evening (after 18:00)
  - Summarize today's completed tasks.
  - If the daily plan has incomplete tasks, suggest carrying them to tomorrow.
  ```
- **PATTERN**: Matches existing vault note format with YAML frontmatter (see `sample-vault/Meta/user-profile.md`)
- **VALIDATE**: File has valid YAML frontmatter

### Task 5: CREATE `heartbeat/src/heartbeat.py`

This is the core module. It contains:

1. **`_strip_frontmatter(text: str) -> str`** — Same as `voice-client/serve.py:66-72`
2. **`_read_memory_context(vault_path: Path) -> str`** — Reads user-profile.md + memory.md, same pattern as `voice-client/serve.py:75-98`
3. **`_read_heartbeat_checklist(vault_path: Path) -> str | None`** — Reads `Meta/heartbeat.md`, strips frontmatter, returns content or None if missing/empty
4. **`_load_conversation_id(path: str) -> str | None`** — Read persisted conversation ID from file, or None
5. **`_save_conversation_id(path: str, conversation_id: str) -> None`** — Write conversation ID to file
6. **`_append_alert_to_daily_note(vault_path: Path, alert_text: str) -> None`** — Append a `## Heartbeat Alert (HH:MM UTC)` block to today's daily note, creating it if needed. Mirror `mcp-server/src/tools/knowledge.py:20-57` but simplified (no ES dependency, just frontmatter + file write)
7. **`async def heartbeat_tick(settings: HeartbeatSettings) -> None`** — The main tick function:
   - Read heartbeat checklist → skip if empty/missing
   - Read memory context
   - Load conversation ID
   - Build prompt: `"HEARTBEAT CHECK: Read the following checklist and evaluate each item using your available tools. If nothing needs the user's attention, respond with exactly HEARTBEAT_OK and nothing else. If something needs attention, describe it clearly.\n\n{checklist_content}"`
   - POST to converse API with memory injection
   - Parse response: if `response.response.message` contains `HEARTBEAT_OK` → log debug, skip
   - Otherwise → log the alert, append to daily note
   - Save conversation ID from response
8. **`def run_scheduler(settings: HeartbeatSettings) -> None`** — Creates `AsyncIOScheduler`, adds `heartbeat_tick` with `CronTrigger(minute=f"*/{settings.heartbeat_interval_minutes}", hour=f"{settings.heartbeat_active_hour_start}-{settings.heartbeat_active_hour_end - 1}")`, handles SIGTERM/SIGINT gracefully

- **IMPORTS**:
  ```python
  import asyncio
  import json
  import logging
  import signal
  from datetime import UTC, datetime
  from pathlib import Path

  import frontmatter
  import httpx
  from apscheduler.schedulers.asyncio import AsyncIOScheduler
  from apscheduler.triggers.cron import CronTrigger

  from src.config import HeartbeatSettings
  ```
- **PATTERN**: `voice-client/serve.py` for converse API call; `mcp-server/src/tools/knowledge.py` for daily note append
- **GOTCHA**: Response path is `data["response"]["message"]`, NOT `data["response"]` (documented in api-reference.md:293)
- **GOTCHA**: `CronTrigger` `hour` range is inclusive — `hour="8-21"` means 8:00 to 21:59. For active_hour_end=22, use `hour="8-21"` (end minus 1)
- **GOTCHA**: httpx client must set headers: `Authorization: ApiKey {key}`, `kbn-xsrf: true`, `Content-Type: application/json`
- **GOTCHA**: Don't create httpx.AsyncClient at module level — create it inside the tick function or as a module-level singleton that's closed on shutdown. In v3 AsyncIOScheduler, the event loop may not exist at import time.
- **VALIDATE**: `cd heartbeat && uv run ruff check src/ && uv run ruff format --check src/`

### Task 6: CREATE `heartbeat/src/__main__.py`

- **IMPLEMENT**:
  ```python
  """Entry point for the heartbeat service: python -m src"""
  import logging
  from src.config import HeartbeatSettings
  from src.heartbeat import run_scheduler

  settings = HeartbeatSettings()
  logging.basicConfig(
      level=getattr(logging, settings.log_level.upper(), logging.INFO),
      format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
      datefmt="%H:%M:%S",
  )
  run_scheduler(settings)
  ```
- **PATTERN**: `mcp-server/src/__main__.py` for entry point pattern
- **VALIDATE**: `cd heartbeat && uv run python -m src --help` (should start then exit if no ES credentials)

### Task 7: CREATE `heartbeat/Dockerfile`

- **IMPLEMENT**: Multi-stage build with uv, matching `mcp-server/Dockerfile`
  ```dockerfile
  FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
  WORKDIR /app
  COPY pyproject.toml uv.lock ./
  RUN uv sync --frozen --no-dev --no-install-project
  COPY src/ src/
  RUN uv sync --frozen --no-dev

  FROM python:3.12-slim
  WORKDIR /app
  COPY --from=builder /app/.venv /app/.venv
  COPY --from=builder /app/src /app/src
  ENV PATH="/app/.venv/bin:$PATH"
  CMD ["python", "-m", "src"]
  ```
- **PATTERN**: `mcp-server/Dockerfile` for multi-stage uv build
- **GOTCHA**: CMD must be exec form `["python", "-m", "src"]` so Python is PID 1 and receives SIGTERM
- **VALIDATE**: `cd heartbeat && uv lock` (ensure uv.lock exists for `--frozen` build)

### Task 8: UPDATE `docker-compose.yml` — Add heartbeat service

- **IMPLEMENT**: Add new service after `voice-proxy`, before `artemis-frontend`:
  ```yaml
  # --- Athena Heartbeat Service ---
  heartbeat:
    profiles:
      - heartbeat
    build:
      context: ./heartbeat
      dockerfile: Dockerfile
    volumes:
      - "${VAULT_PATH:-./sample-vault}:/vault:ro"
    env_file:
      - .env
    environment:
      - VAULT_PATH=/vault
    stop_grace_period: 30s
    restart: unless-stopped
  ```
- **KEY DECISIONS**:
  - `profiles: [heartbeat]` — opt-in via `docker compose --profile heartbeat up`. Not started by default (costs LLM tokens every 30 min).
  - `volumes: /vault:ro` — read-only vault access (heartbeat reads checklist + memory, alert delivery writes via converse API which triggers MCP tools, not direct file writes). Actually — the heartbeat appends alerts directly to daily notes via frontmatter, so it needs `:rw`.
  - `stop_grace_period: 30s` — give running tick time to finish
- **PATTERN**: Matches `voice-proxy` service structure (env_file, volumes, environment override)
- **VALIDATE**: `docker compose config`

### Task 9: UPDATE `.env.example` — Add heartbeat variables

- **IMPLEMENT**: Add new section after the ngrok block:
  ```
  # --- Heartbeat (proactive agent check-ins) ---
  # Interval between checks in minutes
  HEARTBEAT_INTERVAL_MINUTES=30
  # Active hours (24h format) — heartbeat only runs during these hours
  HEARTBEAT_ACTIVE_HOUR_START=8
  HEARTBEAT_ACTIVE_HOUR_END=22
  ```
- **VALIDATE**: File is valid shell syntax (no spaces around `=`)

---

## TESTING STRATEGY

### Unit Tests

No unit test files created for hackathon scope — focus on manual validation. The heartbeat service is thin glue code (scheduler + HTTP + file I/O) where mocking would be more complex than the code itself.

### Integration Tests

Manual integration testing via running a single tick:
```bash
cd heartbeat && uv run python -c "
import asyncio
from src.config import HeartbeatSettings
from src.heartbeat import heartbeat_tick
settings = HeartbeatSettings()
asyncio.run(heartbeat_tick(settings))
"
```

### Edge Cases

- `Meta/heartbeat.md` doesn't exist → tick skips silently (logged at debug level)
- `Meta/heartbeat.md` is empty → tick skips silently
- Kibana unreachable → tick logs error, doesn't crash, scheduler continues
- Agent responds with HEARTBEAT_OK → suppressed, no daily note entry
- Agent responds with an alert → appended to daily note
- Daily note doesn't exist yet → created with frontmatter
- Conversation ID file doesn't exist → fresh conversation started
- Invalid conversation ID (expired) → Kibana creates new conversation

---

## VALIDATION COMMANDS

### Level 1: Syntax & Style

```bash
cd heartbeat && uv run ruff check src/
cd heartbeat && uv run ruff format --check src/
```

### Level 2: Type Checking

```bash
cd heartbeat && uv run pyright src/
```

### Level 3: Import Verification

```bash
cd heartbeat && uv run python -c "from src.config import HeartbeatSettings; print('config OK')"
cd heartbeat && uv run python -c "from src.heartbeat import heartbeat_tick, run_scheduler; print('heartbeat OK')"
```

### Level 4: Docker Validation

```bash
# Compose config validates
docker compose --profile heartbeat config

# Docker builds
docker compose --profile heartbeat build heartbeat
```

### Level 5: Manual Single-Tick Test

```bash
# Run one heartbeat tick (requires ELASTIC_URL + ELASTIC_API_KEY in .env)
cd heartbeat && uv run python -c "
import asyncio
from src.config import HeartbeatSettings
from src.heartbeat import heartbeat_tick
settings = HeartbeatSettings()
asyncio.run(heartbeat_tick(settings))
"
```

---

## ACCEPTANCE CRITERIA

- [ ] `heartbeat/` sub-project scaffolded with pyproject.toml, uv.lock, src/
- [ ] `HeartbeatSettings` loads from `.env` with sensible defaults
- [ ] `Meta/heartbeat.md` exists in sample vault with realistic demo checklist
- [ ] `heartbeat_tick()` reads checklist, injects memory, calls converse API
- [ ] HEARTBEAT_OK responses are suppressed (no daily note entry, debug log only)
- [ ] Real alerts are appended to daily note as `## Heartbeat Alert (HH:MM UTC)` blocks
- [ ] Conversation ID is persisted across ticks for session continuity
- [ ] Scheduler runs only during configured active hours
- [ ] Docker service added under `heartbeat` profile (opt-in)
- [ ] All ruff checks pass with zero errors
- [ ] Docker compose config validates
- [ ] `.env.example` documents new variables

---

## COMPLETION CHECKLIST

- [ ] All tasks completed in order (Tasks 1-9)
- [ ] Each task validation passed
- [ ] `ruff check` + `ruff format --check` pass
- [ ] Import verification passes
- [ ] Docker compose config validates
- [ ] Docker build succeeds
- [ ] Manual single-tick test works (if ES credentials available)
- [ ] No regressions in existing services

---

## NOTES

### Design Decisions

1. **APScheduler v3 over v4**: v4 is alpha (`4.0.0a6`). v3.11.2 is stable and battle-tested. Given 11-day deadline, stability wins.

2. **CronTrigger over IntervalTrigger + guard**: `CronTrigger(minute="*/30", hour="8-21")` natively handles active hours. No runtime guard needed. Cleaner and more reliable than `IntervalTrigger` with `AndTrigger` (known bugs: [issue #361](https://github.com/agronholm/apscheduler/issues/361)).

3. **Profile-gated Docker service**: `profiles: [heartbeat]` means the heartbeat isn't started by default `docker compose up`. Each tick costs one LLM inference (~$0.50-2/day at 30-min intervals). User opts in with `--profile heartbeat`.

4. **File-based conversation ID persistence**: Simplest approach — write conversation ID to a file, read it on next tick. Docker volume or tmpfs. If the file is lost, a new conversation starts (no data loss, just context reset).

5. **Direct daily note writing over MCP**: The heartbeat writes alerts directly to the daily note via `python-frontmatter` (same as knowledge.py's `_append_to_daily_note`). This avoids a circular dependency (heartbeat → converse API → MCP → vault) and keeps alert delivery working even if MCP is down.

6. **Read-write vault mount**: Even though the heartbeat primarily reads (checklist + memory), it writes alerts to daily notes directly. Needs `:rw` volume mount.

7. **No separate notification channel**: For hackathon, alerts go to the daily note (visible in Obsidian) + console log. Post-hackathon: add Telegram/webhook delivery.

### Cost Estimation

At 30-minute intervals, 8 AM - 10 PM (28 ticks/day):
- With Claude Sonnet 4.5: ~$0.50-2/day (input: ~2K tokens for memory + checklist + tools; output: short)
- HEARTBEAT_OK ticks are cheap — short output, minimal tool use
- Alert ticks cost more — agent may call `artemis_list_tasks`, `artemis_get_daily_plan`

### Future Enhancements (Post-Hackathon)

- Telegram/Discord webhook delivery for real-time alerts
- Configurable model override (cheaper model for heartbeat vs main conversations)
- Multiple checklist schedules (morning-only items, evening-only items)
- Heartbeat history in Elasticsearch (track what was checked and when)
- APScheduler v4 migration when it reaches stable
