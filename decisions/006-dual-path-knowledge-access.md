# ADR-006: Dual-Path Knowledge Access (Elasticsearch + Vault Filesystem)

**Date:** 2026-02-12
**Status:** Accepted
**Context:** Athena needs to search, read, and write Obsidian vault notes — how should it access knowledge?

---

## Problem

An Obsidian vault is a folder of Markdown files. The agent needs to:
1. **Search** notes semantically ("what did I write about API design?")
2. **Read** full note content in real-time
3. **Write** new notes and append to existing ones
4. **Analyze** patterns across the vault (tag distribution, recent activity)

A single access path can't serve all four needs well.

## Options

### Option A: Elasticsearch Only — Rejected

Index all notes into ES. Read content from ES `_source`. Write notes by updating ES documents and syncing back to disk.

- **Pro:** Single data layer, semantic search built-in
- **Con:** Sync lag means reads return stale content. Write-back to disk is complex (frontmatter preservation, file creation). ES becomes a source of truth it wasn't designed to be.

### Option B: Filesystem Only — Rejected

Read/write directly from `.md` files. Implement search as in-memory grep.

- **Pro:** Always real-time, simple writes
- **Con:** No semantic search. Keyword grep doesn't find "authentication" when the note says "login flow." No aggregation capability.

### Option C: Dual-Path (Selected)

Elasticsearch for search and analytics. Direct filesystem access for reads and writes.

| Path | Technology | Purpose | Latency |
|------|-----------|---------|---------|
| Semantic search | Elasticsearch + ELSER | Find notes by meaning, aggregations | Seconds (indexing delay) |
| Direct vault | Filesystem via VaultManager | Read/write/query in real-time | Instant |

## Decision

Use both paths, each for what it does best:

- **ES|QL tools** (6) — semantic search, tag aggregation, recent notes, conversation history. Read-only.
- **Vault MCP tools** (3) — real-time read/write/query via VaultManager class. Filesystem access with path validation.
- **Indexer** — one-way sync from vault → ES. Checksum-based dedup. Watchdog for live sync.

The system prompt's tool selection guide tells the agent when to use each path:
- Broad conceptual search → ES|QL `search_notes`
- Full note content → vault `read_note`
- Create/edit notes → vault `vault_manage`
- If ES search returns nothing → fall back to vault `search_content` (keyword grep)

## Consequences

- Agent always reads current vault state (no stale data)
- Semantic search quality matches ES capabilities (ELSER v2)
- Writes go directly to disk — no sync delay for the user's Obsidian app
- Two data access paths means the system prompt must guide tool selection correctly
- Indexer must run to keep ES in sync — added the watcher service for automatic sync
- If ES is unavailable, agent can still fall back to vault filesystem search (degraded but functional)
