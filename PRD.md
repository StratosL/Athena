# Athena: Second Brain Orchestrator Agent — Product Requirements Document

---

## 1. Executive Summary

Athena is a conversational AI agent that serves as the intelligent bridge between a personal knowledge vault (Obsidian) and a productivity execution system (Artemis). It lives inside Elastic Agent Builder and orchestrates across Elasticsearch, a local Obsidian vault, and the Artemis REST API — reading your notes, writing new ones, extracting tasks, planning your day, and reporting on your productivity, all through natural conversation.

What makes Athena different from a generic assistant is its **dual-path knowledge access**: Elasticsearch provides semantic search and analytics across your entire vault, while direct filesystem access gives real-time read/write capability to individual notes. The agent doesn't just search your notes — it lives in your vault, creating new notes, appending to your daily journal, and organizing your knowledge as you work.

Athena also supports **voice interaction** as a first-class input/output mode via an embedded chat sidebar in the Artemis React dashboard. You can talk to your second brain and hear it respond, making it feel like a true intellectual companion rather than a chat window.

Beyond the core orchestration, Athena includes a **persistent memory system** (user profile + agent memory injected into every conversation), a **proactive heartbeat service** that periodically checks on overdue tasks and deadlines, and a **vault-based skills system** for reusable multi-step workflows like morning routines and weekly reviews.

**MVP Goal**: A working orchestrator agent on Elastic Agent Builder that can search an indexed Obsidian vault semantically, read/write notes directly, extract and classify tasks into Artemis with user confirmation, plan daily work using the 1-3-5 rule, remember past conversations, execute reusable workflows, and interact via voice — submitted as a hackathon entry by February 27, 2026.

---

## 2. Mission

**Mission Statement**: Athena turns scattered knowledge into focused action through intelligent, conversational orchestration — with full bidirectional access to your second brain.

**Core Principles:**

1. **Human-in-the-loop**: Never take action without discussing it first. The agent proposes, the user decides, then the agent acts.
2. **Bidirectional vault access**: Read from the vault, write insights back to it. The vault is a living workspace, not a read-only archive.
3. **Dual-path intelligence**: Elasticsearch for semantic understanding and analytics; direct vault access for real-time accuracy and writes.
4. **Intelligence over automation**: Understand context, classify priorities, and adapt to feedback — don't just move data between systems.
5. **Hackathon-pragmatic**: Ship a compelling demo over building a perfect system. Every decision optimizes for a working end-to-end flow by Feb 27.

---

## 3. Target Users

### Primary Persona: Knowledge Worker (Solo Developer / Creator)

- **Profile**: Stratos — solo developer who captures ideas, meeting notes, project plans, and research in Obsidian but struggles to convert them into actionable work
- **Technical comfort**: High — comfortable with CLI tools, APIs, Docker, Python
- **Pain points**:
  - Notes contain buried action items that never become tasks
  - Context switching between "thinking tools" (Obsidian) and "doing tools" (Artemis) causes ideas to fall through cracks
  - Manual task creation is tedious — extracting, classifying, and prioritizing from notes is cognitive overhead
  - No way to ask "what should I work on today?" and get an answer grounded in actual notes and commitments
  - Writing notes during brainstorming sessions interrupts flow — wants to dictate ideas and have them captured
- **Key needs**:
  - A single conversational interface (text or voice) to discuss work, research, and planning
  - Intelligent task extraction that understands priority and effort
  - Daily planning that accounts for existing commitments and deadlines
  - An agent that can create, edit, and organize vault notes on your behalf
  - Persistent memory — the agent should remember past conversations and decisions

---

## 4. MVP Scope

### In Scope (MVP)

**Core Orchestration:**
- ✅ Conversational AI agent with "Athena" persona via Elastic Agent Builder
- ✅ Search indexed Obsidian notes using semantic and full-text search (Elasticsearch)
- ✅ Direct vault read/write access via MCP tools (real-time, no sync delay)
- ✅ Extract actionable tasks from notes through conversation
- ✅ Classify tasks using Eisenhower Matrix (Q1-Q4)
- ✅ Interactive confirmation — agent presents tasks before creating them
- ✅ Create tasks in Artemis via MCP tools
- ✅ Daily planning using 1-3-5 rule (1 major, 3 medium, 5 small)
- ✅ Productivity analytics narration from Artemis data

**Knowledge Management:**
- ✅ Index Obsidian vault (Markdown + YAML frontmatter) into Elasticsearch
- ✅ Read individual notes directly from vault (real-time, with frontmatter)
- ✅ Create new notes in vault (ideas, brainstorms, research summaries)
- ✅ Append to existing notes (daily journals, running logs)
- ✅ Query vault structure (list folders, recent changes, metadata search)
- ✅ Save conversation summaries to Elasticsearch for long-term memory

**Voice Interface:**
- ✅ Speech-to-text input via OpenAI Whisper API
- ✅ Text-to-speech output via OpenAI TTS API
- ✅ Toggle between voice and text modes
- ✅ Microphone capture via browser MediaRecorder API

**Infrastructure:**
- ✅ Elasticsearch Cloud Serverless (2 indices: notes, conversations)
- ✅ Single unified MCP server (Vault + Artemis + Knowledge + Research + Skills tools)
- ✅ Docker volume mounting for vault filesystem access
- ✅ Sample Obsidian vault with 23 demo notes across 7 folders
- ✅ Embedded chat sidebar in Artemis React dashboard with voice support
- ✅ Agent Builder chat UI as secondary interface
- ✅ Monorepo — Artemis backend + frontend merged into single repository

**Research:**
- ✅ Web search capability (Brave Search free tier)
- ✅ URL fetching and content extraction

**Memory & Proactivity:**
- ✅ Persistent user profile and agent memory injected into every conversation
- ✅ Conversation summaries saved to Elasticsearch and daily notes
- ✅ Proactive heartbeat service — periodic check-ins for overdue tasks and deadlines
- ✅ Chat conversation persistence across page refresh (localStorage)

**Skills:**
- ✅ Vault-based runtime skills — reusable multi-step workflows (morning routine, meeting debrief, weekly review)
- ✅ Skill CRUD via MCP tool (list, load, create, edit, delete)

