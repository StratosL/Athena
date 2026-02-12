# Athena: Orchestrator Agent Implementation Plan

## Context

Building an AI orchestrator agent for the Elasticsearch Agent Builder Hackathon (deadline Feb 27, $20K prize pool). Athena bridges an Obsidian knowledge base (via Elasticsearch) with the Artemis productivity app (via MCP), acting as an intelligent control center that discusses, curates, and executes — not just a pipeline.

**Key constraint**: Elastic Cloud 14-day trial starts today (Feb 11), expires Feb 25. Demo must be recorded before then.

---

## Architecture

```
User ←→ Agent Builder (Athena) ←→ Elasticsearch (knowledge)
                ↓ MCP
         Athena MCP Server
           ├── Artemis tools → Artemis API (:8000)
           ├── Knowledge write-back → Elasticsearch + Obsidian vault
           └── Research tools → Web search + URL fetch
```

**5 components to build:**

| # | Component | Location | Purpose |
|---|-----------|----------|---------|
| 1 | **Obsidian Indexer** | `indexer/` | Sync vault → Elasticsearch |
| 2 | **Elasticsearch Indices** | Elastic Cloud | `athena-notes` + `athena-conversations` (2 indices, not 4) |
| 3 | **Athena MCP Server** | `mcp-server/` | Single server: Artemis + Knowledge + Research tools |
| 4 | **Agent Builder Config** | `agent-config/` | System prompt + ES|QL tools |
| 5 | **Sample Vault** | `sample-vault/` | 15-20 demo notes with extractable tasks |

**Key design decisions:**
- **Simple Modular Architecture** (not VSA) — Athena's sub-projects are a CLI indexer and an MCP tool server, neither of which maps to VSA's routes/service/repository pattern. VSA fits Artemis (web API with domain features) but is over-engineering for tools/pipelines. We borrow VSA's good ideas (centralized config, separation of concerns, one file = one job) without the ceremony. See architecture rationale below.
- 2 indices instead of 4 (ideas = notes with `type: idea`, projects tracked in Artemis)
- Single unified MCP server (Artemis + knowledge write-back + research)
- Agent Builder built-in chat UI (no custom frontend)
- `semantic_text` field type for embeddings (ES handles chunking/embedding automatically)
- ngrok for dev, Railway/Render for demo recording

### Architecture Rationale: Why Not VSA

| Criterion | Artemis (VSA) | Athena Indexer | Athena MCP Server |
|-----------|--------------|----------------|-------------------|
| Has REST routes? | Yes (CRUD per feature) | No (CLI) | No (MCP protocol) |
| Has service layer? | Yes (business logic) | No (parse → index pipeline) | Thin (proxy to Artemis API) |
| Has repository layer? | Yes (Supabase queries) | No (ES bulk API) | No (httpx calls) |
| Multiple domain features? | Yes (tasks, plans, pomodoro, analytics) | No (one job: index notes) | Tool groups, not features |
| Codebase size | 5K+ lines | ~300-500 lines | ~500-800 lines |
| **VSA fit?** | **Yes** | **No** | **No** |

**What we use instead**: Flat modules grouped by responsibility. Each file has one clear job. `tools/` subdirectory groups MCP tools by external system (artemis, knowledge, research) — borrowing VSA's isolation idea without the layered ceremony.

---

## Elasticsearch Indices

### `athena-notes`
Fields: `title` (text+keyword), `content` (text), `content_semantic` (semantic_text → ELSER), `tags` (keyword[]), `note_type` (keyword: note/idea/meeting/brainstorm), `path` (keyword), `vault_relative_path` (keyword), `word_count` (integer), `created_at` (date), `updated_at` (date), `indexed_at` (date), `checksum` (keyword)

### `athena-conversations`
Fields: `summary` (text), `summary_semantic` (semantic_text → ELSER), `topics` (keyword[]), `extracted_tasks` (text[]), `task_ids_created` (keyword[]), `timestamp` (date)

---

## Tools Inventory

### ES|QL Tools (read-only, configured in Agent Builder)

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `search_notes` | query (str), tag_filter (str?), limit (int=5) | Full-text search notes |
| `get_recent_notes` | days (int=7), limit (int=10) | Recently modified notes |
| `get_notes_by_tag` | tag (str) | Notes filtered by tag |
| `get_conversation_history` | topic (str?), limit (int=5) | Past conversation summaries |
| `count_notes_by_tag` | none | Tag distribution stats |

Plus **built-in search tool** on `athena-notes` for semantic/hybrid search.

### MCP Tools (in Athena MCP Server)

**Artemis tools** (proxy to Artemis REST API at `/home/stardust/Artemis`):

