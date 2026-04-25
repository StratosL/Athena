# Feature: Monorepo Merge — Artemis into Athena

The following plan should be complete, but validate documentation and codebase patterns before implementing.

## Context

Athena and Artemis are tightly coupled but live in separate git repos. Athena's `docker-compose.yml` references Artemis via `../Artemis/` paths — anyone cloning just Athena gets a broken `docker compose up`. Hackathon judges need a single repo that works out of the box. ADR-004 decided to merge Artemis into Athena before the Feb 27 deadline.

## Feature Description

Copy the Artemis backend (58 tracked files) and frontend (122 tracked files) into the Athena repo, update Docker Compose to use local paths, and remove all cross-repo path references. No source code changes required.

## User Story

As a hackathon judge (or contributor)
I want to clone a single repo and run `docker compose up`
So that the entire Athena + Artemis stack works without sibling directory setup

## Problem Statement

Cloning Athena alone produces a broken Docker Compose setup. The `artemis` and `artemis-frontend` services reference `../Artemis/backend` and `../Artemis/frontend` via env vars, requiring a specific sibling directory layout.

## Solution Statement

Copy Artemis's `backend/` → `services/artemis-backend/` and `frontend/` → `frontend/` using `git ls-files` (tracked files only). Update 5 config files to remove cross-repo paths. Zero source code changes.

## Feature Metadata

**Feature Type**: Refactor
**Estimated Complexity**: Low-Medium
**Primary Systems Affected**: docker-compose.yml, .env.example, .gitignore, README.md, CLAUDE.md
**Dependencies**: Artemis repo at commit `4ee701f`

---

## CONTEXT REFERENCES

### Relevant Codebase Files — READ BEFORE IMPLEMENTING

- `/home/stardust/Athena/docker-compose.yml` — Primary edit target. Lines 15, 19, 61 reference `../Artemis/`
- `/home/stardust/Athena/.env.example` — Line 37 has `ARTEMIS_FRONTEND_PATH=../Artemis/frontend` to remove
- `/home/stardust/Athena/.gitignore` — Python-only, needs Node.js patterns
- `/home/stardust/Athena/README.md` — Lines 64, 168+ reference Artemis as external dependency
- `/home/stardust/Athena/CLAUDE.md` — Lines 22-35 show project structure to update
- `/home/stardust/Athena/decisions/004-monorepo-merge-strategy.md` — ADR with full rationale
- `/home/stardust/Artemis/backend/Dockerfile` — Uses relative `COPY` within its own context (no changes needed)
- `/home/stardust/Artemis/frontend/Dockerfile` — Same (no changes needed)
- `/home/stardust/Artemis/frontend/vite.config.ts` — `envDir: ".."` resolves to Athena root after merge (works)
- `/home/stardust/Artemis/backend/app/core/config.py:12` — `env_file="../.env"` (works: Docker uses compose env_file; local dev `../` → Athena root)

### New Directories to Create

- `services/artemis-backend/` — Artemis FastAPI backend (copied from Artemis/backend/)
- `frontend/` — Artemis React frontend (copied from Artemis/frontend/)

### Why No Source Code Changes

1. **Backend Dockerfile**: `COPY pyproject.toml uv.lock README.md ./` + `COPY app/ ./app/` — all relative to build context. Changing `context:` in compose is transparent.
2. **Backend config.py**: `env_file="../.env"` — in Docker, env vars come from compose `env_file:` directive. For local dev, `../` resolves to Athena root (has `.env`). Same behavior as before.
3. **Frontend vite.config.ts**: `envDir: ".."` — during Docker build, env vars come from `ARG`/`ENV`. During `npm run dev`, `..` resolves to Athena root (has `.env` with SUPABASE vars). Works.
4. **Frontend Dockerfile**: `COPY . .` copies context. Build uses `ARG` env vars. No path assumptions.
5. **MCP server**: Uses `ARTEMIS_BASE_URL=http://artemis:8000` (Docker service name). No filesystem refs.
6. **nginx.conf**: Volume-mounted from repo root. Path unchanged.

---

## IMPLEMENTATION PLAN

### Phase 1: Copy Files

Copy tracked files only (no `.venv/`, `node_modules/`, `__pycache__/`, cache dirs) from Artemis into Athena.

### Phase 2: Update Config Files

Edit 5 files: docker-compose.yml, .env.example, .gitignore, README.md, CLAUDE.md.

### Phase 3: Verify

Validate compose config, Docker builds, and optionally full stack startup.

### Phase 4: Commit

Single commit referencing Artemis source commit hash.

---

## STEP-BY-STEP TASKS