**Developer Experience:**
- ✅ One-command setup automation (`./setup.sh`) — env validation, DB migration, ES indexing, Agent Builder API
- ✅ SQL migration for Supabase schema

### Out of Scope (Post-MVP / Future)

**Deferred:**
- ❌ Multi-user / authentication
- ❌ Elastic Workflows automation (note watcher, daily planning assistant)
- ❌ Wake word detection ("Hey Athena")
- ❌ OpenAI Realtime API (full-duplex voice)
- ❌ Streaming TTS (progressive audio playback)
- ❌ Mobile app integration
- ❌ Sync with cloud-hosted Obsidian vaults (iCloud, Sync)
- ❌ Integration with external tools (Slack, email, calendar)
- ❌ Fine-tuned embeddings model
- ❌ Bulk vault operations (bulk tag, bulk move, bulk metadata updates)
- ❌ Backlink analysis and graph traversal

---

## 5. User Stories

### Primary User Stories

**US-1: Knowledge Search (Semantic)**
> As a knowledge worker, I want to ask Athena about topics in my notes, so that I can quickly find relevant information without manually searching through files.

*Example*: "What did I write about the API refactoring project?" → Athena searches Elasticsearch with ELSER embeddings, returns relevant notes with excerpts and source paths.

**US-2: Direct Note Reading**
> As a knowledge worker, I want Athena to read and quote specific notes from my vault, so that I get the exact current content without sync delays.

*Example*: "Read my note on the Q1 roadmap" → Athena reads the file directly from the vault, returns full content with frontmatter metadata.

**US-3: Task Extraction**
> As a knowledge worker, I want Athena to identify actionable tasks from my notes, so that buried action items become visible and trackable.

*Example*: "Extract tasks from my sprint review notes" → Athena reads the note from vault, identifies 5 action items, presents them with suggested Eisenhower quadrants, and waits for confirmation before creating them in Artemis.

**US-4: Interactive Task Creation**
> As a knowledge worker, I want to discuss and adjust proposed tasks before they're created, so that I maintain control over what enters my execution system.

*Example*: Athena proposes 5 tasks. User says "Skip #2, and make #4 urgent instead of important." Athena adjusts and creates only the approved tasks.

**US-5: Daily Planning**
> As a knowledge worker, I want Athena to help me plan my day using the 1-3-5 rule, so that I focus on the right work each morning.

*Example*: "Plan my day" → Athena checks pending tasks in Artemis, considers deadlines and priorities, suggests a plan (1 major + 3 medium + 5 small), user confirms, tasks are assigned to today's plan.

**US-6: Idea Capture via Voice**
> As a knowledge worker, I want to dictate an idea to Athena and have it saved as a note in my vault, so that no insight is lost during a flow state.

*Example*: User speaks: "I just thought of a way to improve the onboarding flow — use progressive disclosure instead of a wizard" → Athena transcribes, creates a new note in the vault tagged `#idea`, `#onboarding`, `#ux`, and indexes it in Elasticsearch.

**US-7: Research Partner**
> As a knowledge worker, I want to research topics with Athena and have findings saved to my knowledge base, so that research becomes part of my permanent second brain.

*Example*: "Research best practices for API versioning" → Athena searches the web, summarizes findings, and offers to save the summary as a note in the vault.

**US-8: Productivity Check-in**
> As a knowledge worker, I want to ask Athena how I'm doing, so that I get meaningful insights about my productivity trends.

*Example*: "How was my week?" → Athena pulls analytics from Artemis (tasks completed, pomodoros, completion rate) and interprets them: "You completed 12 tasks this week, up from 8 last week. Your focus time increased by 2 hours. Q2 tasks are being neglected though — 0 completed."

**US-9: Conversation Memory**
> As a knowledge worker, I want Athena to remember past conversations, so that I don't have to repeat context.

*Example*: "What did we discuss about the API project last time?" → Athena queries the conversations index and provides a summary.

**US-10: Voice Conversation**
> As a knowledge worker, I want to talk to Athena with my voice and hear responses spoken back, so that I can interact hands-free while thinking or working.

*Example*: User clicks microphone → speaks "What's on my plan for today?" → Athena responds with audio: "You have one major task: finish the authentication module. Three medium tasks: review the PR, update the docs, and fix the login bug. And five small tasks..."

---

## 6. Core Architecture & Patterns

### High-Level Architecture

```
User ←→ Artemis Dashboard (React + Chat Sidebar)
              ↓ Voice Proxy (STT/TTS)
         Agent Builder (Athena) ←→ Elasticsearch
              ↓ MCP Protocol (Streamable HTTP)       ↑ ES|QL
         Athena MCP Server                            |
           ├── Vault tools     → Obsidian Vault       |
           ├── Artemis tools   → Artemis REST API     |
           ├── Knowledge tools → Elasticsearch         |
           ├── Research tools  → Web search + URL      |
           └── Skills tools    → Vault workflows       |
                                                       |
         Indexer CLI ──── Obsidian Vault → ES ─────────┘
         Heartbeat Service ──→ Converse API ──→ Daily Notes
```

### Dual-Path Knowledge Access

| Path | Technology | Purpose | Latency |
|------|-----------|---------|---------|
| **Semantic Search** | Elasticsearch + ELSER | Find notes by meaning, aggregations, cross-note patterns | Seconds (sync delay) |
| **Direct Vault Access** | Filesystem via MCP | Read/write notes in real-time, list structure, metadata queries | Instant |

