# ADR-004: Monorepo Merge Strategy — Artemis into Athena

**Date:** 2026-02-15
**Status:** Approved — Phase A ready for implementation
**Context:** Artemis (productivity app) and Athena (AI agent) are tightly coupled but live in separate git repos. Evaluate how to merge them for hackathon submission and long-term maintainability.

---

## Motivation

The two projects are coupled in practice but separated in git:

- Athena's `docker-compose.yml` builds Artemis via `${ARTEMIS_PATH:-../Artemis/backend}` and `${ARTEMIS_FRONTEND_PATH:-../Artemis/frontend}`
- Artemis's frontend contains **18 files** referencing Athena directly: `useAthenaChat.ts`, `useAthenaVoice.ts`, `athena-api.ts`, `ChatSidebar/`, `chatStore.ts`, `useVoiceRecorder.ts`, etc.
- Anyone cloning just Athena gets a broken `docker compose up`
- Hackathon judges need a single repo that works out of the box
- Future features (memory system, heartbeat service) will further blur the boundary

### Current Repository State

**Artemis** (`/home/stardust/Artemis/`):
- `backend/` — FastAPI + Supabase, own `pyproject.toml`, Dockerfile, `uv.lock`
- `frontend/` — React + Vite + TypeScript, own `package.json`, Dockerfile
- Root-level `docker-compose.yml`, own `.git` repo

**Athena** (`/home/stardust/Athena/`):
- `mcp-server/` — FastMCP server (13 MCP tools), own `pyproject.toml`, `uv.lock`
- `indexer/` — Elasticsearch sync CLI, own `pyproject.toml`, `uv.lock`
- `voice-client/` — HTML/JS voice proxy + serve.py, own Dockerfile
- `agent-config/` — Agent Builder system prompt + ES|QL tool definitions
- `docker-compose.yml` referencing Artemis via relative `../Artemis/` paths

---

## Approaches Evaluated

### 1. Full Monorepo (Bazel/Nx/Pants)

Google uses Bazel, Meta uses Buck2, Microsoft uses Rush/Lage. All require dedicated build-infra teams, BUILD files, and steep learning curves. Designed for 1000+ engineers.

- **Setup time**: 2-3 days
- **Deadline risk**: HIGH
- **Long-term**: Excellent
- **Verdict**: Overkill for a solo dev. Solving problems we don't have.

### 2. Git Subtree / Submodule

Subtree copies code in with history. Submodule pins a commit pointer.

- **Setup time**: 30 min
- **Deadline risk**: Medium
- **Long-term**: Poor (submodule friction) / Mediocre (subtree merge conflicts)
- **Verdict**: Submodule requires `--recursive` clone (bad for judges). Subtree is viable as a mechanism for Phase A but isn't a long-term architecture.

### 3. Copy Needed Files

Cherry-pick Artemis files into Athena. Maintain two copies.

- **Setup time**: 1 hour
- **Deadline risk**: Low
- **Long-term**: Terrible — two copies, guaranteed drift, no canonical source
- **Verdict**: Only acceptable if Artemis is frozen forever. It isn't.

### 4. Fresh Start (Rewrite)

New repo, clean structure, move code from both projects.

- **Setup time**: 3-5 days
- **Deadline risk**: VERY HIGH
- **Long-term**: Excellent
- **Verdict**: The same end state can be reached incrementally. Rewriting under deadline pressure is the wrong move.

### 5. uv Workspaces + Docker Compose (CHOSEN)

Single repo, native workspace tools (`uv` for Python, standard `package.json` for TypeScript), Docker Compose for orchestration. No build orchestrators.

- **Setup time**: 2-4 hours
- **Deadline risk**: LOW
- **Long-term**: Very good
- **Verdict**: The pragmatic choice. Matches what most startups with < 50 engineers do.

---

## Decision: Two-Phase Workspace Monorepo

### Phase A — Before Hackathon Deadline (2-4 hours)

Bring Artemis code into Athena via `git subtree add`. Update paths. Verify Docker Compose works.

**Target structure:**

```
Athena/
├── services/
│   └── artemis-backend/     ← git subtree add from Artemis/backend
│       ├── pyproject.toml
│       ├── Dockerfile
│       └── app/
├── frontend/                ← git subtree add from Artemis/frontend
│   ├── package.json
│   ├── Dockerfile
│   └── src/
│       ├── ... (existing Artemis code)
│       ├── lib/athena-api.ts
│       ├── stores/chatStore.ts
│       ├── hooks/useAthenaChat.ts
│       ├── hooks/useAthenaVoice.ts
│       ├── hooks/useVoiceRecorder.ts
│       └── design-system/.../ChatSidebar/
├── mcp-server/              ← unchanged
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── src/
├── indexer/                 ← unchanged
│   ├── pyproject.toml
│   └── src/
├── voice-client/            ← unchanged
│   ├── Dockerfile
│   └── ...
├── agent-config/            ← unchanged
├── sample-vault/            ← unchanged
├── docker-compose.yml       ← update paths
├── nginx.conf               ← unchanged
├── .env.example             ← consolidate all vars
└── .env
```

