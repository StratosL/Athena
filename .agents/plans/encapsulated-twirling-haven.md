# Setup Automation — One-Command Project Bootstrap

## Context

Setting up Athena requires 5+ manual steps across 4 different services (Supabase, Elasticsearch, Agent Builder, Docker). A new user must: create Supabase tables, create ES indices, index the vault, create 7 Agent Builder tools, register an MCP connector, create the Athena agent, and start Docker. This is error-prone and takes 30+ minutes.

**Goal**: After filling in `.env`, run one command (`./setup.sh` or `setup.bat`) and everything is configured automatically.

**Pattern**: Follows the Arete project's automation approach — thin shell entry points delegating to Python scripts, ordered SQL migrations, validate→setup→verify pipeline.

## File Structure

```
scripts/
├── setup.py              # Main orchestrator — runs all phases
├── validate_env.py       # Phase 1: validate credentials + connectivity
├── setup_supabase.py     # Phase 2a: create tables via Supabase REST API
├── setup_elasticsearch.py # Phase 2b: create indices + index vault
├── setup_agent_builder.py # Phase 2c: create tools + connector + agent in Kibana
├── verify.py             # Phase 3: end-to-end health checks
└── config.py             # Shared config (pydantic-settings, reuses .env)

supabase/
└── migrations/
    └── 001_initial_schema.sql  # Tables + triggers + RLS + RPC function

setup.sh                  # Linux/macOS entry point
setup.bat                 # Windows entry point
```

## Implementation Plan

### 1. `scripts/config.py` — Shared Configuration

Pydantic-settings class loading from root `.env`. All scripts import this.

```python
class SetupConfig(BaseSettings):
    elastic_url: str = ""
    elastic_api_key: str = ""
    vault_path: str = "./sample-vault"
    notes_index: str = "athena-notes"
    conversations_index: str = "athena-conversations"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    openai_api_key: str = ""
    ngrok_domain: str = ""
    mcp_server_port: int = 8001

    @property
    def kibana_url(self) -> str:
        return self.elastic_url.replace(".es.", ".kb.")

    model_config = {"env_file": ("../.env", ".env"), "extra": "ignore"}
```

### 2. `supabase/migrations/001_initial_schema.sql`

Full SQL migration with all 3 tables, triggers, RLS policies, and the `increment_pomodoro_count` RPC function. Idempotent (`CREATE TABLE IF NOT EXISTS`, `CREATE OR REPLACE FUNCTION`).

Tables derived from existing Artemis schemas:
- `tasks` (id uuid PK, title text, description text, quadrant int 1-4, status text default 'pending', due_date timestamptz, pomodoro_count int default 0, created_at, updated_at, completed_at)
- `daily_plans` (id uuid PK, date date UNIQUE, major_task_id uuid FK, medium_task_ids uuid[], small_task_ids uuid[], created_at, updated_at)
- `pomodoro_sessions` (id uuid PK, task_id uuid FK, started_at, ended_at, duration_minutes int default 25, completed bool, interrupted bool, created_at, updated_at)

### 3. `scripts/validate_env.py` — Phase 1: Validate

Checks all required credentials and tests connectivity:

1. Check required env vars are set: `ELASTIC_URL`, `ELASTIC_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`
2. Test Elasticsearch connectivity: `GET /` with API key auth
3. Test Supabase connectivity: `GET /rest/v1/` with anon key
4. Check optional vars and warn if missing: `OPENAI_API_KEY` (voice won't work), `BRAVE_API_KEY`/`TAVILY_API_KEY` (web search won't work), `NGROK_DOMAIN` (Agent Builder setup will be skipped)
5. Fail-fast with specific error messages and signup URLs on failure

Uses `httpx` (sync) for connectivity checks.

### 4. `scripts/setup_supabase.py` — Phase 2a: Database

**Requires `SUPABASE_SERVICE_KEY`** (service role key from Supabase dashboard → Settings → API → service_role key). This key has full DDL permissions.

**Steps**:
1. Read `supabase/migrations/001_initial_schema.sql`
2. Connect to Supabase PostgreSQL directly using the connection string derived from `SUPABASE_URL`:
   - Extract project ref from URL: `https://abcdef.supabase.co` → `abcdef`
   - Connection string: `postgresql://postgres.{ref}:{service_key}@aws-0-{region}.pooler.supabase.com:5432/postgres`
   - **However**, this requires `psycopg2` which has C dependencies — not ideal
3. **Better approach**: Use Supabase's `pg_meta` REST API which accepts raw SQL via service key:
   - `POST {SUPABASE_URL}/pg/query` with `Authorization: Bearer {SERVICE_KEY}` and body `{"query": "SQL..."}`
   - This is the same API the Supabase SQL Editor uses
   - **Actually**, the simplest approach: use `supabase-py` SDK with the service key and call `client.postgrest.rpc()` — but this can't run DDL either.
4. **Final approach**: Use httpx to POST to the Supabase Management API:
   - `POST https://api.supabase.com/v1/projects/{ref}/database/query` requires a Supabase access token (not service key)
   - **This won't work either** — the Management API needs an OAuth token from `supabase login`.