These two paths complement each other. Elasticsearch is the analytical brain (semantic search, aggregations, trend analysis). Direct vault access is the hands (read what's there right now, write new things, append to journals).

### Voice I/O Layer

```
┌─────────────────────────────────────────────┐
│                Voice Layer                   │
│                                              │
│  [Mic] → MediaRecorder → Whisper API → text  │
│                                              │
│  text → Agent Builder → response text        │
│                                              │
│  response text → OpenAI TTS API → [Speaker]  │
└─────────────────────────────────────────────┘
```

Voice sits entirely in the client layer. The agent never knows if input came from typing or speech. This means zero changes to the orchestrator, MCP server, or tools — voice is a pure presentation concern.

### Architecture Style: Simple Modular

Not VSA. Athena's 8 sub-projects don't map to VSA's routes/service/repository pattern. We borrow good ideas — centralized config, separation of concerns, one file = one job — without the layered ceremony.

### Directory Structure

```
/home/stardust/Athena/
├── .claude/                        # Claude Code configuration
│   ├── commands/                   # Slash commands (commit, ship, validate, etc.)
│   └── skills/                     # Developer skills (customize, add-integration, etc.)
├── .gitignore
├── .env.example
├── docker-compose.yml              # 6 services: artemis, mcp-server, voice-proxy, frontend, heartbeat, ngrok
├── nginx.conf                      # Frontend reverse proxy + /athena → voice-proxy
├── setup.sh                        # One-command project bootstrap
├── README.md
├── LICENSE (MIT)
├── PRD.md
├── DEVLOG.md
│
├── services/
│   └── artemis-backend/            # Artemis FastAPI backend (merged from Artemis repo)
│       ├── pyproject.toml
│       └── src/                    # FastAPI app, Supabase client, routes, models
│
├── frontend/                       # Artemis React frontend (merged from Artemis repo)
│   ├── package.json
│   ├── Dockerfile
│   └── src/
│       ├── App.tsx                 # Routes: dashboard, tasks, plan, pomodoro, analytics
│       ├── design-system/          # Glassmorphism component library
│       ├── hooks/                  # useAthenaChat, useAthenaVoice, useTasks, etc.
│       ├── stores/                 # chatStore (persistent), timerStore
│       ├── lib/                    # api.ts, athena-api.ts
│       └── pages-new/             # Dashboard, Tasks, DailyPlan, Pomodoro, Analytics, Settings
│
├── indexer/                        # Obsidian → Elasticsearch sync
│   ├── pyproject.toml
│   └── src/
│       ├── config.py               # ES URL, API key, vault path, index names
│       ├── mappings.py             # Elasticsearch index mapping definitions
│       ├── parser.py               # .md file → dict (frontmatter + content + checksum)
│       ├── indexer.py              # Bulk index parsed documents into Elasticsearch
│       ├── watcher.py              # watchdog file watcher for live sync
│       └── cli.py                  # CLI entry points: index, watch, setup-indices
│
├── mcp-server/                     # Unified MCP server (Streamable HTTP transport)
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── src/
│       ├── config.py               # Vault path, Artemis URL, ES URL, API keys
│       ├── server.py               # FastMCP setup, adapter init, tool registration
│       ├── __main__.py             # Entry point (avoids double-import)
│       ├── artemis_client.py       # httpx wrapper for Artemis REST API
│       ├── es_client.py            # Elasticsearch client for knowledge write-back
│       ├── vault_manager.py        # Obsidian vault filesystem access (read/write/query)
│       └── tools/
│           ├── vault.py            # 3 vault MCP tools (query, read, manage)
│           ├── artemis.py          # 7 Artemis MCP tools
│           ├── knowledge.py        # 1 knowledge write-back tool (ES + daily note)
│           ├── research.py         # 2 research tools (web search, URL fetch)
│           └── skills.py           # 1 skills tool (5 operations: list, load, create, edit, delete)
│
├── voice-client/                   # Voice proxy server + static voice UI
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── serve.py                    # aiohttp server: /api/chat, /api/transcribe, /api/speak
│   ├── index.html                  # Standalone voice interface (fallback)
│   ├── voice.js                    # Whisper STT + OpenAI TTS integration
│   └── style.css
│
├── heartbeat/                      # Proactive agent check-in service
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── src/
│       ├── config.py               # HeartbeatSettings (interval, active hours)
│       ├── heartbeat.py            # APScheduler + converse API + daily note alerts
│       └── __main__.py
│
├── scripts/                        # Setup automation
│   ├── pyproject.toml
│   ├── config.py                   # Shared SetupConfig
│   ├── validate_env.py             # Credential + connectivity checks
│   ├── setup_supabase.py           # Postgres DDL execution
│   ├── setup_elasticsearch.py      # ES indices + vault indexing
│   ├── setup_agent_builder.py      # Kibana API: tools + connector + agent
│   ├── verify.py                   # End-to-end health check
│   └── setup.py                    # Main orchestrator with --phase CLI
│
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql  # Tasks, daily_plans, pomodoro_sessions tables
│
├── agent-config/                   # Agent Builder configuration (tracked in git)
│   ├── system-prompt.md            # Athena persona (281 lines — workflows, guardrails, memory)
│   ├── setup-guide.md              # How to configure in Kibana
│   └── tools/                      # ES|QL tool definitions (JSON exports)
│
├── sample-vault/                   # Demo Obsidian vault (23 notes, 7 folders)
│   ├── Projects/
│   ├── Ideas/
│   ├── Meeting Notes/
│   ├── Daily Notes/
│   ├── Research/
│   ├── Learning/
│   └── Meta/                       # user-profile.md, memory.md, heartbeat.md, Skills/
│
├── decisions/                      # Architecture Decision Records
│   ├── 001-tunnel-ngrok-over-alternatives.md
│   ├── 002-single-agent-over-sub-agents.md
│   ├── 003-openclaw-patterns-research.md
│   └── 004-monorepo-merge-strategy.md
│
├── docs/
│
└── devpost/
    └── screenshots/
```

### Key Design Patterns

1. **VaultManager Pattern**: Centralized filesystem access class (inspired by obsidian-ai-agent) with path validation, directory traversal prevention, frontmatter parsing, and all CRUD operations. All vault tools delegate to this single class.
2. **Adapter Pattern**: `artemis_client.py`, `es_client.py`, and `vault_manager.py` each adapt an external system into a clean internal interface that MCP tools consume.
3. **3-Tool Consolidation**: Vault access uses three tools with operation parameters rather than many single-purpose tools — following Anthropic's "fewer tools, more parameters" best practice.
4. **Configuration via Environment**: All secrets and URLs in `.env`, loaded via `pydantic-settings` with `extra: "ignore"` so each sub-project ignores vars it doesn't need.
5. **Checksum-based Deduplication**: Indexer computes MD5 checksums to skip re-indexing unchanged files. SHA-256 of vault-relative path used as deterministic ES `_id`.
6. **Confirm Destructive**: Vault write/delete operations require explicit confirmation parameter to prevent accidental data loss.
7. **Memory Injection**: User profile and agent memory files from the vault are injected into every conversation via `configuration_overrides.systemPromptAddition` in the converse API.
8. **Heartbeat Suppression**: Proactive check-ins return `HEARTBEAT_OK` when nothing needs attention — silently discarded (no alert). Real alerts are appended to the daily note.
9. **Vault-based Skills**: Reusable multi-step workflows stored as Markdown in `Meta/Skills/`, loaded and executed by the agent at runtime via MCP tool.

---

## 7. Tools / Features

### ES|QL Tools (Read-only, configured in Agent Builder)

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `search_notes` | `query` (str), `tag_filter` (str?), `limit` (int=5) | Semantic + full-text search across notes |
| `get_recent_notes` | `days` (int=7), `limit` (int=10) | Recently modified notes |
| `get_notes_by_tag` | `tag` (str) | All notes with a specific tag |
| `get_conversation_history` | `topic` (str?), `limit` (int=5) | Past conversation summaries |
| `count_notes_by_tag` | none | Tag distribution statistics |

Plus **built-in search tool** on `athena-notes` index for semantic/hybrid search (configured in Agent Builder UI).

### MCP Tools — Vault Group (Direct Filesystem Access)

**`vault_query`** — Discovery and search across the vault

| Operation | Parameters | Purpose |
|-----------|-----------|---------|
| `list_structure` | `folder` (str?), `recursive` (bool=false) | Browse vault folder structure |
| `search_content` | `query` (str), `limit` (int=10) | Keyword search across note content and titles |
| `search_by_metadata` | `tags` (str[]?), `folder` (str?), `date_range_days` (int?) | Filter by tags, folder, date range |
| `recent_changes` | `limit` (int=10) | Most recently modified notes |

**`vault_read`** — Read full note content with context

| Operation | Parameters | Purpose |
|-----------|-----------|---------|
| `read_note` | `path` (str) | Read a single note with frontmatter |
| `read_multiple` | `paths` (str[]) | Read several notes at once |
| `daily_note` | `date` (str?) | Read today's (or specified date's) daily note |

