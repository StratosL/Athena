# Athena — Second Brain Orchestrator Agent

## Project Overview

Athena is a conversational AI agent built on **Elastic Agent Builder** that bridges an **Obsidian vault** (second brain) with **Artemis** (productivity app). It uses **Elasticsearch** for semantic search and a **direct vault filesystem layer** for real-time read/write. It also supports **voice interaction** via Whisper STT and OpenAI TTS.

**Read `PRD.md` before starting any work.** It is the single source of truth for architecture, tools, scope, and implementation phases.

## Tech Stack

- **Python 3.12+** with `uv` for all sub-projects
- **Elastic Agent Builder** — orchestrator (system prompt, tool routing, conversation management)
- **Elasticsearch Serverless** — semantic search with ELSER embeddings
- **MCP protocol** (SSE transport) — how Agent Builder talks to our tools
- **FastAPI** — existing Artemis backend
- **Docker + Docker Compose** — orchestration with vault volume mounting
- **OpenAI Whisper API** — speech-to-text
- **OpenAI TTS API** — text-to-speech

## Project Structure

```
Athena/
├── CLAUDE.md              ← you are here
├── PRD.md                 ← full architecture, tools, APIs, phases
├── .claude/commands/      ← slash commands
│
├── services/
│   └── artemis-backend/   ← Artemis FastAPI backend (merged from Artemis repo)
├── frontend/              ← Artemis React frontend (merged from Artemis repo)
├── indexer/               ← Obsidian → Elasticsearch sync (CLI tool)
├── mcp-server/            ← Unified MCP server (vault + artemis + research tools)
├── voice-client/          ← Thin HTML/JS voice interface
├── agent-config/          ← Agent Builder system prompt + ES|QL tool definitions
├── sample-vault/          ← Demo Obsidian vault (15-20 notes)
├── docs/                  ← Architecture diagrams
└── devpost/               ← Hackathon submission materials
```

## Key Architectural Decisions

### Dual-Path Knowledge Access
- **Elasticsearch** — semantic search (ELSER), aggregations, cross-note analytics. Used via ES|QL tools in Agent Builder.
- **Direct Vault** — real-time read/write to .md files via VaultManager class. Used via MCP tools.
- The indexer syncs vault → Elasticsearch. The VaultManager reads/writes vault directly.

### 3-Tool Vault Consolidation (from obsidian-ai-agent)
Instead of many single-purpose tools, vault access uses 3 tools with operation parameters:
- `vault_query` — discovery: list_structure, search_content, search_by_metadata, recent_changes
- `vault_read` — reading: read_note, read_multiple, daily_note
- `vault_manage` — writes: create_note, append_note, edit_note, move_note, delete_note, create_folder

### Voice = Pure I/O Layer
Voice sits in the client. The agent never knows if input was typed or spoken. Zero backend changes for voice.

### Human-in-the-Loop
The agent NEVER creates tasks, modifies notes, or takes destructive actions without user confirmation. Delete operations require `confirm_destructive=true`.

## Coding Standards

- Use `uv` for Python project management (not pip directly)
- Use `pydantic` v2 for all data models and validation
- Use `pydantic-settings` for configuration (all secrets via `.env`)
- Use `httpx` for async HTTP (not requests)
- Use `python-frontmatter` for Obsidian YAML parsing
- Type hints on all functions
- Docstrings on all public classes and functions
- Error handling: return error messages, never crash. MCP tools must handle unreachable services gracefully.

## Implementation Priority

| Priority | What | Why |
|----------|------|-----|
| P0 | Indexer + ES|QL tools + Artemis MCP tools | Core demo flow |
| P1 | VaultManager + vault MCP tools | Direct vault access |
| P2 | Research tools + conversation memory | Full experience |
| P3 | Voice client (Whisper + TTS) | Wow factor |

## Hackathon Deadline

**February 27, 2026, 1:00 PM EST (20:00 Athens time)**

Demo video must be recorded while Elastic Cloud trial is active (~14 days from signup).
