# Athena — Second Brain Orchestrator Agent

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Elastic](https://img.shields.io/badge/Elastic-Agent%20Builder-005571.svg)

**Turn scattered knowledge into focused action through intelligent, conversational orchestration**

[Quick Start](#-quick-start) · [Architecture](#-architecture) · [Features](#-features) · [Documentation](#-documentation)

</div>

---

## Overview

Athena is a conversational AI agent that bridges your personal knowledge vault ([Obsidian](https://obsidian.md)) with your productivity system ([Artemis](https://github.com/StratosL/Artemis)). Built on **Elastic Agent Builder**, it orchestrates across Elasticsearch, a local Obsidian vault, and the Artemis REST API — searching your notes semantically, extracting tasks, planning your day, and managing your knowledge, all through natural conversation.

**What makes Athena different:**

- **Dual-Path Knowledge Access**: Elasticsearch for semantic search and analytics; direct vault filesystem for real-time read/write — not one or the other, both
- **Bidirectional Vault Access**: Athena doesn't just search your notes — it creates new ones, appends to your journal, and organizes your knowledge as you work
- **Intelligence Over Automation**: Understands context, classifies priorities with the Eisenhower Matrix, and builds daily plans using the 1-3-5 rule — not just moving data between systems
- **Voice-First Option**: Talk to your second brain and hear it respond via Whisper STT and OpenAI TTS
- **Human-in-the-Loop**: Never creates tasks or modifies notes without your explicit confirmation

---

## Features

- **Semantic Note Search** — Ask questions in natural language; ELSER embeddings find notes by meaning, not just keywords
- **Direct Vault Read/Write** — Read, create, append, edit, move, and delete notes in your Obsidian vault in real-time
- **Smart Task Extraction** — Identify actionable tasks buried in notes, classify them by Eisenhower quadrant, confirm before creating
- **Daily Planning** — Build a focused daily plan using the 1-3-5 rule (1 major, 3 medium, 5 small) from your task backlog
- **Productivity Analytics** — Narrated insights from Artemis: completion rates, focus time, trends, and productivity scores
- **Conversation Memory** — Past conversations saved to Elasticsearch for future context recall
- **Web Research** — Search the web and fetch URL content, with findings saved back to your vault
- **Voice Interaction** — Speak to Athena via microphone; hear responses through text-to-speech

---

## Architecture

```
User <-> Voice Layer (STT/TTS) <-> Agent Builder (Athena) <-> Elasticsearch (ELSER)
              |                                                     ^
              v MCP Protocol                                        |
         Athena MCP Server                                          |
           |-- Vault tools     -> Obsidian Vault (filesystem)       |
           |-- Artemis tools   -> Artemis REST API (:8000)          |
           |-- Knowledge tools -> Elasticsearch (write-back)        |
           '-- Research tools  -> Web search + URL fetch            |
                                                                    |
         Indexer CLI ---------- Obsidian Vault -> Elasticsearch ----'
```

### Dual-Path Knowledge Access

| Path | Technology | Purpose | Latency |
|------|-----------|---------|---------|
| **Semantic Search** | Elasticsearch + ELSER | Find notes by meaning, aggregations, cross-note patterns | Seconds (sync delay) |
| **Direct Vault** | Filesystem via MCP | Read/write notes in real-time, list structure, metadata queries | Instant |

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestrator** | Elastic Agent Builder | System prompt, tool routing, conversation management |
| **Knowledge Store** | Elasticsearch Serverless + ELSER v2 | Semantic search with sparse embeddings |
| **Tool Protocol** | MCP (SSE transport) | Agent Builder ↔ MCP server communication |
| **Vault Access** | Python + python-frontmatter | Direct filesystem CRUD with YAML frontmatter |
| **Artemis Integration** | httpx (async) | Task management, daily plans, analytics, pomodoro |
| **Voice Input** | OpenAI Whisper API | Speech-to-text transcription |
| **Voice Output** | OpenAI TTS API | Text-to-speech response |
| **Indexer** | elasticsearch[async] + watchdog | Bulk sync + live file watching |
| **Infrastructure** | Docker + Docker Compose | Orchestration with vault volume mounting |

### Key Design Patterns

| Pattern | Description |
|---------|-------------|
| **3-Tool Vault Consolidation** | `vault_query`, `vault_read`, `vault_manage` with operation parameters — fewer tools, better LLM tool selection |
| **Adapter Pattern** | `artemis_client.py`, `es_client.py`, `vault_manager.py` each wrap an external system into a clean interface |
| **Checksum Deduplication** | MD5 of file content — skip re-indexing unchanged notes |
| **Confirm Destructive** | Delete operations require explicit `confirm_destructive=true` — no accidental data loss |
| **Voice as I/O Layer** | Agent never knows if input was typed or spoken — zero backend changes for voice |

---

## Quick Start

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | [python.org](https://www.python.org/downloads/) |
| uv | Latest | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| Docker | 20.10+ | [Install Docker](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.0+ | Included with Docker Desktop |

**Accounts Required:**
- [Elastic Cloud](https://cloud.elastic.co/registration?cta=hackathon) (free 14-day trial) — Elasticsearch Serverless + Agent Builder
- [OpenAI](https://platform.openai.com) (pay-as-you-go) — Whisper STT + TTS (voice only)
- [Artemis](https://github.com/StratosL/Artemis) running locally — task management backend

### Setup

```bash
# 1. Clone and configure
git clone https://github.com/StratosL/Athena.git
cd Athena
cp .env.example .env
# Edit .env with your Elastic Cloud and OpenAI credentials

# 2. Install indexer dependencies
cd indexer && uv sync && cd ..

# 3. Index your Obsidian vault (or use the sample vault)
VAULT_PATH=./sample-vault uv run --project indexer athena-index setup-indices
VAULT_PATH=./sample-vault uv run --project indexer athena-index index

# 4. Start the MCP server
docker compose up --build

# 5. Configure Agent Builder in Kibana
# See agent-config/setup-guide.md for step-by-step instructions
```

### Verify

```bash
# Check MCP server is running
curl http://localhost:8001/health

# Check Artemis connectivity
curl http://localhost:8000/health

# Verify indexed notes
curl -s "$ELASTIC_URL/athena-notes/_count" \
  -H "Authorization: ApiKey $ELASTIC_API_KEY"
```

---

## Project Structure

```
Athena/
├── indexer/                  # Obsidian -> Elasticsearch sync (CLI)
│   └── src/
│       ├── config.py         # ES credentials, vault path, index names
│       ├── mappings.py       # Index mapping definitions (semantic_text + ELSER)
│       ├── parser.py         # .md file -> dict (frontmatter + content + checksum)
│       ├── indexer.py        # Bulk index parsed documents into Elasticsearch
│       ├── watcher.py        # watchdog file watcher for live sync
│       └── cli.py            # CLI: setup-indices, index, watch
│
├── mcp-server/               # Unified MCP server
│   └── src/
│       ├── config.py         # Vault path, Artemis URL, ES credentials
│       ├── server.py         # MCP server setup + SSE transport
│       ├── vault_manager.py  # Obsidian vault filesystem CRUD
│       ├── artemis_client.py # httpx wrapper for Artemis REST API
│       ├── es_client.py      # Elasticsearch knowledge write-back
│       └── tools/
│           ├── vault.py      # 3 vault tools (query, read, manage)
│           ├── artemis.py    # 7 Artemis tools
│           ├── knowledge.py  # Conversation summary persistence
│           └── research.py   # Web search + URL fetch
│
├── voice-client/             # Thin voice-enabled web client
│   ├── index.html            # Single-page app with mic/speaker controls
│   ├── voice.js              # Whisper STT + OpenAI TTS integration
│   └── style.css             # Minimal styling
│
├── agent-config/             # Agent Builder configuration
│   ├── system-prompt.md      # Athena persona and behavioral rules
│   ├── setup-guide.md        # Kibana configuration walkthrough
│   └── tools/                # ES|QL tool definitions
│
├── sample-vault/             # Demo Obsidian vault (17 notes, 5 folders)
│   ├── Research/              # 3 notes — ES semantic search, API versioning, JWT
│   ├── Ideas/                 # 3 notes — onboarding, AI prioritization, voice
│   ├── Projects/              # 4 notes — DB migration, auth, roadmap, API refactor
│   ├── Meeting Notes/         # 3 notes — planning, sprint review, standup
│   └── Daily Notes/           # 4 notes — journals with pomodoro logs, priorities
│
├── docker-compose.yml        # MCP server + optional Artemis
├── PRD.md                    # Product Requirements Document
├── DEVLOG.md                 # Development log
└── CLAUDE.md                 # AI coding assistant instructions
```

---

## Tool Reference

### ES|QL Tools (Agent Builder — read-only)

| Tool | Purpose |
|------|---------|
| `search_notes` | Semantic + full-text search across indexed notes |
| `get_recent_notes` | Recently modified notes by time window |
| `get_notes_by_tag` | Filter notes by tag |
| `get_conversation_history` | Recall past conversation summaries |
| `count_notes_by_tag` | Tag distribution statistics |

### MCP Tools — Vault (direct filesystem)

| Tool | Operations |
|------|-----------|
| `vault_query` | `list_structure`, `search_content`, `search_by_metadata`, `recent_changes` |
| `vault_read` | `read_note`, `read_multiple`, `daily_note` |
| `vault_manage` | `create_note`, `append_note`, `edit_note`, `move_note`, `delete_note`, `create_folder` |

### MCP Tools — Artemis

| Tool | Purpose |
|------|---------|
| `artemis_create_task` | Create task with Eisenhower quadrant |
| `artemis_list_tasks` | List tasks filtered by quadrant/status |
| `artemis_complete_task` | Mark task as completed |
| `artemis_get_daily_plan` | Get today's 1-3-5 plan |
| `artemis_assign_to_plan` | Assign task to major/medium/small slot |
| `artemis_get_analytics` | Productivity summary for day/week/month |
| `artemis_start_pomodoro` | Start a focus session |

### MCP Tools — Knowledge & Research

| Tool | Purpose |
|------|---------|
| `save_conversation_summary` | Persist conversation context to Elasticsearch |
| `web_search` | Search the web via Tavily/Brave API |
| `fetch_url` | Fetch and extract text content from a URL |

---

## Development

### Running Locally (without Docker)

```bash
# MCP server
cd mcp-server && uv sync
uv run python -m src.server

# Indexer
cd indexer && uv sync
uv run athena-index --help
```

### Code Quality

```bash
# Lint and format (both sub-projects use ruff)
cd indexer && uv run ruff check . && uv run ruff format .
cd mcp-server && uv run ruff check . && uv run ruff format .

# Tests
cd indexer && uv run pytest
cd mcp-server && uv run pytest
```

### Configuration

All configuration via environment variables (see `.env.example`):

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `ELASTIC_URL` | Yes | — | Elasticsearch endpoint URL |
| `ELASTIC_API_KEY` | Yes | — | Elasticsearch API key |
| `VAULT_PATH` | Yes | `/vault` | Path to Obsidian vault |
| `ARTEMIS_BASE_URL` | Yes | `http://localhost:8000` | Artemis backend URL |
| `MCP_SERVER_PORT` | No | `8001` | MCP server port |
| `OPENAI_API_KEY` | For voice | — | Whisper STT + TTS |
| `TAVILY_API_KEY` | For research | — | Web search API |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

---

## Documentation

| Resource | Description |
|----------|-------------|
| **[PRD.md](PRD.md)** | Full product requirements — architecture, tools, APIs, phases |
| **[DEVLOG.md](DEVLOG.md)** | Development log with decisions and progress |
| **[CLAUDE.md](CLAUDE.md)** | AI coding assistant instructions and conventions |
| **[Agent Setup Guide](agent-config/setup-guide.md)** | Configuring Athena in Kibana Agent Builder |
| **[System Prompt](agent-config/system-prompt.md)** | Athena persona and behavioral rules |

---

## Roadmap

### In Progress — MVP

- [x] Project scaffold and configuration
- [x] Elasticsearch Serverless setup (ELSER + indices)
- [x] Indexer: parse, index, and sync Obsidian vault
- [x] Sample vault with 17 demo notes (validated end-to-end)
- [ ] MCP server with Artemis tools
- [ ] VaultManager with direct vault CRUD
- [ ] Vault MCP tools (query, read, manage)
- [ ] Agent Builder configuration (system prompt + ES|QL tools)
- [ ] Knowledge write-back (conversation memory)
- [ ] Research tools (web search + URL fetch)
- [ ] Voice client (Whisper STT + OpenAI TTS)
- [ ] Demo video and hackathon submission

### Future Enhancements

- [ ] Custom chat UI embedded in Artemis dashboard
- [ ] Real-time WebSocket updates when agent creates tasks
- [ ] Elastic Workflows automation (note watcher, daily planning assistant)
- [ ] Weekly productivity review generation
- [ ] Backlink analysis and Obsidian graph traversal
- [ ] OpenAI Realtime API for full-duplex voice
- [ ] Multi-vault support
- [ ] Calendar integration for daily planning context

---

## Hackathon

**Event:** [Elasticsearch Agent Builder Hackathon](https://elasticsearch.devpost.com/)
**Deadline:** February 27, 2026, 1:00 PM EST
**Prize Pool:** $20,000 ($10K / $5K / $3K + 4x$500 Creative Awards)
**Judging:** Technical Execution (30%), Impact & Wow Factor (30%), Demo (30%), Social (10%)

---

## Acknowledgments

**Athena** is a solo hackathon project created by **Stratos Louvaris**.

**Powered by:**
- [Elastic Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/elastic-agent-builder) — AI agent orchestration
- [Elasticsearch Serverless](https://www.elastic.co/elasticsearch/serverless) — Semantic search with ELSER
- [Artemis](https://github.com/StratosL/Artemis) — Sustainable productivity tool
- [Obsidian](https://obsidian.md/) — Knowledge management
- [OpenAI Whisper & TTS](https://platform.openai.com) — Voice interaction
- [Claude Code](https://claude.ai/claude-code) — AI-assisted development

**Inspired by:**
- [obsidian-ai-agent](https://github.com/paddyobrien/obsidian-ai-agent) — VaultManager pattern, 3-tool consolidation
- [hierarchical-rag](https://github.com/example/hierarchical-rag) — Dual hierarchy chunking strategy

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with purpose by Stratos Louvaris**

**Built for the Elasticsearch Agent Builder Hackathon 2026**

[Documentation](PRD.md) · [Development Log](DEVLOG.md) · [Report Issue](https://github.com/StratosL/Athena/issues)

</div>