**`vault_manage`** — Create, edit, and organize notes

| Operation | Parameters | Purpose |
|-----------|-----------|---------|
| `create_note` | `path` (str), `content` (str), `tags` (str[]?), `metadata` (dict?) | Create a new note with optional frontmatter |
| `append_note` | `path` (str), `content` (str) | Append to an existing note (preserves frontmatter) |
| `edit_note` | `path` (str), `old_text` (str), `new_text` (str) | Surgical str_replace edit within a note |
| `create_folder` | `path` (str) | Create a new folder in the vault |
| `move_note` | `source` (str), `destination` (str) | Move a note to a different location |
| `delete_note` | `path` (str), `confirm_destructive` (bool) | Delete a note (requires confirmation flag) |

### MCP Tools — Artemis Group

| Tool | Artemis Endpoint | Parameters |
|------|-----------------|------------|
| `artemis_create_task` | `POST /tasks` | `title`, `quadrant` (1-4), `description?`, `due_date?` |
| `artemis_list_tasks` | `GET /tasks` | `quadrant?`, `status?` (pending/in_progress/completed) |
| `artemis_complete_task` | `POST /tasks/{id}/complete` | `task_id` |
| `artemis_get_daily_plan` | `GET /daily-plans/today` | none (auto-creates if missing) |
| `artemis_assign_to_plan` | `POST /daily-plans/{plan_id}/tasks` | `plan_id`, `task_id`, `slot` (major/medium/small) |
| `artemis_get_analytics` | `GET /analytics/summary` | `period` (day/week/month) |
| `artemis_start_pomodoro` | `POST /pomodoro/start` | `task_id?`, `duration_minutes?` |

### MCP Tools — Knowledge Group

| Tool | Purpose | Writes To |
|------|---------|-----------|
| `save_conversation_summary` | Persist conversation context for future recall | `athena-conversations` index + daily note in vault |

Conversation summaries are dual-written: indexed in Elasticsearch for semantic search, and appended to the day's daily note for vault continuity.

### MCP Tools — Research Group

| Tool | Purpose |
|------|---------|
| `web_search` | Search the web via Brave API, return top results with snippets |
| `fetch_url` | Fetch a URL, extract text content via html2text, return summary |

### MCP Tools — Skills Group

**`skill_manager`** — Discover, load, and manage reusable multi-step workflows stored in `Meta/Skills/`

| Operation | Parameters | Purpose |
|-----------|-----------|---------|
| `list_skills` | none | List all available skills with names and trigger phrases |
| `load_skill` | `name` (str) | Load a skill's full steps and instructions |
| `create_skill` | `name` (str), `content` (str) | Create a new skill from conversation (requires confirmation) |
| `edit_skill` | `name` (str), `content` (str) | Update an existing skill's content |
| `delete_skill` | `name` (str), `confirm_destructive` (bool) | Delete a skill (requires confirmation flag) |

### Tool Priority

All priorities below have been implemented and validated.

| Priority | Tools | Rationale |
|----------|-------|-----------|
| **P0 — Demo-critical** | `search_notes`, `vault_read`, `vault_manage` (create, append), `artemis_create_task`, `artemis_list_tasks`, `artemis_get_daily_plan`, `artemis_assign_to_plan`, `save_conversation_summary` | Core demo flow: search → read → extract → create → plan |
| **P1 — Full experience** | `vault_query`, `vault_manage` (edit, move, delete), `artemis_complete_task`, `artemis_get_analytics`, `artemis_start_pomodoro`, `get_recent_notes`, `get_notes_by_tag`, `skill_manager` | Complete vault management + productivity tracking + workflows |
| **P2 — Nice-to-have** | `web_search`, `fetch_url`, `count_notes_by_tag`, `get_conversation_history` | Research capability + analytics |
| **P3 — Voice** | Whisper STT, OpenAI TTS, embedded chat sidebar with voice mode | Voice I/O layer (independent of backend) |

