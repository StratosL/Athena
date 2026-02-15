# Plan: Add Artemis Frontend to Docker Compose (Production Build)

## Context

Currently, `docker compose up` starts three backend services (artemis, mcp-server, voice-proxy), but the Artemis React frontend must be started separately with `npm run dev` in a different terminal. This means the full Athena experience requires two commands and two terminals. With the hackathon demo approaching, consolidating everything into a single `docker compose up` command makes the setup simpler and more reproducible.

## What Changes

Two files touched in the Athena repo. Zero changes to the Artemis repo.

### 1. Create `nginx.conf` (NEW)

**File**: `/home/stardust/Athena/nginx.conf`

This replaces the minimal inline nginx config baked into the Artemis frontend Dockerfile. It adds a reverse proxy for Athena's voice-proxy, matching what the Vite dev server does in development.

```nginx
server {
    listen 3000;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing — all unmatched paths serve index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy Athena API calls to voice-proxy service
    # Mirrors Vite dev proxy: /athena/* → voice-proxy:3001/api/*
    location /athena/ {
        proxy_pass http://voice-proxy:3001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
    }

    # Static asset caching (JS/CSS bundles have content hashes)
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Why this works**: The frontend's `athena-api.ts` uses `const BASE_URL = "/athena"` — all Athena requests go to `/athena/chat`, `/athena/transcribe`, `/athena/speak`. Nginx rewrites these to `http://voice-proxy:3001/api/chat`, etc., using Docker's internal DNS. This is the exact same rewrite the Vite dev proxy does.

**Artemis backend API** (`VITE_API_URL`): Stays as `http://localhost:8000`. The browser makes direct requests to the exposed Artemis port. No proxying needed — this matches the existing behavior.

### 2. Add `artemis-frontend` service to `docker-compose.yml` (MODIFY)

**File**: `/home/stardust/Athena/docker-compose.yml`

Add this service after `voice-proxy`:

```yaml
  # --- Artemis Frontend ---
  artemis-frontend:
    build:
      context: ${ARTEMIS_FRONTEND_PATH:-../Artemis/frontend}
      args:
        - SUPABASE_URL=${SUPABASE_URL:-}
        - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY:-}
        - VITE_API_URL=http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - voice-proxy
    restart: unless-stopped
```

**Key details**:
- **Build context**: Points to `../Artemis/frontend` (configurable via `ARTEMIS_FRONTEND_PATH` env var, same pattern as the existing `artemis` backend service)
- **Build args**: `SUPABASE_URL` and `SUPABASE_ANON_KEY` are injected at build time (Vite bakes them into the JS bundle). `VITE_API_URL=http://localhost:8000` tells the browser where to find the Artemis backend
- **Volume mount**: Overrides the Dockerfile's inline nginx config with our custom one that includes the `/athena` proxy
- **depends_on**: voice-proxy must be up for nginx to resolve the upstream hostname

### 3. Update `.env.example` (MODIFY)

**File**: `/home/stardust/Athena/.env.example`

Add the Supabase variables needed for the frontend build:

```env
# Artemis Frontend (required for Docker build)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
ARTEMIS_FRONTEND_PATH=../Artemis/frontend
```

These values come from the existing Artemis `.env` file at `../Artemis/.env`.

## What Doesn't Change

- **Artemis repo** — zero modifications. The existing Dockerfile, vite.config.ts, and source code are untouched
- **Athena MCP server, voice-proxy, indexer** — no changes
- **Dev workflow** — `npm run dev` still works for frontend development (Vite proxy handles `/athena` in dev)
- **Port 8001** — still exposed for ngrok/Elastic Cloud
- **Port 3001** — still exposed (useful for debugging; can be removed later)

## Result

```
docker compose up --build
```

Starts 4 services:
| Service | Port | Purpose |
|---------|------|---------|
| `artemis` | 8000 | Backend API |
| `mcp-server` | 8001 | MCP tools (vault, artemis, knowledge, research) |
| `voice-proxy` | 3001 | Chat/STT/TTS proxy to Kibana + OpenAI |
| `artemis-frontend` | 3000 | Production React app + nginx (proxies `/athena` to voice-proxy) |

Open `http://localhost:3000` — full Artemis dashboard with Athena chat sidebar, voice, everything.

## Verification

```bash
# Build and start all services
docker compose up --build -d

# Frontend serves the React SPA
curl -s http://localhost:3000 | head -5   # should return HTML

# Athena proxy works through nginx
curl -s http://localhost:3000/athena/health   # should return {"status": "ok"}

# Artemis backend accessible
curl -s http://localhost:8000/health   # should return health response

# MCP server still responds
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1"}}}'
```
