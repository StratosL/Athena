# Athena: Second Brain Orchestrator Agent — Product Requirements Document

---

## 1. Executive Summary

Athena is a conversational AI agent that serves as the intelligent bridge between a personal knowledge vault (Obsidian) and a productivity execution system (Artemis). It lives inside Elastic Agent Builder and orchestrates across Elasticsearch, a local Obsidian vault, and the Artemis REST API — reading your notes, writing new ones, extracting tasks, planning your day, and reporting on your productivity, all through natural conversation.

What makes Athena different from a generic assistant is its **dual-path knowledge access**: Elasticsearch provides semantic search and analytics across your entire vault, while direct filesystem access gives real-time read/write capability to individual notes. The agent doesn't just search your notes — it lives in your vault, creating new notes, appending to your daily journal, and organizing your knowledge as you work.

Athena also supports **voice interaction** as a first-class input/output mode. You can talk to your second brain and hear it respond, making it feel like a true intellectual companion rather than a chat window.

**MVP Goal**: A working orchestrator agent on Elastic Agent Builder that can search an indexed Obsidian vault semantically, read/write notes directly, extract and classify tasks into Artemis with user confirmation, plan daily work using the 1-3-5 rule, and optionally interact via voice — submitted as a hackathon entry by February 27, 2026.

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
- ✅ Single unified MCP server (Vault + Artemis + Knowledge + Research tools)
- ✅ Docker volume mounting for vault filesystem access
- ✅ Sample Obsidian vault with 15-20 demo notes
- ✅ Agent Builder built-in chat UI (primary) + voice-enabled thin client

**Research:**
- ✅ Web search capability (Tavily or Brave Search free tier)
- ✅ URL fetching and content extraction

### Out of Scope (Post-MVP / Future)

**Deferred:**
- ❌ Custom chat frontend embedded in Artemis
- ❌ Real-time WebSocket updates in Artemis when agent creates tasks
- ❌ Multi-user / authentication
- ❌ Elastic Workflows automation (note watcher, daily planning assistant)
- ❌ Wake word detection ("Hey Athena")
- ❌ OpenAI Realtime API (full-duplex voice)
- ❌ Streaming TTS (progressive audio playback)
- ❌ Mobile app integration
- ❌ Sync with cloud-hosted Obsidian vaults (iCloud, Sync)
- ❌ Integration with external tools (Slack, email, calendar)
- ❌ Fine-tuned embeddings model
- ❌ Advanced analytics (weekly reviews, trend analysis)
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
User ←→ Voice Layer (STT/TTS) ←→ Agent Builder (Athena) ←→ Elasticsearch
              ↓ MCP Protocol                                  ↑ ES|QL
         Athena MCP Server                                     |
           ├── Vault tools     → Obsidian Vault (filesystem)   |
           ├── Artemis tools   → Artemis REST API (:8000)      |
           ├── Knowledge tools → Elasticsearch (write-back)     |
           └── Research tools  → Web search + URL fetch         |
                                                                |
         Indexer CLI ──────── Obsidian Vault → Elasticsearch ───┘
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

Not VSA. Athena's sub-projects (a CLI indexer, an MCP server, and a thin voice client) don't map to VSA's routes/service/repository pattern. We borrow good ideas — centralized config, separation of concerns, one file = one job — without the layered ceremony.

### Directory Structure