---

## 8. Technology Stack

### Agent Layer

| Technology | Version | Purpose |
|-----------|---------|---------|
| Elastic Agent Builder | GA (Jan 2026) | Orchestrator — system prompt, tool routing, conversation management |
| Elasticsearch Serverless | Latest | Knowledge store — search, indexing, semantic embeddings |
| LLM Connector | OpenAI GPT-4o or Anthropic Claude | Agent reasoning via Agent Builder |

### Indexer (`indexer/`)

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Runtime |
| `uv` | Latest | Project management, dependency resolution |
| `elasticsearch[async]` | >=8.17.0 | Elasticsearch client for bulk indexing |
| `python-frontmatter` | Latest | Parse Obsidian YAML frontmatter from .md files |
| `watchdog` | Latest | Filesystem watcher for live vault sync |
| `pydantic-settings` | Latest | Configuration management |

### MCP Server (`mcp-server/`)

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Runtime |
| `uv` | Latest | Project management |
| `mcp[cli]` | >=1.3.0 | MCP protocol server implementation (Streamable HTTP transport) |
| `httpx` | >=0.27.0 | Async HTTP client for Artemis REST API |
| `elasticsearch[async]` | >=8.17.0 | ES client for knowledge write-back |
| `python-frontmatter` | >=1.1.0 | Parse/write YAML frontmatter in vault notes |
| `pydantic` | >=2.7.0 | Data validation for tool inputs/outputs |
| `pydantic-settings` | >=2.5.0 | Configuration management |
| `html2text` | Latest | URL content extraction (research tools) |

### Voice Proxy (`voice-client/`)

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Runtime |
| `aiohttp` | Latest | HTTP server proxying to Kibana converse API |
| `python-frontmatter` | Latest | Parse memory files for injection |
| OpenAI Whisper API | Latest | Speech-to-text transcription |
| OpenAI TTS API | Latest | Text-to-speech (voices: alloy, echo, fable, onyx, nova, shimmer) |
| HTML/JS/CSS | Vanilla | Standalone voice fallback UI |

### Artemis Frontend (`frontend/`)

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18.3 | UI framework |
| TypeScript | 5.5+ | Type-safe frontend |
| Vite | 5.4 | Build tool |
| Tailwind CSS | 3.4 | Utility-first styling |
| Zustand | 4.5 | State management (chat, timer) with localStorage persistence |
| TanStack Query | 5.0 | Server state, cache invalidation |
| React Router | 6.26 | Client-side routing |
| Motion | 12.34 | Animations |
| MediaRecorder API | Browser built-in | Audio capture from microphone |

### Heartbeat Service (`heartbeat/`)

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Runtime |
| APScheduler | 3.11 | Cron-based periodic scheduling |
| `httpx` | Latest | Calls Kibana converse API |
| `python-frontmatter` | Latest | Reads heartbeat checklist from vault |

### Artemis Backend (`services/artemis-backend/`)

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Runtime |
| FastAPI | Latest | REST API framework |
| Supabase (PostgreSQL) | Latest | Database for tasks, plans, pomodoro sessions |
| Pydantic | v2 | Request/response models |

### Infrastructure

| Technology | Purpose |
|-----------|---------|
| Docker + Docker Compose | Orchestrate 6 services: artemis, mcp-server, voice-proxy, frontend, heartbeat (opt-in), ngrok (opt-in) |
| ngrok | Expose local MCP server to Elastic Cloud via static domain (`sylas-saporific-ilona.ngrok-free.dev`) |
| nginx | Reverse proxy for frontend — SPA routing + `/athena` → voice-proxy |

---

## 9. Security & Configuration

### Configuration Management

All configuration via environment variables, loaded with `pydantic-settings`:

```env
# Elasticsearch
ELASTIC_URL=<serverless-endpoint-url>
ELASTIC_API_KEY=<api-key>

# Obsidian Vault
VAULT_PATH=/path/to/obsidian/vault

# Indexer
NOTES_INDEX=athena-notes
CONVERSATIONS_INDEX=athena-conversations

# MCP Server
ARTEMIS_BASE_URL=http://localhost:8000
MCP_SERVER_PORT=8001

# Supabase (Artemis backend)
SUPABASE_URL=<supabase-project-url>
SUPABASE_ANON_KEY=<supabase-anon-key>
SUPABASE_DB_URL=<postgres-connection-string>  # optional, for setup.sh SQL migration
CORS_ORIGINS=http://localhost:3000

# Voice (optional)
OPENAI_API_KEY=<key>

# Research (optional)
BRAVE_API_KEY=<key>
TAVILY_API_KEY=<key>

# ngrok tunnel (optional — for Elastic Cloud connectivity)
NGROK_AUTHTOKEN=<auth-token>
NGROK_DOMAIN=sylas-saporific-ilona.ngrok-free.dev

# Heartbeat (optional — proactive check-ins)
HEARTBEAT_INTERVAL_MINUTES=30
HEARTBEAT_ACTIVE_HOUR_START=8
HEARTBEAT_ACTIVE_HOUR_END=22

# Agent Builder
KIBANA_URL=<kibana-endpoint-url>
KIBANA_API_KEY=<kibana-api-key>
```

### Vault Security

- ✅ **Path validation**: All vault paths are resolved and validated to stay within the vault root directory
- ✅ **Directory traversal prevention**: Reject any path containing `..` or resolving outside vault root
- ✅ **Confirm destructive**: Delete operations require an explicit `confirm_destructive=true` parameter
- ✅ **Human-in-the-loop for writes**: Agent must describe what it will write and get user confirmation before creating or editing notes
- ✅ **Docker volume mount**: Vault access is scoped to a single mounted directory (`-v ${VAULT_PATH}:/vault:rw`)

### General Security

