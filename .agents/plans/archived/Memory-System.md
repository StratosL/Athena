# Feature: Memory System

## Context

Athena is a conversational AI agent that currently has no memory across sessions. Each conversation starts from scratch — the agent doesn't know who the user is, what was discussed previously, or what decisions were made. ADR-003 (OpenClaw/NanoClaw research) identified a memory pattern: inject vault-stored memory files into the system prompt at request time via Elastic Agent Builder's `configuration_overrides.systemPromptAddition` API field. This gives the agent persistent personalization and continuity without changing the agent infrastructure.

**Estimated effort:** ~4 hours (matches ADR-003 feasibility assessment)

## Solution

1. Create two memory files in the Obsidian vault under `Meta/` folder
2. Modify the voice proxy to read these files and inject them into every converse API call
3. Update the system prompt to tell the agent about memory files and how to update them
4. Enhance `save_conversation_summary` to also append to the daily note in the vault

No new MCP tools needed — the agent already has `vault_manage` (append_note, edit_note) to update memory files.

---

## STEP-BY-STEP TASKS

### Task 1: CREATE `sample-vault/Meta/user-profile.md` and `sample-vault/Meta/memory.md`

Create the `Meta/` folder and two memory files following the existing vault note format (frontmatter with title, tags, created, updated).

**`sample-vault/Meta/user-profile.md`** — Demo user profile for "Stratos":
- Name, role (full-stack engineer at Helios), timezone (Europe/Athens)
- Communication preferences (concise, numbered lists, cite vault paths)
- Vault organization (which folders contain what)
- Current focus (Q1 2026 — API refactoring, Athena hackathon)
- Team members (Nikos, Elena, Mara, Alex)
- Work patterns (deep focus mornings, standups at 10:30)

**`sample-vault/Meta/memory.md`** — Starter long-term memory:
- Key decisions (cursor pagination, JWT auth, migration order)
- Project relationships (API Refactoring depends on DB Migration + Auth Module)
- Preferences discovered (afternoon PR reviews, default Q2 for ambiguous tasks)

**PATTERN:** Follow frontmatter format from `sample-vault/Daily Notes/2026-02-12.md` (lines 1-8)

**VALIDATE:**
```bash
ls sample-vault/Meta/
python3 -c "import frontmatter; print(frontmatter.load('sample-vault/Meta/user-profile.md').metadata)"
```

---

### Task 2: UPDATE `docker-compose.yml` — add vault mount to voice-proxy

**File:** `docker-compose.yml` lines 47-56 (voice-proxy service)

Add vault volume mount (read-only) and `VAULT_PATH` environment variable:

```yaml
  voice-proxy:
    build:
      context: ./voice-client
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    volumes:
      - "${VAULT_PATH:-./sample-vault}:/vault:ro"
    env_file:
      - .env
    environment:
      - VAULT_PATH=/vault
    restart: unless-stopped
```

**PATTERN:** Mirror `mcp-server` service at lines 35-41 (same `VAULT_PATH` variable, same default)

**VALIDATE:**
```bash
docker compose config | grep -A 15 "voice-proxy"
```

---

### Task 3: UPDATE `voice-client/serve.py` — add memory injection to chat endpoint

Three surgical changes:

**3a.** Add `vault_path` field to `VoiceSettings` class (line 46):
```python
vault_path: str = "/vault"
```

**3b.** Add `_read_memory_context()` helper function after `settings = VoiceSettings()` (line 60):
- Reads `Meta/user-profile.md` and `Meta/memory.md` from `settings.vault_path`
- Strips YAML frontmatter (between `---` delimiters)
- Truncates at 20,000 chars per file (OpenClaw limit from ADR-003)
- Returns empty string if files don't exist (graceful degradation)
- Uses plain `pathlib.Path.read_text()` — no VaultManager dependency

**3c.** In `chat()` endpoint (line 103, after building payload dict), inject memory context:
```python
memory_context = _read_memory_context()
if memory_context:
    payload["configuration_overrides"] = {
        "systemPromptAddition": memory_context,
    }
```

**IMPORTANT FILES TO READ:**
- `voice-client/serve.py` lines 39-60 — VoiceSettings class and module-level setup
- `voice-client/serve.py` lines 86-124 — chat() endpoint (injection point)
- `decisions/003-openclaw-patterns-research.md` lines 85-98 — configuration_overrides API format

**VALIDATE:**
```bash
cd voice-client && uv run python -c "from serve import _read_memory_context; print(repr(_read_memory_context()[:200]))"
```

---

### Task 4: UPDATE `agent-config/system-prompt.md` — expand Memory & Context section

**File:** `agent-config/system-prompt.md` lines 231-234

Replace the current 4-line "Memory & Context" section with a comprehensive guide:

- Explain that User Profile and Agent Memory are injected automatically each turn
- Tell the agent to reference profile naturally (greet by name, respect timezone)
- Tell the agent to update `Meta/memory.md` via `vault_manage` → `append_note` when learning durable facts
- NEVER modify `Meta/user-profile.md` without explicit user permission
- Distinguish memory.md (durable facts) vs. save_conversation_summary (session context)
- Keep the existing guidance about save_conversation_summary