### Task 1: Pre-flight checks

- **VALIDATE**: Athena working tree is clean
  ```bash
  cd /home/stardust/Athena && git status --short
  ```
- **VALIDATE**: Artemis HEAD is `4ee701f`
  ```bash
  cd /home/stardust/Artemis && git rev-parse --short HEAD
  ```
- **VALIDATE**: Target dirs don't exist yet
  ```bash
  test ! -d /home/stardust/Athena/services && test ! -d /home/stardust/Athena/frontend && echo "OK"
  ```

### Task 2: Copy Artemis backend → services/artemis-backend/

- **IMPLEMENT**: Use `git ls-files` to copy only tracked files, preserving directory structure
  ```bash
  cd /home/stardust/Artemis && \
    git ls-files backend/ | while IFS= read -r f; do
      dest="/home/stardust/Athena/services/artemis-backend/${f#backend/}"
      mkdir -p "$(dirname "$dest")"
      cp "$f" "$dest"
    done
  ```
- **VALIDATE**: File count matches (58 files)
  ```bash
  find /home/stardust/Athena/services/artemis-backend -type f | wc -l
  ```
- **VALIDATE**: Key files exist
  ```bash
  ls /home/stardust/Athena/services/artemis-backend/{Dockerfile,pyproject.toml,uv.lock,README.md,app/main.py}
  ```

### Task 3: Copy Artemis frontend → frontend/

- **IMPLEMENT**: Use `git ls-files` to copy only tracked files
  ```bash
  cd /home/stardust/Artemis && \
    git ls-files frontend/ | while IFS= read -r f; do
      dest="/home/stardust/Athena/${f}"
      mkdir -p "$(dirname "$dest")"
      cp "$f" "$dest"
    done
  ```
- **VALIDATE**: File count matches (122 files)
  ```bash
  find /home/stardust/Athena/frontend -type f | wc -l
  ```
- **VALIDATE**: Key files exist
  ```bash
  ls /home/stardust/Athena/frontend/{Dockerfile,package.json,package-lock.json,vite.config.ts,src/App.tsx}
  ```

### Task 4: UPDATE docker-compose.yml

Three edits to remove cross-repo path indirection:

**4a — Artemis backend build context** (line 15-16):
```yaml
# BEFORE
    build:
      context: ${ARTEMIS_PATH:-../Artemis/backend}
# AFTER
    build:
      context: ./services/artemis-backend
```

**4b — Artemis backend env_file** (line 18-19):
```yaml
# BEFORE
    env_file:
      - ${ARTEMIS_ENV_FILE:-../Artemis/.env}
# AFTER
    env_file:
      - .env
```

**4c — Artemis frontend build context** (line 61):
```yaml
# BEFORE
    build:
      context: ${ARTEMIS_FRONTEND_PATH:-../Artemis/frontend}
# AFTER
    build:
      context: ./frontend
```

- **GOTCHA**: Do NOT change anything else. The mcp-server and voice-proxy `env_file: .env` are already correct. The nginx volume mount `./nginx.conf:/etc/nginx/conf.d/default.conf:ro` is unchanged.
- **VALIDATE**:
  ```bash
  cd /home/stardust/Athena && docker compose config > /dev/null && echo "PASS"
  ```

### Task 5: UPDATE .env.example

**5a** — Remove the `ARTEMIS_FRONTEND_PATH` line and its comment:
```
# REMOVE these lines:
# --- Artemis Frontend (required for Docker build) ---
...
ARTEMIS_FRONTEND_PATH=../Artemis/frontend
```

**5b** — Reorganize the Artemis section. The final Artemis-related block should look like:
```env
# --- Artemis ---
ARTEMIS_BASE_URL=http://localhost:8000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
CORS_ORIGINS=http://localhost:3000
```

- **GOTCHA**: `ARTEMIS_BASE_URL` already exists at line 19. Move Supabase vars to be with it, remove the old "Artemis Frontend" section header, add `CORS_ORIGINS`.
- **VALIDATE**: Visual review — no `../Artemis` references remain.

### Task 6: UPDATE .gitignore

Add Node.js / frontend patterns at the end:
```gitignore
# Node / Frontend
node_modules/
npm-debug.log*
frontend/dist/
*.tsbuildinfo
```

- **VALIDATE**:
  ```bash
  cd /home/stardust/Athena && grep "node_modules" .gitignore && echo "PASS"
  ```

### Task 7: UPDATE README.md