**In Scope:**
- ✅ API keys stored in `.env` (never committed)
- ✅ `.env.example` template with placeholder values
- ✅ `.gitignore` excludes `.env`, `__pycache__`, `.venv`
- ✅ Elasticsearch API key scoped to minimum required permissions
- ✅ Input validation on all MCP tool parameters via Pydantic

**Out of Scope (hackathon):**
- ❌ User authentication (single-user system)
- ❌ Rate limiting
- ❌ HTTPS for local MCP server (ngrok handles TLS)
- ❌ Audit logging

### Networking

```
Agent Builder (Elastic Cloud) → MCP Server: MCP Streamable HTTP (public URL via ngrok static domain)
MCP Server → Artemis Backend: HTTP to artemis:8000 (Docker network)
MCP Server → Elasticsearch: HTTPS to Elastic Cloud Serverless endpoint
MCP Server → Obsidian Vault: Filesystem via Docker volume mount (/vault:rw)
Voice Proxy → OpenAI API: HTTPS (Whisper STT + TTS)
Voice Proxy → Agent Builder: HTTPS (Kibana converse API)
Frontend → Voice Proxy: HTTP via nginx reverse proxy (/athena → voice-proxy:3001)
Frontend → Artemis Backend: HTTP to localhost:8000 (direct or via Vite dev proxy)
Heartbeat → Agent Builder: HTTPS (Kibana converse API, periodic)
Heartbeat → Obsidian Vault: Filesystem via Docker volume mount (alert write-back)
```

---

## 10. API Specification

### Artemis REST API (Existing — consumed by MCP server)

**Tasks:**

```
POST /tasks
Body: { "title": "str", "quadrant": 1-4, "description?": "str", "due_date?": "ISO datetime" }
Response: { "id", "title", "quadrant", "status", "pomodoro_count", "created_at", "updated_at" }

GET /tasks?quadrant=1&status=pending&limit=100&offset=0
Response: { "items": [TaskResponse], "total": int }

POST /tasks/{task_id}/complete
Response: TaskResponse (with status="completed", completed_at set)
```

**Daily Plans:**

```
GET /daily-plans/today
Response: { "id", "date", "major_task_id", "medium_task_ids[]", "small_task_ids[]",
            "major_task", "medium_tasks[]", "small_tasks[]",
            "completed", "completion_rate", "total_tasks", "completed_tasks" }

POST /daily-plans/{plan_id}/tasks
Body: { "task_id": "uuid", "slot": "major|medium|small" }
Response: DailyPlanResponse
```

**Analytics:**

```
GET /analytics/summary?period=week
Response: { "period", "start_date", "end_date",
            "total_pomodoros", "total_focus_minutes", "average_pomodoros_per_day",
            "tasks_created", "tasks_completed", "task_completion_rate",
            "daily_plan_stats": { "total_plans", "plans_completed", "avg_completion_rate" },
            "productivity_score": { "score" (0-100), "trend", "trend_percentage" } }
```

**Pomodoro:**

```
POST /pomodoro/start
Body: { "task_id?": "uuid", "duration_minutes?": 25 }
Response: { "id", "task_id", "started_at", "duration_minutes" }
```

### Elasticsearch Index APIs (Used by Indexer + MCP Server)

**Bulk Index (Indexer):**
```
POST athena-notes/_bulk
{ "index": { "_id": "<vault-relative-path-hash>" } }
{ "title": "...", "content": "...", "content_semantic": "...", "tags": [...], ... }
```

**Index Document (MCP Knowledge Tools):**
```
POST athena-conversations/_doc
{ "summary": "...", "topics": [...], "extracted_tasks": [...], "timestamp": "..." }
```

### Vault Filesystem API (Internal — VaultManager class)

```python
class VaultManager:
    def __init__(self, vault_path: str)
    def read_note(self, relative_path: str) -> Note
    def write_note(self, relative_path: str, content: str, metadata: dict | None) -> Note
    def append_to_note(self, relative_path: str, content: str) -> Note
    def edit_note(self, relative_path: str, old_text: str, new_text: str) -> Note
    def delete_note(self, relative_path: str, confirm_destructive: bool) -> bool
    def move_note(self, source: str, destination: str) -> Note
    def list_notes(self, folder: str | None, recursive: bool) -> list[NoteSummary]
    def search_content(self, query: str, limit: int) -> list[NoteSummary]
    def search_by_metadata(self, tags: list[str] | None, folder: str | None, date_range_days: int | None) -> list[NoteSummary]
    def get_recent_notes(self, limit: int) -> list[NoteSummary]
    def create_folder(self, relative_path: str) -> bool
```

### Voice API (External — OpenAI)

**Speech-to-Text:**
```
POST https://api.openai.com/v1/audio/transcriptions
Content-Type: multipart/form-data
Body: file=<audio_blob>, model="whisper-1"
Response: { "text": "transcribed text" }
```

**Text-to-Speech:**
```
POST https://api.openai.com/v1/audio/speech
Body: { "model": "tts-1", "voice": "nova", "input": "text to speak" }
Response: audio/mpeg stream
```

---

## 11. Success Criteria

### MVP Success Definition

A successful MVP demonstrates the complete knowledge-to-action loop in a 3-minute demo video, including at least one voice interaction, with all core tools working end-to-end.

### Functional Requirements

- ✅ User can ask Athena about topics in their notes and get relevant results (semantic search)
- ✅ Athena can read a specific note directly from the vault and quote its content
- ✅ Athena can create a new note in the vault with proper frontmatter
- ✅ Athena can append content to an existing note (daily journal use case)
- ✅ Athena can extract actionable tasks from a note and present them with Eisenhower classification
- ✅ Athena confirms with user before creating any task in Artemis
- ✅ User can adjust proposed tasks (change priority, skip items) before confirmation
- ✅ Created tasks appear in Artemis with correct quadrant and description
- ✅ Athena can build a 1-3-5 daily plan from existing pending tasks
- ✅ Athena can report on productivity using Artemis analytics
- ✅ Athena can save conversation summaries for future context
- ✅ Indexer can process 23 Obsidian notes with frontmatter into Elasticsearch
- ✅ Semantic search returns relevant results (not just keyword matches)
- ✅ User can speak to Athena and hear a voice response back
- ✅ Voice mode can be toggled on/off

