# ADR-008: Memory System via Vault Files and System Prompt Injection

**Date:** 2026-02-16
**Status:** Accepted
**Context:** Athena needs persistent memory across conversation sessions on Elastic Agent Builder

---

## Problem

Elastic Agent Builder does not have built-in persistent memory. Each conversation starts fresh — the agent doesn't know the user's name, past decisions, or project context. We need memory that:

1. Persists across sessions
2. Is readable by the agent on every turn
3. Is editable by both the agent and the user
4. Doesn't require custom backend infrastructure

## Options

### Option A: Database-Backed Memory — Rejected

Store memory in Supabase/Postgres. Add MCP tools to read/write memory records.

- **Pro:** Structured data, query flexibility
- **Con:** New infrastructure, new MCP tools, memory is invisible to the user, not part of the knowledge graph

### Option B: ES-Only Memory — Rejected

Store memory documents in a dedicated ES index. Query via ES|QL tools.

- **Pro:** Semantic search over memories
- **Con:** Still invisible to user. Agent can't easily update (no ES write tool for arbitrary docs). Separate from the vault ecosystem.

### Option C: Vault Markdown Files + System Prompt Injection (Selected)

Store memory as Markdown files in the Obsidian vault (`Meta/` folder). Inject their content into every conversation via the converse API's `configuration_overrides.instructions` field.

Inspired by OpenClaw's `SOUL.md` / `USER.md` / `MEMORY.md` pattern (ADR-003).

## Decision

Two memory files in the vault:

| File | Purpose | Who Edits |
|------|---------|-----------|
| `Meta/user-profile.md` | User identity, preferences, timezone, team, projects | User only (agent needs permission) |
| `Meta/memory.md` | Durable facts learned across sessions — decisions, preferences, relationships | Agent appends via `vault_manage`; user can edit in Obsidian |

**Injection mechanism:** The voice proxy reads both files on every chat request and injects their content via `configuration_overrides.instructions` in the Kibana converse API payload. The agent receives memory as additional system prompt context.

**Update mechanism:** The agent uses the existing `vault_manage` tool (`append_note` operation) to add new facts to `Meta/memory.md`. No new tools needed.

**Conversation summaries** are a separate layer — dual-written to ES (for semantic search) and daily notes (for vault continuity).

## Consequences

- Memory files live in the user's Obsidian vault — visible, editable, part of the knowledge graph
- No new infrastructure — reuses existing vault filesystem and MCP tools
- Agent greets user by name, references projects/preferences without asking
- Memory injection adds ~2-3KB to every request — within prompt limits
- Voice proxy is the injection point (not the agent itself) — if using Agent Builder's native chat UI, memory isn't injected (limitation)
- `user-profile.md` is protected — agent must ask permission before modifying
- Memory grows unboundedly — may need periodic pruning (future concern)
- The converse API field is `instructions`, not `systemPromptAddition` (discovered via 400 error on Day 36)
