# ADR-003: OpenClaw/NanoClaw Pattern Research for Athena

**Date:** 2026-02-15
**Status:** Research Complete (pending implementation decisions)
**Context:** Evaluate patterns from OpenClaw and NanoClaw for adoption in Athena — specifically Memory System, Heartbeat, and Skills.

---

## Motivation

Athena currently works as a reactive conversational agent: the user asks, Athena responds. To make it more sustainable and capable as a "second brain" assistant, we researched how OpenClaw (https://github.com/openclaw/openclaw) and NanoClaw (https://github.com/qwibitai/nanoclaw) solve three problems:

1. **Persistent Memory** — How the agent remembers across sessions
2. **Proactive Behavior (Heartbeat)** — How the agent acts without being asked
3. **Extensible Skills** — How the agent learns new capabilities

---

## 1. Memory System

### OpenClaw's Approach

OpenClaw uses a **file-first, Markdown-native memory system** with two layers:

**Layer 1 — Human-readable Markdown files (canonical source of truth)**

| File | Purpose | Loaded When |
|------|---------|-------------|
| `SOUL.md` | Personality, values, communication style | Every session start |
| `USER.md` | Who the human is: name, timezone, preferences | Every session start |
| `MEMORY.md` | Long-term curated facts and decisions | Private sessions only |
| `AGENTS.md` | Operating instructions and rules | Every session start |
| `IDENTITY.md` | Agent name and visual identity | Every session start |
| `HEARTBEAT.md` | Checklist for proactive heartbeat checks | Every heartbeat tick |
| `memory/YYYY-MM-DD.md` | Daily memory logs (append-only) | On-demand via search |
| `memory/YYYY-MM-DD-slug.md` | Session summaries (auto-created on `/new`) | On-demand via search |

**Layer 2 — Derived machine-recall index (rebuildable)**
- SQLite database with FTS5 full-text search + optional vector embeddings
- Hybrid search: 70% vector / 30% BM25 by default
- Always rebuildable from the Markdown source files

**Key constraints:**
- Individual file cap: 20,000 characters per file
- Total bootstrap cap: 24,000 characters across all injected files
- Large files are trimmed; blank files are skipped

### How Memory Is Read

1. **Automatic bootstrap injection** — Core files (SOUL.md, USER.md, MEMORY.md, etc.) are injected into the system prompt at the start of every session. This gives the agent its personality and user context without tool calls.

2. **On-demand tool access** — Two tools for deeper recall:
   - `memory_search` — Semantic search across all memory files (hybrid vector/BM25, top-6 results, min score 0.35)
   - `memory_get` — Direct file read with optional line-range for targeted retrieval

### How Memory Is Written

1. **Direct agent writes** — When user says "remember this", the agent writes to `memory/YYYY-MM-DD.md` or `MEMORY.md`
2. **Pre-compaction memory flush** — Automatic, silent. Before context window fills up, the agent runs a hidden turn to persist important context to daily memory files. Triggers at `contextWindow - reserveFloor - 4000 tokens`.
3. **Session-memory hook** — On `/new` command, extracts last 15 messages and creates `memory/YYYY-MM-DD-slug.md` with an LLM-generated descriptive filename.

### NanoClaw's Approach

NanoClaw uses a simpler **CLAUDE.md hierarchy** per group:

| Level | Location | Written By |
|-------|----------|------------|
| Global | `groups/global/CLAUDE.md` | Main group only |
| Group | `groups/{name}/CLAUDE.md` | That group |
| Conversations | `groups/{name}/conversations/*.md` | Auto-archived by PreCompact hook |

Key difference: NanoClaw piggybacks on Claude Code's native CLAUDE.md loading. No custom memory tools needed — the framework handles it. Conversation archiving happens automatically before context compaction.

### Mapping to Athena

| OpenClaw File | Athena Equivalent | Notes |
|---|---|---|
| `SOUL.md` | `agent-config/system-prompt.md` | Already exists (245 lines) |
| `USER.md` | `vault: Meta/user-profile.md` | New — user identity, preferences, timezone |
| `MEMORY.md` | `vault: Meta/memory.md` | New — curated long-term facts and decisions |
| `HEARTBEAT.md` | `vault: Meta/heartbeat.md` | New — proactive checklist |
| `memory/YYYY-MM-DD.md` | Obsidian Daily Notes | Already supported via vault_read → daily_note |
| Session summaries | `save_conversation_summary` (ES) | Already implemented as MCP tool |

**How it works in Athena:**
- The **system prompt** (`agent-config/system-prompt.md`) already serves as SOUL.md — it defines Athena's persona, guardrails, and tool selection guide.
- **user-profile.md** and **memory.md** would be vault notes that we inject into the system prompt via Elastic Agent Builder's `configuration_overrides.systemPromptAddition` field.
- The Agent Builder converse API supports runtime instruction injection:
  ```json
  {
    "input": "...",
    "agent_id": "athena",
    "configuration_overrides": {
      "systemPromptAddition": "## User Profile\n{contents of user-profile.md}\n\n## Memory\n{contents of memory.md}"
    }
  }
  ```
- This means the voice proxy (or any client) reads memory files from the vault at request time and injects them into each conversation turn.

---

## 2. Heartbeat System

### OpenClaw's Approach

A **cron-driven 30-minute cycle** that wakes the agent to evaluate a user-defined checklist:

1. Scheduler fires every 30 minutes (configurable)
2. Injects synthetic prompt: *"Read HEARTBEAT.md. Follow it strictly. If nothing needs attention, reply HEARTBEAT_OK."*
3. Agent evaluates the checklist against current context
4. `HEARTBEAT_OK` responses are **silently suppressed** (not delivered to user)
5. Real alerts are delivered via the configured channel

**Key design decisions:**
- Runs in main session context (has full conversation history)
- Active hours configurable (e.g., 8 AM - 10 PM)
- Empty HEARTBEAT.md causes the run to be skipped (token saving)
- Cheaper model can be used for heartbeat evaluation

**HEARTBEAT.md example:**
```markdown
# Heartbeat Checklist

## Morning (8:00-8:30 AM)
- Check pending Artemis tasks and send morning briefing
- Review today's daily note for any items

## Throughout Day
- If any Q1 task has a deadline within 2 hours, send reminder
- Check if daily plan has been created; if not, offer to help

## Evening (8:00-9:00 PM)
- Summarize today's completed tasks
- Suggest tasks to carry over to tomorrow
```

### NanoClaw's Approach

NanoClaw does **not** have a heartbeat. Instead, it uses idle timeouts + close sentinels for container lifecycle management, plus a task scheduler (cron/interval/once) that checks SQLite every 60 seconds.

### Integration Options for Athena

#### Option A: External Python Service with APScheduler (Recommended for production)

A new `heartbeat/` sub-project with a long-running async process:

```python
# heartbeat/main.py — sketch
async def heartbeat_tick():
    # 1. Read HEARTBEAT.md from vault
    # 2. Read user-profile.md and memory.md
    # 3. POST /api/agent_builder/converse with heartbeat prompt + memory injection
    # 4. If response != HEARTBEAT_OK, deliver alert (webhook, Telegram, etc.)
    # 5. Persist conversation_id for session continuity
```

- Uses APScheduler's `AsyncIOScheduler` with `IntervalTrigger`
- Runs as a Docker service in the Compose stack
- Full MCP tool access (the converse API triggers normal agent execution)
- Session continuity via persistent `conversation_id`

#### Option B: Elastic Workflows (Technical Preview)

Native scheduled triggers in Elastic 9.3+:
```yaml
trigger:
  type: scheduled
  interval: "30m"
steps:
  - type: ai.agent
    config:
      agent_id: athena
      input: "HEARTBEAT: ..."
```

Pros: No external process. Cons: May not be available on our Serverless trial.

#### Option C: System Cron + One-Shot Script (Simplest)

```bash
*/30 8-22 * * * cd /home/stardust/Athena/heartbeat && uv run heartbeat.py >> heartbeat.log 2>&1
```

Pros: Zero dependencies, battle-tested. Cons: No persistent session (fresh conversation per tick unless we persist conversation_id to file).

### Cost Considerations

Every heartbeat tick = 1 full LLM inference call. At 30-minute intervals (8 AM - 10 PM = 28 ticks/day):
- With Claude Sonnet: ~$0.50-2/day (acceptable)
- With Claude Opus: ~$5-30/day (expensive)

**Recommendation:** Use a cheaper model for heartbeat evaluation. Elastic Agent Builder supports model selection per conversation via configuration overrides.

---

## 3. Skills System

### OpenClaw's Approach

Skills are modular packages with **progressive disclosure**:

1. **Metadata** (name + description, ~100 words) — Always in context
2. **SKILL.md body** — Loaded only when skill triggers
3. **Bundled resources** (scripts, references) — Loaded on demand

Skills are `SKILL.md` files with YAML frontmatter:
```markdown
---
name: obsidian
description: Work with Obsidian vaults via obsidian-cli.
metadata:
  openclaw:
    requires:
      bins: ["obsidian-cli"]
---
# Obsidian
Instructions for using this skill...
```

70+ bundled skills. Loaded from multiple directories with priority: `bundled < managed < workspace`.

The **Skill-Creator** meta-skill guides creation of new skills with init/package/validate scripts.

### NanoClaw's Approach

Skills are **Claude Code transformation instructions** — `.claude/skills/*/SKILL.md` files that teach Claude Code how to modify the codebase. Not runtime plugins; they modify source code when invoked. Examples: `/add-telegram`, `/add-gmail`, `/convert-to-docker`.

### Relevance to Athena

Skills are less applicable to Athena's architecture because:
- Athena's tool system is MCP-based (already modular)
- Elastic Agent Builder handles tool routing and prompt management
- Adding a new "skill" in Athena means adding a new MCP tool or ES|QL query

**However**, the concept of storing skill-like instructions as vault notes is interesting:
- A `Meta/skills/` folder in the vault could contain instruction templates
- The agent could read these at runtime for specialized tasks (e.g., "how to do a weekly review", "how to write a meeting note")
- This is lower priority than memory and heartbeat

---

## 4. Other Patterns Worth Noting

### Hooks (OpenClaw)
Event-driven lifecycle hooks (`command:new`, `agent:bootstrap`, `gateway:startup`). Three bundled hooks:
1. `session-memory` — Saves session to memory on `/new`
2. `boot-md` — Runs BOOT.md on gateway start
3. `command-logger` — Logs all commands for auditing

**Athena equivalent:** Not directly applicable since we don't control the Agent Builder lifecycle. But the concept of "save conversation summary on session end" already exists via `save_conversation_summary`.

### Channel Adapters (OpenClaw)
Plugin-based channel system supporting WhatsApp, Telegram, Slack, Discord, etc. Each adapter implements a well-defined interface.

**Athena equivalent:** Currently voice-only via the voice proxy. Adding Telegram/Discord would be a post-hackathon feature, using the same pattern: a thin adapter that calls `POST /api/agent_builder/converse`.

### Agent Swarms (NanoClaw)
Multiple specialized agents collaborating via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`. Container-isolated with per-group IPC.

**Athena equivalent:** Out of scope. Elastic Agent Builder doesn't natively support multi-agent orchestration in the current version.

---

## 5. Key Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Memory file location | Obsidian vault (`Meta/` folder) | Stays in user's knowledge graph, editable in Obsidian |
| Memory injection method | `configuration_overrides.systemPromptAddition` | Supported by Agent Builder API, no agent code changes |
| Heartbeat approach | Option A (APScheduler) or C (cron) | A for production, C for hackathon demo |
| Heartbeat delivery | Via voice proxy webhook or Telegram | Depends on channel availability |
| Skills system | Defer | MCP tools already provide modularity |
| Hooks system | Defer | Agent Builder lifecycle not extensible |

---

## 6. Feasibility Assessment (Hackathon Timeline)

| Feature | Effort | Demo Value | Verdict |
|---------|--------|------------|---------|
| Memory files (`user-profile.md`, `memory.md`) | ~2h | High — shows personalization | **Do it** |
| System prompt injection via voice proxy | ~1h | High — makes memory functional | **Do it** |
| Conversation summary → daily note | ~1h | Medium — shows continuity | **Do it** |
| Heartbeat service (basic cron version) | ~3h | High — shows proactivity | **If time allows** |
| HEARTBEAT.md in vault | ~30m | Medium — shows customization | **If doing heartbeat** |
| Skills as vault notes | ~2h | Medium — shows extensibility | **Defer** |

**Total estimated effort for core features: ~4h**
**Total with heartbeat: ~7h**

---

## 7. Implementation Plan (Proposed)

### Step 1: Memory Files (~2h)
1. Create `Meta/user-profile.md` in sample vault with demo user data
2. Create `Meta/memory.md` in sample vault with starter content
3. Add MCP tool `update_user_profile` to let the agent write to user-profile.md
4. Add MCP tool `update_memory` to let the agent append to memory.md

### Step 2: Memory Injection (~1h)
1. Modify voice proxy `chat()` endpoint to:
   - Read `Meta/user-profile.md` and `Meta/memory.md` from vault
   - Include their content in `configuration_overrides.systemPromptAddition`
2. Update system prompt to reference these files and instruct the agent to use them

### Step 3: Conversation Summary to Daily Note (~1h)
1. Enhance `save_conversation_summary` to also append a summary to the Obsidian daily note
2. This creates the `memory/YYYY-MM-DD.md` equivalent using Obsidian's existing daily notes structure

### Step 4: Heartbeat (if time allows, ~3h)
1. Create `heartbeat/` sub-project with `uv` and APScheduler
2. Read `Meta/heartbeat.md` from vault for the checklist
3. Call converse API with heartbeat prompt + memory injection
4. Suppress HEARTBEAT_OK, deliver real alerts via webhook
5. Add as Docker service in compose stack

---

## 8. Sources

- [OpenClaw GitHub](https://github.com/openclaw/openclaw) — Full source code analysis
- [OpenClaw Agent Docs](https://docs.openclaw.ai/concepts/agent) — Agent architecture and bootstrap files
- [OpenClaw Memory Docs](https://docs.openclaw.ai/concepts/memory) — Memory system design
- [OpenClaw Heartbeat Docs](https://docs.openclaw.ai/gateway/heartbeat) — Heartbeat configuration
- [NanoClaw GitHub](https://github.com/qwibitai/nanoclaw) — Source code analysis (security model, CLAUDE.md hierarchy)
- [Elastic Agent Builder Converse API](https://www.elastic.co/docs/api/doc/serverless/operation/operation-post-agent-builder-converse)
- [Elastic Workflows Blog](https://www.elastic.co/search-labs/blog/elastic-workflows-automation)
- `reference/claude-agent-sdk-proactive-agent/` — Proactive agent pattern with Claude Agent SDK