**Steps:**

1. `git subtree add --prefix=services/artemis-backend <artemis-remote> main --squash` (backend)
2. `git subtree add --prefix=frontend <artemis-remote> main --squash` (frontend)
   - Alternative: since we only need `backend/` and `frontend/` subdirs, we may need to subtree from the Artemis root and then reorganize, OR simply copy + commit with a message referencing the source commit hash
3. Update `docker-compose.yml`:
   - `artemis` service: `context: ./services/artemis-backend` (was `${ARTEMIS_PATH:-../Artemis/backend}`)
   - `artemis-frontend` service: `context: ./frontend` (was `${ARTEMIS_FRONTEND_PATH:-../Artemis/frontend}`)
   - Remove `ARTEMIS_PATH`, `ARTEMIS_FRONTEND_PATH` env vars
   - Update `env_file` for artemis service (was `${ARTEMIS_ENV_FILE:-../Artemis/.env}`)
4. Move Artemis's required `.env` vars into Athena's `.env.example`
5. Update `README.md` setup instructions (no more sibling directory requirement)
6. Verify: `docker compose up --build` starts all 4 services
7. Verify: MCP server can reach Artemis backend via Docker network
8. Verify: Frontend builds and serves with Athena ChatSidebar working

**What does NOT change in Phase A:**
- Each Python service keeps its own `.venv` and `uv.lock`
- No `pyproject.toml` changes
- No code changes to any Python or TypeScript source files
- Dockerfiles stay the same (they use relative paths within their own context)

### Phase B — After Hackathon (post-Feb 27)

1. Add root `pyproject.toml` with `[tool.uv.workspace]`:
   ```toml
   [project]
   name = "athena-workspace"
   version = "0.1.0"
   requires-python = ">=3.12"

   [tool.uv.workspace]
   members = [
       "services/artemis-backend",
       "services/mcp-server",
       "services/indexer",
   ]
   ```
2. Move `mcp-server/` → `services/mcp-server/`, `indexer/` → `services/indexer/`
3. Extract shared code (pydantic models, config patterns) into `packages/shared/`
4. Replace 3 individual `uv.lock` files with single root `uv.lock`
5. Add `Makefile` or `justfile` for common tasks (`make dev`, `make test`, `make build`)
6. Decide whether Artemis needs to remain a standalone project; if not, simplify further

---

## Alternatives Rejected

| Approach | Why Rejected |
|----------|-------------|
| Bazel/Nx/Pants | Overkill for solo dev. Steep learning curve. Days of setup. |
| Git submodule | Judges need `--recursive` clone. Constant friction. Boundary isn't clean (18 cross-project files). |
| Copy files | Two copies = guaranteed drift. No canonical source. Technical debt. |
| Fresh start | 3-5 days of zero feature output under deadline pressure. Same end state achievable incrementally. |
| Turborepo | JS/TS only. Zero Python awareness. Not applicable. |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Subtree add creates merge conflicts | Low | Medium | Use `--squash` to flatten Artemis history into one commit |
| Dockerfile paths break after move | Medium | Low | Dockerfiles use relative paths within their own `context:` — context changes, not Dockerfile |
| `.env` consolidation misses a variable | Medium | Medium | Diff Artemis `.env.example` against Athena `.env.example` before merging |
| Frontend build breaks | Low | Medium | Run `npm run build` immediately after subtree add to verify |
| Artemis backend needs its own `.env` format | Medium | Low | Keep `env_file` pointing to root `.env`; add any Artemis-specific vars |

---

## References

- [uv Workspaces Documentation](https://docs.astral.sh/uv/concepts/projects/workspaces/)
- [Apache Airflow: 120+ packages in uv workspace monorepo](https://fosdem.org/2026/schedule/event/WE7NHM-modern-python-monorepo-apache-airflow/)
- [uv-monorepo template (GitHub)](https://github.com/JasperHG90/uv-monorepo)
- [Monorepo Tools Comparison](https://monorepo.tools/)
- [Git Subtree vs Submodule](https://adam-p.ca/blog/2022/02/git-submodule-subtree/)
- ADR-003 (OpenClaw patterns) — memory/heartbeat features that will become new workspace members

---

*Decision made: 2026-02-15*
*Implementation: Phase A before Feb 27 deadline, Phase B after hackathon*