**Actual simplest reliable approach**: Connect directly to Postgres via the pooler URL using `psycopg` (pure Python, no C deps). Add `psycopg[binary]>=3.1.0` to the scripts dependencies.

```python
import psycopg

# Supabase provides a direct Postgres connection via pooler
# URL: postgresql://postgres.{ref}:[PASSWORD]@aws-0-{region}.pooler.supabase.com:6543/postgres
conn = psycopg.connect(supabase_db_url)
conn.execute(open("supabase/migrations/001_initial_schema.sql").read())
conn.commit()
```

**Config**: Add `SUPABASE_DB_URL` to `.env.example`. The user copies this from Supabase dashboard → Settings → Database → Connection string (URI) → Transaction pooler. This is the most straightforward path — one connection string, pure Python driver, no auth complexity.

**Fallback**: If `SUPABASE_DB_URL` is not set, print the SQL and instructions to paste it in the Supabase SQL Editor.

**Verification**: After execution (either path), verify tables exist via REST API:
- `GET {SUPABASE_URL}/rest/v1/tasks?limit=0` with anon key headers

### 5. `scripts/setup_elasticsearch.py` — Phase 2b: Indices + Indexing

Invokes the existing indexer CLI as a subprocess:

```python
subprocess.run(["uv", "run", "athena-index", "setup-indices"], cwd="indexer/", check=True)
subprocess.run(["uv", "run", "athena-index", "index"], cwd="indexer/", check=True)
```

Before running:
1. Check `uv` is installed
2. Run `uv sync` in `indexer/` to install dependencies
3. Run `setup-indices` to create ES indices
4. Run `index` to bulk-index the sample vault
5. Verify: query `athena-notes/_count` and check count > 0

### 6. `scripts/setup_agent_builder.py` — Phase 2c: Kibana Configuration

This is the most complex script. Uses httpx to call the Kibana REST API.

**Steps**:

1. **Create ES|QL tools** (5) + Index Search tool (1):
   - Read each JSON from `agent-config/tools/*.json`
   - `POST /api/agent_builder/tools` for each
   - Handle 409 (already exists) gracefully — skip or update
   - Collect all tool IDs

2. **Create/update MCP connector + register MCP tools** (skipped if ngrok not running):
   - First, check if `NGROK_DOMAIN` is set and MCP server is reachable at `https://{NGROK_DOMAIN}/`
   - **If not reachable**: skip MCP connector + MCP tools entirely. Print message:
     ```
     ⚠ MCP server not reachable at https://{NGROK_DOMAIN}
       Run: docker compose --profile tunnel up --build
       Then re-run: ./setup.sh --phase agent-builder
     ```
   - **If reachable**:
     - `POST /api/actions/connector` with `connector_type_id: ".mcp"`, `config.serverUrl`
     - Save connector ID
     - Register 13 MCP tools with `type: "mcp"`, `configuration.connector_id`, `configuration.tool_name`
     - Tool names: `vault_query`, `vault_read`, `vault_manage`, `artemis_create_task`, `artemis_list_tasks`, `artemis_complete_task`, `artemis_get_daily_plan`, `artemis_assign_to_plan`, `artemis_get_analytics`, `artemis_start_pomodoro`, `save_conversation_summary`, `web_search`, `fetch_url`
     - Tool IDs: `athena.{tool_name}`

3. **Create/update Athena agent**:
   - Read system prompt from `agent-config/system-prompt.md`
   - Collect all tool IDs created so far (ES|QL + index search + MCP if available)
   - Try `GET /api/agent_builder/agents/athena` first to check if agent exists
   - If exists: `PUT /api/agent_builder/agents/athena` (without `id` in body)
   - If not: `POST /api/agent_builder/agents` (with `id: "athena"` in body)
   - Configuration: `instructions` = system prompt, `tools` = `[{"tool_ids": [...]}]`

**Key patterns from api-reference.md**:
- Auth: `Authorization: ApiKey {key}`, `kbn-xsrf: true`
- Kibana URL derived from ES URL: replace `.es.` with `.kb.`
- Agent creation: `instructions` not `system_prompt`, no `id` in PUT body
- MCP connector: `serverUrl` (camelCase), endpoint is `/api/actions/connector`

### 7. `scripts/verify.py` — Phase 3: End-to-End Verification

Quick health checks after setup:

| Check | Method |
|-------|--------|
| Supabase tables exist | `GET /rest/v1/tasks?limit=0` (200 OK) |
| ES indices exist | `GET /athena-notes/_count` (count > 0) |
| ES|QL tools registered | `GET /api/agent_builder/tools` (count >= 6) |
| Agent exists | `GET /api/agent_builder/agents/athena` (200 OK) |
| MCP connector (if ngrok set) | `GET /api/actions/connector/{id}` |
| Docker services (if running) | `GET http://localhost:8000/health`, `GET http://localhost:3001/api/health` |

Print a summary table (pass/fail/skip for each check).

### 8. `scripts/setup.py` — Main Orchestrator

Runs all phases in sequence with colored output (using `rich` which is already in the indexer deps):