```
/home/stardust/Athena/
├── .claude/                        # Claude Code configuration
│   ├── commands/
│   │   └── create-prd.md
│   └── settings.json
├── .gitignore
├── .env.example
├── docker-compose.yml
├── README.md
├── LICENSE (MIT)
├── PRD.md
│
├── indexer/                         # Obsidian → Elasticsearch sync
│   ├── pyproject.toml
│   └── src/
│       ├── __init__.py
│       ├── config.py                # ES URL, API key, vault path, index names
│       ├── mappings.py              # Elasticsearch index mapping definitions
│       ├── parser.py                # .md file → dict (frontmatter + content + checksum)
│       ├── indexer.py               # Bulk index parsed documents into Elasticsearch
│       ├── watcher.py               # watchdog file watcher for live sync
│       └── cli.py                   # CLI entry points: index, watch, setup-indices
│
├── mcp-server/                      # Unified MCP server
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── src/
│       ├── __init__.py
│       ├── config.py                # Vault path, Artemis URL, ES URL, API keys
│       ├── server.py                # MCP server setup + SSE transport
│       ├── artemis_client.py        # httpx wrapper for Artemis REST API
│       ├── es_client.py             # Elasticsearch client for knowledge write-back
│       ├── vault_manager.py         # Obsidian vault filesystem access (read/write/query)
│       └── tools/
│           ├── __init__.py
│           ├── vault.py             # 3 vault MCP tools (query, read, manage)
│           ├── artemis.py           # 7 Artemis MCP tools
│           ├── knowledge.py         # 2 knowledge write-back tools (ES)
│           └── research.py          # 2 research tools (web search, URL fetch)
│
├── voice-client/                    # Thin voice-enabled web client
│   ├── index.html                   # Single-page app with mic/speaker controls
│   ├── voice.js                     # Whisper STT + OpenAI TTS integration
│   └── style.css                    # Minimal styling
│
├── agent-config/                    # Agent Builder configuration (tracked in git)
│   ├── system-prompt.md             # Athena persona and behavioral rules
│   ├── setup-guide.md              # How to configure in Kibana
│   └── tools/                       # ES|QL tool definitions (JSON exports)
│
├── sample-vault/                    # Demo Obsidian vault
│   ├── Projects/
│   ├── Ideas/
│   ├── Meeting Notes/
│   ├── Daily Notes/
│   └── Research/
│
├── docs/
│   ├── architecture.md
│   └── architecture.mermaid
│
└── devpost/
    ├── description.md
    └── screenshots/
```

### Key Design Patterns

1. **VaultManager Pattern**: Centralized filesystem access class (inspired by obsidian-ai-agent) with path validation, directory traversal prevention, frontmatter parsing, and all CRUD operations. All vault tools delegate to this single class.
2. **Adapter Pattern**: `artemis_client.py`, `es_client.py`, and `vault_manager.py` each adapt an external system into a clean internal interface that MCP tools consume.
3. **3-Tool Consolidation**: Vault access uses three tools with operation parameters rather than many single-purpose tools — following Anthropic's "fewer tools, more parameters" best practice.
4. **Configuration via Environment**: All secrets and URLs in `.env`, loaded via `pydantic-settings`.
5. **Checksum-based Deduplication**: Indexer computes MD5 checksums to skip re-indexing unchanged files.
6. **Confirm Destructive**: Vault write/delete operations require explicit confirmation parameter to prevent accidental data loss.

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
| `save_conversation_summary` | Persist conversation context for future recall | `athena-conversations` index |

Note: `save_note` is now handled by `vault_manage.create_note` which writes to the filesystem. The indexer (or watcher) syncs it to Elasticsearch.

### MCP Tools — Research Group

| Tool | Purpose |
|------|---------|
| `web_search` | Search the web via Tavily/Brave API, return top results with snippets |
| `fetch_url` | Fetch a URL, extract text content via html2text, return summary |

### Tool Priority

| Priority | Tools | Rationale |
|----------|-------|-----------|
| **P0 — Demo-critical** | `search_notes`, `vault_read`, `vault_manage` (create, append), `artemis_create_task`, `artemis_list_tasks`, `artemis_get_daily_plan`, `artemis_assign_to_plan`, `save_conversation_summary` | Core demo flow: search → read → extract → create → plan |
| **P1 — Full experience** | `vault_query`, `vault_manage` (edit, move, delete), `artemis_complete_task`, `artemis_get_analytics`, `artemis_start_pomodoro`, `get_recent_notes`, `get_notes_by_tag` | Complete vault management + productivity tracking |
| **P2 — Nice-to-have** | `web_search`, `fetch_url`, `count_notes_by_tag`, `get_conversation_history` | Research capability + analytics |
| **P3 — Voice** | Whisper STT, OpenAI TTS, voice client UI | Voice I/O layer (independent of backend) |

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
| `elasticsearch[async]` | >=9.3.0 | Elasticsearch client for bulk indexing |
| `python-frontmatter` | Latest | Parse Obsidian YAML frontmatter from .md files |
| `watchdog` | Latest | Filesystem watcher for live vault sync |
| `pydantic-settings` | Latest | Configuration management |