### Quality Indicators

- Agent correctly classifies Eisenhower quadrants >80% of the time
- Agent never creates tasks or modifies notes without user confirmation
- Search returns relevant notes in the top 3 results
- End-to-end flow (search → read → extract → create → plan) completes without errors
- MCP tools handle Artemis or vault being unreachable gracefully (error message, not crash)
- Vault path validation blocks all directory traversal attempts
- Voice transcription accuracy >90% for clear English speech

### Demo Experience Goals

- "Wow moment #1": User speaks to Athena → tasks materialize in Artemis's Eisenhower Matrix
- "Wow moment #2": User says "save this as a note" → note appears in the Obsidian vault
- "Wow moment #3": Athena greets user by name and references their current projects (memory injection)
- "Wow moment #4": User says "run my morning routine" → agent executes multi-step skill automatically
- Smooth conversational flow — no awkward pauses, no tool errors visible
- Clear demonstration of bidirectional data flow (read notes + write notes + create tasks + save conversations)

---

## 12. Implementation Phases

### Phase 1: Foundation (Days 1-7) — COMPLETE

**Goal**: Get data flowing — vault indexed, agent searching, MCP server proxying to Artemis with vault access, deployed to Elastic Cloud.

**Deliverables:**
- ✅ Elastic Cloud Serverless trial active with LLM connector configured
- ✅ ELSER inference endpoint set up for semantic search
- ✅ `athena-notes` and `athena-conversations` indices created with mappings
- ✅ Indexer project: `parser.py`, `indexer.py`, `cli.py`, `mappings.py`, `config.py`, `watcher.py`
- ✅ Sample vault with 17 notes created and indexed (later expanded to 23)
- ✅ MCP server with 13 tools (3 vault + 7 Artemis + 1 knowledge + 2 research)
- ✅ VaultManager class with path validation, frontmatter parsing, all CRUD operations
- ✅ Agent Builder "Athena" agent with 281-line system prompt and 19 tools
- ✅ ES|QL tools: `search_notes`, `get_recent_notes`, `get_notes_by_tag`, `count_notes_by_tag`, `get_conversation_history` + `semantic_search`
- ✅ MCP server deployed via ngrok, registered in Agent Builder
- ✅ Docker volume mount for vault access configured
- ✅ Transport: Streamable HTTP (Elastic requirement, not SSE)
- ✅ pyright + ruff validation on all sub-projects

**Validation**: Agent responds in Kibana chat. Semantic search returns relevant results. Tasks created via agent appear in Artemis.

### Phase 2: Unified Experience + Intelligence (Days 8-13) — COMPLETE

**Goal**: Embed Athena in Artemis, add voice, consolidate into Docker Compose.

**Deliverables:**
- ✅ Voice proxy server (aiohttp) — Whisper STT, OpenAI TTS, Kibana converse API proxy
- ✅ Voice proxy Dockerfile + Docker Compose integration
- ✅ Chat sidebar embedded in Artemis React dashboard (glassmorphism, markdown, voice mode)
- ✅ React hooks: `useAthenaChat`, `useVoiceRecorder`, `useAthenaVoice`
- ✅ Zustand chat store with conversation management
- ✅ `docker compose up` starts full stack (4 services initially)
- ✅ nginx reverse proxy for frontend + voice-proxy routing
- ✅ TanStack Query cache invalidation on agent actions
- ✅ End-to-end validation on Linux (28/28 checks pass)
- ✅ OpenClaw/NanoClaw pattern research (ADR-003)

**Validation**: Full chat + voice flow through Artemis dashboard. Agent creates tasks → dashboard updates live.

### Phase 3: Memory, Proactivity, Polish (Days 14-24) — COMPLETE

**Goal**: Add memory, heartbeat, skills, monorepo, setup automation, polish for demo.

**Deliverables:**
- ✅ Monorepo merge — Artemis backend + frontend copied into single repo (ADR-004)
- ✅ ngrok static domain — no more URL churn across restarts
- ✅ Full end-to-end validation (28/28 checks pass)
- ✅ Memory system — `Meta/user-profile.md`, `Meta/memory.md`, injected via `systemPromptAddition`
- ✅ Conversation summaries dual-written to ES + daily notes
- ✅ System prompt synced to Agent Builder (16.3k chars)
- ✅ Heartbeat service — APScheduler, converse API, HEARTBEAT_OK suppression, daily note alerts
- ✅ Setup automation — `./setup.sh` one-command bootstrap (env validation, SQL migration, ES indexing, Kibana API)
- ✅ SQL migration for Supabase schema (tasks, daily_plans, pomodoro_sessions)
- ✅ Skills system — `skill_manager` MCP tool (5 operations), 3 sample skills
- ✅ Claude Code developer skills (`customize`, `add-integration`)
- ✅ `/ship` command (devlog + commit + push workflow)
- ✅ Persistent chat conversations (localStorage + history panel)
- ✅ Pomodoro polling fix (WebSocket-first, HTTP fallback)
- ✅ Full validation pass: 13/13 checks across 8 sub-projects, 0 errors

**Validation**: Complete agent flow with memory, skills, all tools working. Docker Compose starts 6 services.

### Phase 4: Ship (Days 25-27) — IN PROGRESS

**Goal**: Record, polish, submit.

**Deliverables:**
- [ ] 3-minute demo video recorded (OBS) and uploaded (YouTube unlisted)
- ✅ Final code cleanup and documentation pass
- ✅ `docker-compose.yml` for full stack deployment (6 services)
- ✅ `.env.example` with all variables documented
- [ ] Devpost description (~400 words)
- ✅ MIT license
- [ ] Social post on X tagging @elastic_devs, @elastic
- [ ] Screenshots captured
- [ ] Submission reviewed against judging criteria

**Validation**: Devpost submission is complete with all required fields. GitHub repo is public with MIT license.

---

## 13. Future Considerations

### Post-MVP Enhancements