```
Phase 1/3: Validating environment...
  ✓ ELASTIC_URL set
  ✓ ELASTIC_API_KEY set
  ✓ Elasticsearch reachable
  ✓ SUPABASE_URL set
  ✓ SUPABASE_ANON_KEY set
  ✓ Supabase reachable
  ⚠ OPENAI_API_KEY not set (voice features disabled)

Phase 2/3: Setting up services...
  [2a] Supabase database...
    → Tables created (or already exist)
  [2b] Elasticsearch indices...
    → athena-notes created, 17 notes indexed
    → athena-conversations created
  [2c] Agent Builder (Kibana)...
    → 6 ES|QL tools created
    → MCP connector registered (https://your-domain.ngrok-free.dev)
    → 13 MCP tools registered
    → Athena agent created (19 tools, 14.5k char system prompt)

Phase 3/3: Verifying...
  ✓ Supabase: 3 tables accessible
  ✓ Elasticsearch: 17 notes indexed
  ✓ Agent Builder: Athena agent ready (19 tools)

Setup complete! Next steps:
  docker compose --profile tunnel up --build
```

CLI flags for running individual phases:
- `--phase validate` — only validate
- `--phase supabase` — only database setup
- `--phase elasticsearch` — only ES setup
- `--phase agent-builder` — only Kibana setup
- `--phase verify` — only verification
- No flag = run all phases

### 9. `setup.sh` — Linux/macOS Entry Point

```bash
#!/usr/bin/env bash
set -e

# Check .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found."
    echo "Run: cp .env.example .env"
    echo "Then fill in your credentials and run this script again."
    exit 1
fi

# Check Python 3.12+
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 not found. Install from https://www.python.org/downloads/"
    exit 1
fi

# Check uv
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found. Install from https://docs.astral.sh/uv/"
    exit 1
fi

# Install setup script dependencies
cd scripts && uv sync && cd ..

# Run the setup
uv run --project scripts python -m scripts.setup "$@"
```

### 10. `setup.bat` — Windows Entry Point

Same logic as `setup.sh` but in batch. Checks for `.env`, Python, `uv`, then delegates to the Python orchestrator.

### 11. `scripts/pyproject.toml` — Setup Scripts Sub-project

```toml
[project]
name = "athena-setup"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27.0",
    "pydantic-settings>=2.5.0",
    "python-dotenv>=1.0.0",
    "rich>=13.9.0",
    "psycopg[binary]>=3.1.0",
]
```

Deps: httpx (API calls), pydantic-settings (config), rich (output), psycopg (Supabase Postgres DDL). Does NOT import the indexer or MCP server — invokes them via subprocess.

## Files to Create (12 total)

| File | Lines (est.) | Purpose |
|------|-------------|---------|
| `setup.sh` | ~25 | Linux/macOS entry point |
| `setup.bat` | ~30 | Windows entry point |
| `scripts/pyproject.toml` | ~25 | Sub-project definition |
| `scripts/__init__.py` | ~1 | Package marker |
| `scripts/config.py` | ~40 | Shared configuration |
| `scripts/setup.py` | ~120 | Main orchestrator |
| `scripts/validate_env.py` | ~100 | Credential validation + connectivity |
| `scripts/setup_supabase.py` | ~80 | Database table creation/verification |
| `scripts/setup_elasticsearch.py` | ~60 | ES indices + vault indexing via subprocess |
| `scripts/setup_agent_builder.py` | ~200 | Kibana API: tools + connector + agent |
| `scripts/verify.py` | ~100 | End-to-end health checks |
| `supabase/migrations/001_initial_schema.sql` | ~80 | Full database schema |

## Files to Modify (2)

| File | Change |
|------|--------|
| `.env.example` | Add `SUPABASE_DB_URL` (Postgres connection string for DDL execution) |
| `README.md` | Add "Automated Setup" section pointing to `setup.sh`/`setup.bat` |

## Verification

After implementation, test the full pipeline:

1. `cp .env.example .env` and fill in real credentials
2. Run `./setup.sh` — all phases should pass
3. Run `./setup.sh` again — idempotent, no errors on second run
4. Run `./setup.sh --phase verify` — all checks pass
5. Run `docker compose --profile tunnel up --build` — services start
6. Open Kibana → Agent Builder → chat with Athena — tools work

## Supabase DDL Strategy

**Primary path (automated)**: Requires `SUPABASE_DB_URL` in `.env` — the Postgres transaction pooler connection string from Supabase dashboard (Settings → Database → Connection string → URI → Transaction mode). Uses `psycopg` (pure Python Postgres driver) to connect and execute the SQL migration directly.

**Fallback (manual)**: If `SUPABASE_DB_URL` is not set, print the SQL migration content and instructions to paste it into the Supabase SQL Editor (with the URL to open).

**Verification (both paths)**: After execution, confirm tables exist via the Supabase REST API with the anon key:
- `GET {SUPABASE_URL}/rest/v1/tasks?limit=0` → 200 means table exists
- `GET {SUPABASE_URL}/rest/v1/daily_plans?limit=0` → 200
- `GET {SUPABASE_URL}/rest/v1/pomodoro_sessions?limit=0` → 200