| Tool | Artemis Endpoint | Notes |
|------|-----------------|-------|
| `artemis_create_task` | `POST /tasks` | title, quadrant(1-4), description?, due_date? |
| `artemis_list_tasks` | `GET /tasks` | quadrant?, status? filters |
| `artemis_complete_task` | `POST /tasks/{id}/complete` | |
| `artemis_get_daily_plan` | `GET /daily-plans/today` | Auto-creates if none exists |
| `artemis_assign_to_plan` | `POST /daily-plans/{plan_id}/tasks` | task_id + slot (major/medium/small) |
| `artemis_get_analytics` | `GET /analytics/summary` | period: day/week/month |
| `artemis_start_pomodoro` | `POST /pomodoro/start` | task_id? |

**Knowledge tools** (write to Elasticsearch + Obsidian vault):

| Tool | Purpose |
|------|---------|
| `save_note` | Save new note → .md file in vault + index in `athena-notes` |
| `save_conversation_summary` | Save conversation context → `athena-conversations` |

**Research tools** (stretch goal):

| Tool | Purpose |
|------|---------|
| `web_search` | Search web via Tavily/Brave API |
| `fetch_url` | Fetch + extract text from URL |

**Priority**: Artemis tools + save_conversation_summary = MVP. save_note + research = nice-to-have.

---

## System Prompt Design

Core behavioral rules for the Athena agent:
1. **Always confirm before acting** on Artemis — present proposed tasks, wait for approval
2. **Search first** — when user asks about anything, check knowledge base before responding
3. **Eisenhower-literate** — correctly classify Q1-Q4 (default to Q2 when uncertain)
4. **1-3-5 aware** — understand daily plan slot limits
5. **Save insights** — after productive conversations, save summaries for future context
6. **Concise and structured** — use numbered lists for task proposals, interpret analytics

---

## Files to Create

```
/home/stardust/Athena/
├── .gitignore
├── .env.example
├── docker-compose.yml
├── README.md (later)
├── LICENSE (MIT, later)
│
├── indexer/
│   ├── pyproject.toml
│   └── src/
│       ├── __init__.py
│       ├── config.py          # ES URL, API key, vault path, index names
│       ├── mappings.py        # Index mapping dicts
│       ├── parser.py          # .md → dict (frontmatter + content + checksum)
│       ├── indexer.py         # Bulk index into ES
│       ├── watcher.py         # watchdog file watcher (Day 10)
│       └── cli.py             # CLI: index, watch, setup-indices
│
├── mcp-server/
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── src/
│       ├── __init__.py
│       ├── config.py          # Artemis URL, ES URL, API keys
│       ├── server.py          # MCP server setup + SSE transport
│       ├── artemis_client.py  # httpx wrapper for Artemis REST API
│       ├── es_client.py       # ES client for knowledge write-back
│       └── tools/
│           ├── __init__.py
│           ├── artemis.py     # All Artemis MCP tools
│           ├── knowledge.py   # save_note, save_conversation_summary
│           └── research.py    # web_search, fetch_url (stretch)
│
├── agent-config/
│   ├── system-prompt.md
│   ├── setup-guide.md
│   └── tools/                 # ES|QL tool definitions (JSON)
│
├── sample-vault/
│   ├── Projects/              # 3-4 project notes with action items
│   ├── Ideas/                 # 3-4 idea notes
│   ├── Meeting Notes/         # 3-4 meeting notes with follow-ups
│   ├── Daily Notes/           # 3-4 daily journal entries
│   └── Research/              # 2-3 research notes
│
├── docs/
│   ├── architecture.md
│   └── architecture.mermaid
│
└── devpost/
    ├── description.md
    └── screenshots/
```

---

## Implementation Order (17 Days)

### Phase 1: Foundation (Days 1-4)

**Day 1 (Feb 11) — Elasticsearch + Indexer**
- Sign up Elastic Cloud Serverless trial
- Complete "Your First Elastic Agent" tutorial
- Configure LLM connector (OpenAI or Anthropic)
- Set up ELSER inference endpoint
- Create `athena-notes` + `athena-conversations` indices
- Init `indexer/` project (uv), implement parser.py + indexer.py + cli.py + mappings.py
- Create sample vault (15-20 notes)
- Run indexer, verify search works in Dev Tools
- **Deliverable**: Vault indexed and searchable

**Day 2 (Feb 12) — Agent Builder + ES|QL Tools**
- Create "Athena" agent in Agent Builder
- Write system prompt
- Configure built-in search on `athena-notes`
- Create ES|QL tools: search_notes, get_recent_notes, get_notes_by_tag, count_notes_by_tag
- Test conversational flow — ask about vault content
- Iterate system prompt based on behavior
- **Deliverable**: Agent searches and discusses knowledge base