**7a** — Prerequisites section (~line 64): Change Artemis from external dependency to included:
```markdown
# BEFORE
- **[Artemis](https://github.com/StratosL/Artemis)** running locally on port 8000 (optional — Athena handles it being unavailable)

# AFTER
- **Artemis** is included in this repository (`services/artemis-backend/` + `frontend/`)
```

**7b** — Project Structure section (~line 168): Update tree to show new layout:
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

### Task 8: UPDATE CLAUDE.md

Update the Project Structure section (~lines 22-35) to reflect the new layout. Add `services/artemis-backend/` and `frontend/` entries:

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
├── devpost/               ← Hackathon submission materials
│
└── reference/             ← Inspiration codebases (READ-ONLY, never modify)
```

### Task 9: Verify Docker builds

```bash
cd /home/stardust/Athena

# Config parses
docker compose config > /dev/null && echo "PASS: config"

# Backend image builds
docker compose build artemis && echo "PASS: backend build"

# Frontend image builds
docker compose build artemis-frontend && echo "PASS: frontend build"
```

- **GOTCHA**: If Supabase credentials are not in `.env`, the backend container will start but fail at runtime (Supabase connection error). The Docker _build_ itself doesn't need Supabase — only the frontend build needs `SUPABASE_URL`/`SUPABASE_ANON_KEY` as build args (and those have empty-string defaults in compose, so the build succeeds even without them).

### Task 10: Commit

Stage all new and modified files, commit with provenance reference:

```bash
cd /home/stardust/Athena
git add services/artemis-backend/ frontend/
git add docker-compose.yml .env.example .gitignore README.md CLAUDE.md
git commit -m "$(cat <<'EOF'
feat(monorepo): merge Artemis backend + frontend into Athena repo

Copy tracked files from Artemis repo at commit 4ee701f:
- backend/ (58 files) → services/artemis-backend/
- frontend/ (122 files) → frontend/

Update docker-compose.yml to use local paths instead of ../Artemis/
env var indirection. Update .env.example, .gitignore, README.md, CLAUDE.md.

No source code changes — Dockerfiles, pyproject.toml, package.json,
and vite.config.ts all work unchanged in the new layout.

Ref: ADR-004 Phase A (decisions/004-monorepo-merge-strategy.md)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## VALIDATION COMMANDS

### Level 1: Config Syntax

```bash
cd /home/stardust/Athena && docker compose config > /dev/null && echo "PASS"
```

### Level 2: File Integrity

```bash
# Backend file count
test $(find services/artemis-backend -type f | wc -l) -eq 58 && echo "PASS: backend files"

# Frontend file count
test $(find frontend -type f | wc -l) -eq 122 && echo "PASS: frontend files"

# No ../Artemis references in config files
grep -r "../Artemis" docker-compose.yml .env.example && echo "FAIL" || echo "PASS: no cross-repo refs"
```

### Level 3: Docker Builds

```bash
docker compose build artemis && echo "PASS: backend"
docker compose build artemis-frontend && echo "PASS: frontend"
```

### Level 4: Full Stack (optional, needs .env credentials)

```bash
docker compose up -d
sleep 15
docker compose ps
curl -sf http://localhost:8000/health && echo " PASS: backend"
curl -sf http://localhost:3000 > /dev/null && echo " PASS: frontend"
curl -sf http://localhost:8001/ > /dev/null && echo " PASS: mcp-server" || true
docker compose down
```

---

## ACCEPTANCE CRITERIA

- [x] `services/artemis-backend/` contains 58 tracked files from Artemis backend
- [x] `frontend/` contains 122 tracked files from Artemis frontend
- [x] `docker compose config` parses without errors
- [x] No `../Artemis` references remain in docker-compose.yml or .env.example
- [x] `.gitignore` includes `node_modules/` and `frontend/dist/`
- [x] README.md no longer lists Artemis as external prerequisite
- [x] CLAUDE.md project structure reflects new layout
- [x] `docker compose build` succeeds for artemis and artemis-frontend services
- [x] No Python or TypeScript source code was modified
- [x] Commit message references Artemis source commit hash (4ee701f)

## NOTES

- **Phase B** (post-hackathon): Add root `pyproject.toml` with `[tool.uv.workspace]`, move mcp-server/ and indexer/ under services/, extract shared packages. See ADR-004.
- **No `git subtree`**: ADR-004 mentions subtree, but it imports the entire repo (we only need 2 subdirs). Copy + commit is cleaner for the hackathon. The commit message preserves provenance.
- **Artemis `.env` consolidation**: All Artemis env vars (Supabase, CORS, APP_NAME) are now served from Athena's root `.env`. The backend's `env_file="../.env"` in config.py still works (local dev: `../` = Athena root; Docker: compose `env_file:` overrides).