**IMPORTANT FILES TO READ:**
- `agent-config/system-prompt.md` full file — understand the existing structure, don't break section flow
- `mcp-server/src/tools/vault.py` lines 138-228 — vault_manage tool signature (the agent uses this to update memory)

**VALIDATE:**
```bash
wc -l agent-config/system-prompt.md
grep "Meta/memory.md" agent-config/system-prompt.md
```

---

### Task 5: UPDATE `mcp-server/src/tools/knowledge.py` — append summary to daily note

Enhance `save_conversation_summary` to also write to `Daily Notes/YYYY-MM-DD.md` via `vault_manager`.

Changes:
1. Import `vault_manager` from `src.server` (same pattern as `src/tools/vault.py` line 14)
2. Add `_append_to_daily_note(summary, topics)` helper:
   - Formats a `## Conversation Summary (HH:MM UTC)` block
   - Calls `vault_manager.append_to_note()` on `Daily Notes/YYYY-MM-DD.md`
   - If daily note doesn't exist, creates it with `vault_manager.write_note()` using same format as existing daily notes (title=date, tags=[daily, journal], header=`# Weekday, Month DD, YYYY`)
   - Non-fatal: if vault write fails, log and continue (ES is the primary store)
3. Call `_append_to_daily_note()` after successful ES write in the main tool function
4. Return JSON result with both `es_document_id` and `daily_note` path

**IMPORTANT FILES TO READ:**
- `mcp-server/src/tools/knowledge.py` full file — current implementation
- `mcp-server/src/vault_manager.py` lines 238-284 — write_note() and append_to_note() signatures
- `sample-vault/Daily Notes/2026-02-12.md` — daily note format to follow
- `mcp-server/src/tools/vault.py` line 14 — import pattern for vault_manager

**VALIDATE:**
```bash
cd mcp-server && uv run ruff check src/tools/knowledge.py
cd mcp-server && uv run python -c "from src.tools.knowledge import _append_to_daily_note; print('import ok')"
```

---

### Task 6: UPDATE `NOTE_TYPE_FOLDER_MAP` in vault manager and indexer

Add `"meta": "meta"` to the folder map in both files so Meta/ notes get a proper `note_type`.

**Files:**
- `mcp-server/src/vault_manager.py` line 24-30 — add `"meta": "meta"`
- `indexer/src/parser.py` line 14-20 — add `"meta": "meta"` (same map)

**VALIDATE:**
```bash
cd mcp-server && uv run ruff check src/vault_manager.py
cd indexer && uv run ruff check src/parser.py
```

---

## VALIDATION COMMANDS

### Level 1: Lint & Type Check
```bash
cd mcp-server && uv run ruff check src/ && uv run ruff format --check src/
cd voice-client && uv run ruff check serve.py && uv run ruff format --check serve.py
cd indexer && uv run ruff check src/ && uv run ruff format --check src/
```

### Level 2: Docker Build
```bash
docker compose build voice-proxy mcp-server
docker compose config
```

### Level 3: Integration — Memory Injection
```bash
# Start stack
docker compose up -d

# Verify memory files accessible
docker compose exec voice-proxy ls /vault/Meta/

# Test: agent should know user's name from injected profile
curl -s -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"input": "What is my name and timezone?"}' | python3 -m json.tool
```

### Level 4: Integration — Daily Note Append
```bash
# Invoke save_conversation_summary via MCP and check daily note
cat "sample-vault/Daily Notes/$(date +%Y-%m-%d).md"
# Should contain "## Conversation Summary" block
```

---

## ACCEPTANCE CRITERIA

- [ ] `sample-vault/Meta/` contains `user-profile.md` and `memory.md` with valid frontmatter
- [ ] Voice proxy injects memory into `configuration_overrides.systemPromptAddition` on every chat request
- [ ] Agent responds with user's name/timezone when asked (proves injection works)
- [ ] Missing memory files don't crash the chat endpoint (graceful degradation)
- [ ] System prompt instructs agent to update `Meta/memory.md` via existing vault tools
- [ ] `save_conversation_summary` appends to daily note in addition to ES write
- [ ] `NOTE_TYPE_FOLDER_MAP` includes `"meta": "meta"` in both vault manager and indexer
- [ ] All lint/format checks pass
- [ ] Docker Compose builds and starts with new volume mount
- [ ] No regressions — existing 28 E2E tests still conceptually pass

---

## NOTES

- **No new MCP tools**: Agent uses existing `vault_manage` (append_note/edit_note) to update memory. ADR-003 proposed `update_user_profile` and `update_memory` tools, but they're unnecessary — the existing tools already do this.
- **System prompt re-sync needed**: After editing `system-prompt.md`, the new text must be pasted into Elastic Agent Builder (Kibana UI or API). This is an operational step, not automated.
- **Heartbeat service**: Explicitly out of scope for this plan (separate feature per ADR-003).
- **Timezone in daily notes**: `_append_to_daily_note` uses UTC dates, consistent with existing `vault_manager.daily_note()` behavior.