**Day 3 (Feb 13) — MCP Server Core**
- Init `mcp-server/` project (uv)
- Implement server.py (MCP + SSE transport)
- Implement artemis_client.py (httpx wrapper)
- Implement all Artemis tools (create_task, list_tasks, complete_task, get_daily_plan, assign_to_plan, get_analytics, start_pomodoro)
- Test with MCP Inspector
- **Deliverable**: MCP server with Artemis tools working standalone

**Day 4 (Feb 14) — Connect Agent Builder ↔ MCP**
- Deploy MCP server + expose via ngrok
- Register MCP server in Agent Builder
- Test: agent creates task → appears in Artemis
- Test: agent plans day → assigns to daily plan
- Debug connection issues
- **Deliverable**: End-to-end: Agent Builder → MCP → Artemis

### Phase 2: Intelligence (Days 5-8)

**Day 5 (Feb 15) — Knowledge Write-back**
- Implement save_conversation_summary tool
- Implement save_note tool (ES + .md file)
- Add get_conversation_history ES|QL tool
- Test full bidirectional flow
- **Deliverable**: Agent reads AND writes to knowledge base

**Day 6 (Feb 16) — Task Extraction + Classification**
- Refine system prompt for accurate task extraction from notes
- Test with various note styles (meetings, projects, brainstorms)
- Tune Eisenhower classification with examples in prompt
- Add Pomodoro estimation guidance
- **Deliverable**: Reliable task extraction and classification

**Day 7 (Feb 17) — Daily Planning Flow**
- Build "plan my day" workflow: list tasks → check plan → suggest 1-3-5 → confirm → assign
- Handle edge cases (plan full, no tasks, already assigned)
- Test "start working" flow (pick major task → start pomodoro)
- **Deliverable**: Complete daily planning conversational flow

**Day 8 (Feb 18) — Research Tools + Robustness**
- Implement web_search tool (Tavily or Brave free tier)
- Implement fetch_url tool (httpx + html2text)
- Add error handling to all MCP tools
- Test edge cases
- **Deliverable**: Research capability + stable system

### Phase 3: Demo Prep (Days 9-13)

**Day 9 (Feb 19)** — File watcher (watchdog), analytics narration
**Day 10 (Feb 20)** — Finalize sample vault for demo, practice demo flow
**Day 11 (Feb 21)** — Architecture diagram (Mermaid), README, demo script
**Day 12 (Feb 22)** — Devpost description, screenshots, MIT license
**Day 13 (Feb 23)** — Social post on X, final practice run, buffer

### Phase 4: Ship (Days 14-17)

**Day 14 (Feb 24)** — Record 3-min demo video (OBS → YouTube unlisted)
**Day 15 (Feb 25)** — Final polish, docker-compose, .env.example **(TRIAL EXPIRES)**
**Day 16 (Feb 26)** — Submit to Devpost
**Day 17 (Feb 27)** — Buffer (deadline 1:00 PM EST)

---

## Verification

After each phase, verify:

1. **After Day 1**: `curl` Elasticsearch with a search query → returns indexed notes
2. **After Day 2**: Chat with agent in Agent Builder → it finds and discusses notes
3. **After Day 4**: Ask agent to create a task → check Artemis at `localhost:8000/tasks` → task exists
4. **After Day 5**: Ask agent to save a conversation → check `athena-conversations` index → document exists
5. **After Day 7**: Ask agent to plan your day → check `localhost:8000/daily-plans/today` → tasks assigned
6. **After Day 8**: Ask agent to research a URL → it fetches and summarizes content

---

## Critical Artemis API Surface (verified)

Source: `/home/stardust/Artemis/backend/app/features/`

- `POST /tasks` — body: `{title, quadrant(1-4), description?, due_date?}`
- `GET /tasks?quadrant=X&status=Y&limit=N&offset=N` — returns `{items[], total}`
- `POST /tasks/{id}/complete`
- `GET /daily-plans/today` — auto-creates plan
- `POST /daily-plans/{plan_id}/tasks` — body: `{task_id, slot: "major"|"medium"|"small"}`
- `GET /analytics/summary?period=day|week|month`
- `POST /pomodoro/start` — body: `{task_id?, duration_minutes?}`

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Trial expires before demo | Sign up Day 1, record by Day 14, backup partial recording Day 11 |
| MCP connection fails (ngrok) | Have Dockerfile ready Day 3, deploy to Railway if needed |
| ES|QL tools too limited | Fall back to built-in search tool (covers 80% of cases) |
| Agent creates tasks without asking | Add explicit "NEVER" rules in system prompt, test adversarially |
| Scope creep | MVP = search + extract + create + plan. Add features only after Day 8 |