- **Elastic Workflows**: Automated `note_watcher` (scan new notes for tasks) and `daily_planning_assistant` (morning plan suggestions)
- **Streaming responses**: SSE token-by-token streaming from agent to chat sidebar for lower perceived latency
- **Bulk vault operations**: Bulk tag, bulk move, bulk metadata updates across many notes at once
- **Backlink analysis**: Traverse Obsidian-style `[[wikilinks]]` to find related content through graph structure
- **uv workspaces**: Unify Python sub-projects under a root `pyproject.toml` with `[tool.uv.workspace]`

### Voice Enhancements

- **OpenAI Realtime API**: Full-duplex voice conversations with interruption handling and emotion
- **Streaming TTS**: Progressive audio playback as response generates, cutting perceived latency
- **Wake word detection**: "Hey Athena" via Picovoice Porcupine for always-listening mode
- **Voice activity detection**: Auto-detect when user starts/stops speaking (no button needed)
- **Multi-language support**: Whisper handles 50+ languages — enable non-English vault interaction

### Integration Opportunities

- **Calendar integration**: Pull calendar events to inform daily planning
- **Slack/Discord**: Let Athena respond to messages in team channels
- **Email**: Scan inbox for action items, propose tasks
- **GitHub**: Link tasks to PRs/issues, track development progress

### Advanced Features

- **Multi-vault support**: Index multiple Obsidian vaults (personal + work)
- **Custom embedding models**: Fine-tune on user's writing style for better search relevance
- **Task dependencies**: Model "blocked by" relationships between tasks
- **Recurring tasks**: Detect recurring patterns and auto-suggest repeating tasks
- **Obsidian plugin**: Native Obsidian plugin that talks to Athena directly

---

## 14. Risks & Mitigations

| # | Risk | Probability | Impact | Mitigation |
|---|------|------------|--------|------------|
| 1 | **Elastic Cloud trial expires before demo recorded** | Medium | Critical | Trial active since Feb 12. Must record demo before expiry (~Feb 26). All tools validated end-to-end. |
| 2 | **MCP connection from Elastic Cloud to local server fails** | Low | High | ngrok static domain eliminates URL churn. Docker Compose includes ngrok service. Validated end-to-end on Day 15. |
| 3 | **Agent creates tasks or modifies vault without user confirmation** | Medium | High | Add explicit "NEVER" rules in system prompt. Use `confirm_destructive` parameter for deletes. Test adversarially. |
| 4 | **Vault path traversal or accidental file corruption** | Low | Critical | VaultManager validates all paths against vault root. Write operations create backups. Test with adversarial paths. |
| 5 | **Voice transcription too slow or inaccurate for demo** | Low | Medium | Whisper API is fast (~1-2s). Fall back to text-only demo if issues arise. Voice is additive, not required for core flow. |
| 6 | **Scope creep consumes hackathon time** | High | High | MVP is exactly: search, read, create note, extract tasks, plan day. Voice is P3 — only if core works by Day 9. |

---

## 15. Appendix

### Hackathon Details

- **Event**: Elasticsearch Agent Builder Hackathon (Devpost)
- **Deadline**: February 27, 2026, 1:00 PM EST (20:00 Athens time)
- **Prize Pool**: $20,000 ($10K / $5K / $3K + 4x$500 Creative Awards)
- **Judging**: Technical Execution (30%), Impact & Wow Factor (30%), Demo (30%), Social (10%)
- **Required**: Agent Builder, Elasticsearch, demo video, public GitHub repo, social post

### Key Dependencies

| Dependency | URL | Notes |
|-----------|-----|-------|
| Elastic Cloud | https://cloud.elastic.co/registration?cta=hackathon | 14-day trial |
| Agent Builder Docs | https://www.elastic.co/docs/explore-analyze/ai-features/elastic-agent-builder | Configuration reference |
| MCP Server Docs | https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/mcp-server | MCP integration |
| OpenAI Whisper API | https://platform.openai.com/docs/guides/speech-to-text | STT for voice input |
| OpenAI TTS API | https://platform.openai.com/docs/guides/text-to-speech | TTS for voice output |
| Artemis (merged) | `services/artemis-backend/` + `frontend/` | FastAPI + React + Supabase (monorepo) |
| Devpost | https://elasticsearch.devpost.com/ | Submission platform |

### Elasticsearch Index Schemas

**`athena-notes`**:
`title` (text+keyword), `content` (text), `content_semantic` (semantic_text → ELSER), `tags` (keyword[]), `note_type` (keyword), `path` (keyword), `vault_relative_path` (keyword), `word_count` (integer), `created_at` (date), `updated_at` (date), `indexed_at` (date), `checksum` (keyword)

**`athena-conversations`**:
`summary` (text), `summary_semantic` (semantic_text → ELSER), `topics` (keyword[]), `extracted_tasks` (text[]), `task_ids_created` (keyword[]), `timestamp` (date)

### Reference Projects (Inspiration)

| Project | What We Borrowed |
|---------|-----------------|
| `obsidian-ai-agent` (Paddy) | VaultManager pattern, 3-tool consolidation, path validation, Docker volume mounting, frontmatter models |
| `hierarchical-rag` | Dual hierarchy concept (categorical + structural), chunk context retrieval pattern |
| `obsidian-productivity-agent` | Tool registration patterns, web search integration, RAG retrieval approach |
| `full-stack-fastapi-nextjs-llm-template` | Project structure inspiration, WebSocket streaming pattern (future) |
| `claude-code-second-brain-skills` | Skill/command creation patterns for Claude Code integration |

### Submission Checklist

- [ ] ~400 word project description on Devpost
- [ ] ~3 minute demo video (YouTube unlisted)
- [x] Public GitHub repository with MIT license
- [ ] Social media post on X tagging @elastic_devs or @elastic
- [ ] Architecture diagram (Mermaid) in repo and demo
- [x] Docker Compose for full stack (6 services)
- [x] README with setup instructions
- [x] One-command setup (`./setup.sh`)
- [ ] Voice demo included in video
- [ ] Screenshots captured

---

*Created: February 12, 2026*
*Updated: February 18, 2026*
*Project: Athena — Second Brain Orchestrator Agent*
*Developer: Stratos Louvaris (solo)*
