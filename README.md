# Athena — Second Brain Orchestrator Agent

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Elastic](https://img.shields.io/badge/Elastic-Agent%20Builder-005571.svg)

**Turn scattered knowledge into focused action through intelligent, conversational orchestration.**

</div>

---

Athena is a conversational AI agent built on [Elastic Agent Builder](https://www.elastic.co/elasticsearch/agent-builder) that bridges your [Obsidian](https://obsidian.md) vault with [Artemis](https://github.com/StratosL/Artemis) (included), a productivity app. It searches your notes semantically, reads and writes to your vault in real-time, extracts tasks with Eisenhower classification, plans your day using the 1-3-5 rule, and remembers past conversations — all through natural language, text or voice.

### What's Different

- **Dual-path knowledge**: Elasticsearch (ELSER) for semantic search *and* direct vault filesystem for real-time read/write
- **Bidirectional**: Creates notes, appends to journals, organizes your vault — not just read-only search
- **Human-in-the-loop**: Never creates tasks or modifies notes without your explicit confirmation
- **Voice-first option**: Whisper STT + OpenAI TTS — talk to your second brain and hear it respond

### Current State

Self-contained monorepo — Artemis backend + frontend included. 19 tools registered in Agent Builder (6 ES|QL + 13 MCP), 17-note sample vault indexed with ELSER semantic search, voice client with proxy server. Clone and `docker compose up`.

---

## Architecture

```
User <-> Voice Layer (STT/TTS) <-> Agent Builder (Athena) <-> Elasticsearch (ELSER)
              |                                                     ^
              v MCP Protocol                                        | ES|QL
         Athena MCP Server                                          |
           |-- Vault tools     -> Obsidian Vault (filesystem)       |
           |-- Artemis tools   -> Artemis REST API (:8000)          |
           |-- Knowledge tools -> Elasticsearch (write-back)        |
           '-- Research tools  -> Web search + URL fetch            |
                                                                    |
         Indexer CLI ---------- Obsidian Vault -> Elasticsearch ----'
```

| Component | Technology |
|-----------|-----------|
| Orchestrator | Elastic Agent Builder (system prompt, tool routing, conversations) |
| Search | Elasticsearch Serverless + ELSER v2 (`semantic_text` auto-embedding) |
| Tool protocol | MCP — Streamable HTTP transport |
| Vault access | Python + `python-frontmatter` (direct filesystem CRUD) |
| Task management | Artemis REST API via `httpx` |
| Voice | OpenAI Whisper (STT) + TTS, browser MediaRecorder |
| Infrastructure | Docker Compose, ngrok for tunneling |

---

## Prerequisites

- **Python 3.12+** and [uv](https://docs.astral.sh/uv/)
- **Docker** and **Docker Compose** (recommended — runs all services with one command)
- **[Elastic Cloud](https://cloud.elastic.co/registration?cta=hackathon)** account — free 14-day Serverless trial
- **[ngrok](https://ngrok.com/)** — free account to expose MCP server to Elastic Cloud
- **[OpenAI API key](https://platform.openai.com)** — for voice (Whisper + TTS) and optionally research
- **Artemis** is included in this repository (`services/artemis-backend/` + `frontend/`)

---

## Quick Start

### Option A: Run Locally (recommended for development)

```bash
# 1. Clone and configure
git clone https://github.com/StratosL/Athena.git
cd Athena
cp .env.example .env
# Edit .env — fill in ELASTIC_URL, ELASTIC_API_KEY, VAULT_PATH, and OPENAI_API_KEY
```

```bash
# 2. Create Elasticsearch indices and index your vault
cd indexer && uv sync
uv run athena-index setup-indices   # creates athena-notes + athena-conversations indices
uv run athena-index index           # parses and bulk-indexes all .md files
cd ..
```

```bash
# 3. Start the MCP server
cd mcp-server && uv sync
uv run python -m src                # starts on port 8001 (Streamable HTTP)
```

> **Important**: Always use `python -m src`, never `python -m src.server` — the latter causes a double-import bug that prevents tools from registering.

```bash
# 4. Expose to Elastic Cloud via ngrok
ngrok http 8001
# Copy the https:// URL — you'll need it for Step 5
```

```bash
# 5. (Optional) Start the voice proxy
cd voice-client && uv sync
uv run python serve.py              # starts on port 3001
```

### Option B: Run with Docker Compose (recommended)

```bash
git clone https://github.com/StratosL/Athena.git
cd Athena
cp .env.example .env
# Edit .env with your credentials (ELASTIC_URL, ELASTIC_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY)

docker compose up --build
# Artemis backend  → http://localhost:8000
# Artemis frontend → http://localhost:3000
# MCP server       → http://localhost:8001
# Voice proxy      → http://localhost:3001
```

To also start an ngrok tunnel (needed for Elastic Agent Builder):

```bash
# Add your ngrok auth token to .env:
#   NGROK_AUTHTOKEN=your-token
docker compose --profile tunnel up --build
# ngrok inspector at http://localhost:4040 — copy the public URL from there
```

### Option C: Automated Setup (recommended)

After filling in `.env`, run one command to configure Supabase, Elasticsearch, and Agent Builder:

```bash
git clone https://github.com/StratosL/Athena.git
cd Athena
cp .env.example .env
# Edit .env with your credentials

./setup.sh              # Linux/macOS
setup.bat               # Windows
```

This validates credentials, creates database tables, indexes the vault, registers all 19 tools in Agent Builder, and creates the Athena agent. Run individual phases with `--phase`:

```bash
./setup.sh --phase validate        # check credentials + connectivity
./setup.sh --phase supabase        # create database tables
./setup.sh --phase elasticsearch   # create indices + index vault
./setup.sh --phase agent-builder   # register tools + create agent in Kibana
./setup.sh --phase verify          # end-to-end health checks
```

Then start services: `docker compose --profile tunnel up --build`

### Step 3: Configure Agent Builder in Kibana (manual alternative)

This is the one-time setup that connects everything together. See [`agent-config/setup-guide.md`](agent-config/setup-guide.md) for detailed instructions.

**Summary:**

1. **Create an LLM connector** — Stack Management → Connectors → OpenAI or Anthropic
2. **Create ES|QL tools** — Import the 5 JSON files from `agent-config/tools/` (+ 1 index search tool)
3. **Register the MCP server** — Create an MCP connector pointing to your ngrok URL; it auto-discovers 13 tools
4. **Create the Athena agent** — Paste the system prompt from `agent-config/system-prompt.md`, add all 19 tools
5. **Chat with Athena** — Open the agent in Kibana and start a conversation

### Verify Everything Works

```bash
# MCP server responds to Streamable HTTP
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize",
       "params":{"protocolVersion":"2024-11-05","capabilities":{},
                 "clientInfo":{"name":"test","version":"0.1"}}}'

# Voice proxy is healthy
curl http://localhost:3001/api/health

# Notes are indexed (should return {"count": 17, ...})
curl -s "$ELASTIC_URL/athena-notes/_count" \
  -H "Authorization: ApiKey $ELASTIC_API_KEY"
```

**Test queries in Kibana Agent Builder chat:**

- "What are my notes about the API refactoring?" — semantic search
- "Read my daily note for Feb 12" — direct vault read
- "Extract tasks from the Sprint Review note" — task extraction with Eisenhower classification
- "Plan my day" — 1-3-5 daily planning

---

## Project Structure

```
Athena/
├── services/
│   └── artemis-backend/      # Artemis FastAPI backend (Supabase + tasks)
│       ├── Dockerfile
│       ├── pyproject.toml
│       └── app/
├── frontend/                  # Artemis React frontend (Vite + Tailwind + ChatSidebar)
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── indexer/                   # Obsidian -> Elasticsearch sync (CLI)
├── mcp-server/                # Unified MCP server (13 tools)
├── voice-client/              # Voice-enabled web client + proxy server
├── agent-config/              # Agent Builder configuration
├── sample-vault/              # Demo Obsidian vault (17 notes, 5 folders)
├── docker-compose.yml         # All services, one-command startup
└── .env.example               # All configuration variables
```

---

## Configuration

All settings via environment variables (`.env` file). See [`.env.example`](.env.example) for the full list.

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `ELASTIC_URL` | Yes | — | Elasticsearch Serverless endpoint |
| `ELASTIC_API_KEY` | Yes | — | Elasticsearch API key |
| `VAULT_PATH` | Yes | `/vault` | Path to Obsidian vault |
| `SUPABASE_URL` | For Artemis | — | Supabase project URL |
| `SUPABASE_ANON_KEY` | For Artemis | — | Supabase anonymous key |
| `ARTEMIS_BASE_URL` | No | `http://localhost:8000` | Artemis backend URL |
| `MCP_SERVER_PORT` | No | `8001` | MCP server port |
| `OPENAI_API_KEY` | For voice | — | Whisper STT + TTS |
| `BRAVE_API_KEY` | For research | — | Web search (or `TAVILY_API_KEY`) |

---

## Tool Reference

**19 tools total** — 6 ES|QL (read-only analytics) + 13 MCP (read/write operations).

| Tool | Type | Purpose |
|------|------|---------|
| `search_notes` | ES|QL | Semantic + full-text hybrid search (ELSER) |
| `get_recent_notes` | ES|QL | Notes modified within a time window |
| `get_notes_by_tag` | ES|QL | Filter by tag |
| `count_notes_by_tag` | ES|QL | Tag distribution stats |
| `get_conversation_history` | ES|QL | Recall past conversations |
| `semantic_search` | Index search | Dynamic natural-language query |
| `vault_query` | MCP | List structure, search content, filter by metadata, recent changes |
| `vault_read` | MCP | Read note, read multiple, daily note |
| `vault_manage` | MCP | Create, append, edit, move, delete note, create folder |
| `artemis_create_task` | MCP | Create task with Eisenhower quadrant |
| `artemis_list_tasks` | MCP | List tasks (filter by quadrant/status) |
| `artemis_complete_task` | MCP | Mark task completed |
| `artemis_get_daily_plan` | MCP | Get today's 1-3-5 plan |
| `artemis_assign_to_plan` | MCP | Assign task to major/medium/small slot |
| `artemis_get_analytics` | MCP | Productivity summary (day/week/month) |
| `artemis_start_pomodoro` | MCP | Start a focus session |
| `save_conversation_summary` | MCP | Persist conversation context to ES |
| `web_search` | MCP | Web search via Tavily/Brave API |
| `fetch_url` | MCP | Fetch and extract text from a URL |

---

## Development

```bash
# Lint and format
cd indexer && uv run ruff check src/ && uv run ruff format src/
cd mcp-server && uv run ruff check src/ && uv run ruff format src/

# Type checking
cd indexer && uv run pyright src/
cd mcp-server && uv run pyright src/

# Live vault sync (watches for file changes)
cd indexer && uv run athena-index watch
```

---

## Hackathon

**Event:** [Elasticsearch Agent Builder Hackathon](https://elasticsearch.devpost.com/) | **Deadline:** February 27, 2026 | **Prize Pool:** $20,000

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built by **Stratos Louvaris** for the Elasticsearch Agent Builder Hackathon 2026

Powered by [Elastic Agent Builder](https://www.elastic.co/elasticsearch/agent-builder) · [Elasticsearch](https://www.elastic.co/elasticsearch/serverless) · [Artemis](https://github.com/StratosL/Artemis) · [Obsidian](https://obsidian.md) · [OpenAI](https://platform.openai.com) · [Claude Code](https://claude.ai/claude-code)

</div>