### MCP Server (`mcp-server/`)

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Runtime |
| `uv` | Latest | Project management |
| `mcp` | Latest | MCP protocol server implementation (SSE transport) |
| `httpx` | Latest | Async HTTP client for Artemis REST API |
| `elasticsearch[async]` | >=9.3.0 | ES client for knowledge write-back |
| `python-frontmatter` | Latest | Parse/write YAML frontmatter in vault notes |
| `pydantic` | >=2.0 | Data validation for tool inputs/outputs |
| `pydantic-settings` | Latest | Configuration management |
| `html2text` | Latest | URL content extraction (research tools) |

### Voice Client (`voice-client/`)

| Technology | Version | Purpose |
|-----------|---------|---------|
| HTML/JS/CSS | Vanilla | Single-page voice-enabled interface |
| MediaRecorder API | Browser built-in | Audio capture from microphone |
| OpenAI Whisper API | Latest | Speech-to-text transcription |
| OpenAI TTS API | Latest | Text-to-speech (voices: alloy, echo, fable, onyx, nova, shimmer) |

### Existing Dependencies

| Technology | Location | Purpose |
|-----------|----------|---------|
| Artemis Backend | `/home/stardust/Artemis/backend/` | FastAPI + Supabase — task management, daily plans, pomodoro, analytics |
| Artemis Frontend | `/home/stardust/Artemis/frontend/` | React + Vite + TypeScript — dashboard UI |

### Infrastructure

| Technology | Purpose |
|-----------|---------|
| Docker + Docker Compose | Orchestrate MCP server + Artemis stack + vault volume mount |
| ngrok | Expose local MCP server to Elastic Cloud during development |
| Railway or Render | Production deployment for demo recording |

---

## 9. Security & Configuration

### Configuration Management

All configuration via environment variables, loaded with `pydantic-settings`:

```env
# Elasticsearch
ELASTIC_CLOUD_ID=<deployment-cloud-id>
ELASTIC_API_KEY=<api-key>

# Obsidian Vault
VAULT_PATH=/path/to/obsidian/vault

# Indexer
NOTES_INDEX=athena-notes
CONVERSATIONS_INDEX=athena-conversations

# MCP Server
ARTEMIS_BASE_URL=http://localhost:8000
MCP_SERVER_PORT=8001

# Voice (optional)
OPENAI_API_KEY=<key>

# Research (stretch)
TAVILY_API_KEY=<key>  # or BRAVE_API_KEY
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
Agent Builder (Elastic Cloud) → MCP Server: MCP protocol over SSE (public URL via ngrok)
MCP Server → Artemis Backend: HTTP to localhost:8000 (Docker network)
MCP Server → Elasticsearch: HTTPS to Elastic Cloud endpoint
MCP Server → Obsidian Vault: Filesystem via Docker volume mount
Voice Client → OpenAI API: HTTPS (Whisper STT + TTS)
Voice Client → Agent Builder: HTTPS (chat API)
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
- ✅ Indexer can process 15-20 Obsidian notes with frontmatter into Elasticsearch
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
- Smooth conversational flow — no awkward pauses, no tool errors visible
- Clear demonstration of bidirectional data flow (read notes + write notes + create tasks + save conversations)

---

## 12. Implementation Phases

### Phase 1: Foundation (Days 1-4)

**Goal**: Get data flowing — vault indexed, agent searching, MCP server proxying to Artemis with vault access.

**Deliverables:**
- ✅ Elastic Cloud Serverless trial active with LLM connector configured
- ✅ ELSER inference endpoint set up for semantic search
- ✅ `athena-notes` and `athena-conversations` indices created with mappings
- ✅ Indexer project: `parser.py`, `indexer.py`, `cli.py`, `mappings.py`, `config.py`
- ✅ Sample vault with 15-20 notes created and indexed
- ✅ Agent Builder "Athena" agent with system prompt and built-in search
- ✅ ES|QL tools: `search_notes`, `get_recent_notes`, `get_notes_by_tag`, `count_notes_by_tag`
- ✅ MCP server with all 7 Artemis tools implemented
- ✅ MCP server registered in Agent Builder via ngrok
- ✅ Docker volume mount for vault access configured

**Validation**: Ask agent "What are my notes about [topic]?" → get relevant results. Ask agent to create a task → it appears in Artemis at `localhost:8000/tasks`.

### Phase 2: Vault Access + Intelligence (Days 5-8)

**Goal**: Give the agent direct vault read/write, smart task extraction, and daily planning.

**Deliverables:**
- ✅ `VaultManager` class with path validation, frontmatter parsing, all CRUD operations
- ✅ Vault MCP tools: `vault_query`, `vault_read`, `vault_manage`
- ✅ Knowledge write-back tool: `save_conversation_summary`
- ✅ `get_conversation_history` ES|QL tool
- ✅ System prompt refined for accurate Eisenhower classification
- ✅ Daily planning flow: list tasks → check plan → suggest 1-3-5 → confirm → assign
- ✅ Research tools: `web_search`, `fetch_url`
- ✅ Error handling on all MCP tools
- ✅ Edge cases handled (empty vault, full plan slots, no pending tasks)

**Validation**: Full end-to-end flow — search notes → read specific note → extract tasks → create with confirmation → plan day. Agent saves a new note to the vault. Conversation summary saved to ES.

### Phase 3: Voice + Demo Prep (Days 9-13)

**Goal**: Add voice capabilities and polish for a compelling 3-minute demo.

**Deliverables:**
- ✅ Voice client: HTML page with microphone capture (MediaRecorder API)
- ✅ Whisper API integration for speech-to-text
- ✅ OpenAI TTS integration for text-to-speech
- ✅ Voice/text toggle in client UI
- ✅ File watcher (`watchdog`) for live vault sync
- ✅ Analytics narration (agent interprets numbers, not just reports them)
- ✅ Sample vault finalized with demo-optimized content
- ✅ Demo script written and rehearsed (2-3 practice runs)
- ✅ Architecture diagram (Mermaid)
- ✅ README with setup instructions

**Validation**: Complete demo run-through with voice interaction, no errors, under 3 minutes.

### Phase 4: Ship (Days 14-17)

**Goal**: Record, polish, submit.

**Deliverables:**
- ✅ 3-minute demo video recorded (OBS) and uploaded (YouTube unlisted)
- ✅ Final code cleanup and documentation pass
- ✅ `docker-compose.yml` for full stack deployment
- ✅ `.env.example` with all variables documented
- ✅ Devpost description (~400 words)
- ✅ MIT license
- ✅ Social post on X tagging @elastic_devs, @elastic
- ✅ Screenshots captured
- ✅ Submission reviewed against judging criteria

**Validation**: Devpost submission is complete with all required fields. GitHub repo is public with MIT license.

---

## 13. Future Considerations

### Post-MVP Enhancements

- **Custom chat UI in Artemis**: Embed Athena's chat interface in the Artemis dashboard for a unified experience
- **Real-time task updates**: WebSocket integration so Artemis dashboard updates live when agent creates tasks
- **Elastic Workflows**: Automated `note_watcher` (scan new notes for tasks) and `daily_planning_assistant` (morning plan suggestions)
- **Weekly review**: Agent generates a weekly productivity report combining Artemis analytics + knowledge base activity
- **Bulk vault operations**: Bulk tag, bulk move, bulk metadata updates across many notes at once
- **Backlink analysis**: Traverse Obsidian-style `[[wikilinks]]` to find related content through graph structure

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
| 1 | **Elastic Cloud trial expires before demo recorded** | Medium | Critical | Sign up immediately. Trial expires ~14 days later. Record demo by Day 14. Backup partial recording on Day 11. |
| 2 | **MCP connection from Elastic Cloud to local server fails** | Medium | High | Have `Dockerfile` ready by Day 3. Test ngrok Day 5. If unstable, deploy to Railway/Render immediately. |
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
| Artemis (existing) | `/home/stardust/Artemis` | FastAPI + React + Supabase |
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
- [ ] Public GitHub repository with MIT license
- [ ] Social media post on X tagging @elastic_devs or @elastic
- [ ] Architecture diagram (Mermaid) in repo and demo
- [ ] Docker Compose for full stack
- [ ] README with setup instructions
- [ ] Voice demo included in video

---

*Created: February 12, 2026*
*Updated: February 12, 2026*
*Project: Athena — Second Brain Orchestrator Agent*
*Developer: Stratos Louvaris (solo)*
