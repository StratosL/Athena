# Feature: Voice Client — Whisper STT + OpenAI TTS

Read all referenced files and documentation links before implementing. Validate names, imports, and patterns against the actual codebase.

## Context

Athena is a conversational AI agent on Elastic Agent Builder (hackathon, deadline Feb 27). Phases 1-2 are complete — the agent is deployed with 19 tools in Kibana, searching/reading the Obsidian vault and managing tasks in Artemis. The voice client (Phase 3) adds speech input/output so the user can **talk** to Athena and **hear** responses, creating the demo "wow factor."

## Problem Statement

The agent currently only works through Kibana's built-in chat UI. For the demo video, we need a standalone voice interface that captures speech, sends it to the agent, and speaks the response — all without modifying the backend.

## Solution

A thin web client (vanilla HTML/JS/CSS) served by a small Python proxy server. The proxy is necessary because **both Kibana and OpenAI APIs block browser CORS requests**. The proxy holds all API keys and forwards requests.

```
Browser (localhost:3000)
  │
  ├─ POST /api/chat       → Kibana Agent Builder converse API
  ├─ POST /api/transcribe  → OpenAI Whisper STT
  ├─ POST /api/speak       → OpenAI TTS
  └─ GET  /                → static files (index.html, voice.js, style.css)
  │
serve.py (aiohttp, port 3000)
  │
  ├─→ https://athena-cs-1-bcccaa.kb.europe-west3.gcp.elastic.cloud/api/agent_builder/converse
  ├─→ https://api.openai.com/v1/audio/transcriptions
  └─→ https://api.openai.com/v1/audio/speech
```

**Feature Type**: New Capability
**Complexity**: Medium
**Systems Affected**: `voice-client/` only (zero backend changes)
**Dependencies**: aiohttp, httpx, pydantic-settings (new sub-project)

**Key finding**: The existing `ELASTIC_API_KEY` in `.env` already works for the Kibana Agent Builder converse API — no separate Kibana API key is needed. The Kibana URL is derived from the ES URL by replacing `.es.` with `.kb.` in the hostname.

---

## CONTEXT REFERENCES

### Files to Read Before Implementing

- `mcp-server/src/config.py` — Pattern for `pydantic-settings` config class with `env_file`, `extra: ignore`
- `mcp-server/src/tools/research.py` — Pattern for `httpx` async HTTP (error handling, timeout, response processing)
- `mcp-server/src/tools/artemis.py` — Pattern for proxying REST APIs with error wrapping
- `mcp-server/pyproject.toml` — Pattern for sub-project `pyproject.toml` structure
- `voice-client/index.html` — Existing scaffold (will be rewritten)
- `voice-client/voice.js` — Existing scaffold (will be rewritten)
- `voice-client/style.css` — Existing scaffold (will be rewritten)
- `.env.example` — Will be updated with new vars

### New Files to Create

| File | Purpose | ~Lines |
|------|---------|--------|
| `voice-client/pyproject.toml` | uv project with aiohttp, httpx, pydantic-settings | 20 |
| `voice-client/serve.py` | Proxy server: static files + 3 API routes | 150 |

### Files to Rewrite

| File | Purpose | ~Lines |
|------|---------|--------|
| `voice-client/index.html` | Full UI: header, chat area, text input, mic button, settings | 80 |
| `voice-client/style.css` | Dark theme, chat bubbles, mic animation, status indicators | 280 |
| `voice-client/voice.js` | State machine, MediaRecorder, API calls, chat display, voice flow | 450 |

### Files to Update

| File | Change |
|------|--------|
| `.env.example` | Add `VOICE_SERVER_PORT` (ELASTIC_URL and ELASTIC_API_KEY already exist — reused for Kibana) |

### Relevant Documentation (Read Before Implementing)

- [Elastic Agent Builder Converse API (sync)](https://www.elastic.co/docs/api/doc/serverless/operation/operation-post-agent-builder-converse) — Request/response schema for chat endpoint
- [Elastic Agent Builder Converse API (streaming)](https://www.elastic.co/docs/api/doc/serverless/operation/operation-post-agent-builder-converse-async) — SSE event format for streaming responses
- [OpenAI Audio Transcriptions API](https://platform.openai.com/docs/api-reference/audio/createTranscription) — Whisper STT endpoint
- [OpenAI Text-to-Speech API](https://platform.openai.com/docs/api-reference/audio/createSpeech) — TTS endpoint
- [MDN: MediaRecorder API](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder) — Browser audio recording

### Patterns to Follow

**Config pattern** (from `mcp-server/src/config.py`):
```python
class VoiceSettings(BaseSettings):
    model_config = {"env_file": (".env", "../.env"), "env_file_encoding": "utf-8", "extra": "ignore"}
```

**Error handling** (from `mcp-server/src/tools/artemis.py`):
- Wrap each proxy route in try/except
- Return `{"error": "descriptive message"}` on failure
- Handle `httpx.HTTPStatusError`, `httpx.ConnectError`, and generic `Exception` separately

### Key API Specifications

**Agent Builder Converse (sync)** — verified working with existing `ELASTIC_API_KEY`:
```
POST {KIBANA_URL}/api/agent_builder/converse
Headers: Authorization: ApiKey {ELASTIC_API_KEY}, kbn-xsrf: true, Content-Type: application/json
Body: { "input": "user text", "agent_id": "athena", "conversation_id": "optional" }
Response: { "response": { "message": "agent text" }, "conversation_id": "id", "steps": [...] }

Kibana URL: derive from ELASTIC_URL by replacing .es. with .kb. in hostname
  ELASTIC_URL: https://athena-cs-1-bcccaa.es.europe-west3.gcp.elastic.cloud:443
  KIBANA_URL:  https://athena-cs-1-bcccaa.kb.europe-west3.gcp.elastic.cloud:443
```

**OpenAI Whisper STT**:
```
POST https://api.openai.com/v1/audio/transcriptions
Headers: Authorization: Bearer {key}
Body: multipart/form-data — file=<audio_blob>, model="whisper-1"
Response: { "text": "transcribed text" }
```

**OpenAI TTS**:
```
POST https://api.openai.com/v1/audio/speech
Headers: Authorization: Bearer {key}, Content-Type: application/json
Body: { "model": "tts-1", "voice": "nova", "input": "text to speak" }
Response: binary audio/mpeg stream
```

---

## IMPLEMENTATION PLAN

### Phase 1: Proxy Server (serve.py + pyproject.toml)

Build the Python proxy that serves static files and forwards API requests. Test each route with `curl` before writing any JavaScript.

### Phase 2: HTML + CSS (Static UI)

Build the complete visual interface with dark theme, chat layout, mic button, and all CSS animations. No JS behavior — just the static structure.

### Phase 3: Text Chat (JavaScript)

Implement the text-only chat flow: type message → display → proxy to agent → display response. This validates the full proxy chain without voice complexity.

### Phase 4: Voice Pipeline (JavaScript)

Add MediaRecorder for mic capture, Whisper transcription, and TTS playback. Wire the full voice flow: record → transcribe → chat → speak.

### Phase 5: Polish

Settings panel, keyboard shortcuts, error handling, localStorage persistence.

---

## STEP-BY-STEP TASKS

### Prerequisite: Verify OPENAI_API_KEY

The `.env` currently has `OPENAI_API_KEY=your-openai-api-key` (placeholder). Before implementing voice, set a real OpenAI API key. The existing `ELASTIC_URL` and `ELASTIC_API_KEY` already work for the Kibana converse API (verified).

**VALIDATE**: `OPENAI_API_KEY` in `.env` is a real key (starts with `sk-`).

---

### Task 1: CREATE `voice-client/pyproject.toml`

Create the uv project definition following the pattern from `mcp-server/pyproject.toml`.

Dependencies:
- `aiohttp>=3.11.0` — async HTTP server (static files + proxy routes)
- `httpx>=0.27.0` — async HTTP client (forwarding to external APIs)
- `pydantic-settings>=2.5.0` — config from env vars
- `python-dotenv>=1.0.0` — load .env files

No build system needed (not a library). No ruff/pytest config (too small for tests).

**VALIDATE**: `cd voice-client && uv sync` succeeds.

---

### Task 2: CREATE `voice-client/serve.py` — Config + Static Files + Health

Start with the foundation: config class, static file serving, and health endpoint.

**`VoiceSettings`** (pydantic-settings, matching `mcp-server/src/config.py` pattern):
- `elastic_url: str = ""` — reused from existing .env; Kibana URL derived by replacing `.es.` with `.kb.` in hostname
- `elastic_api_key: str = ""` — reused from existing .env; works for both ES and Kibana APIs
- `agent_id: str = "athena"`
- `openai_api_key: str = ""`
- `voice_server_port: int = 3000`
- `model_config` with `env_file: (".env", "../.env")`, `extra: "ignore"`
- Add a `@property` method `kibana_url` that derives the URL: `self.elastic_url.replace(".es.", ".kb.")`

**Routes**:
- `GET /api/health` → `{"status": "ok"}`
- Static files: serve `index.html`, `voice.js`, `style.css` from the same directory as `serve.py`

**Entry point**: `if __name__ == "__main__": aiohttp.web.run_app(app, port=settings.voice_server_port)`

**VALIDATE**: `cd voice-client && uv run python serve.py` → server starts on port 3000. `curl http://localhost:3000/api/health` → `{"status":"ok"}`. `curl http://localhost:3000/` → returns existing index.html content.

---

### Task 3: ADD `POST /api/chat` route to `serve.py`

Proxy to Kibana Agent Builder converse API.

- Read JSON body: `{ "input": "...", "conversation_id": "..." }`
- Forward to `{settings.kibana_url}/api/agent_builder/converse` with:
  - `Authorization: ApiKey {settings.elastic_api_key}`
  - `kbn-xsrf: true`
  - `Content-Type: application/json`
  - Body: `{ "input": ..., "agent_id": settings.agent_id, "conversation_id": ... }`
- Return the full Kibana response JSON to the browser
- Use `httpx.AsyncClient` with `timeout=120.0` (agent tool chains can be slow)
- Error handling: return `{"error": "..."}` with appropriate status code

**VALIDATE**: `curl -X POST http://localhost:3000/api/chat -H 'Content-Type: application/json' -d '{"input":"Hello, what can you help me with?"}'` → returns JSON with `response.message` and `conversation_id`.

---

### Task 4: ADD `POST /api/transcribe` route to `serve.py`

Proxy to OpenAI Whisper STT.

- Read multipart form data (the audio blob from the browser's MediaRecorder)
- Forward to `https://api.openai.com/v1/audio/transcriptions` as multipart with:
  - `Authorization: Bearer {openai_api_key}`
  - Fields: `file` (the audio data), `model` = `whisper-1`
- Return the transcription JSON `{"text": "..."}` to browser
- Handle: missing API key → `{"error": "OpenAI API key not configured"}`

**VALIDATE**: Record a short test audio file or use any `.webm` file: `curl -X POST http://localhost:3000/api/transcribe -F 'file=@test.webm' -F 'model=whisper-1'` → returns `{"text":"..."}`.

---

### Task 5: ADD `POST /api/speak` route to `serve.py`

Proxy to OpenAI TTS.

- Read JSON body: `{ "text": "...", "voice": "nova" }`
- Forward to `https://api.openai.com/v1/audio/speech` with:
  - `Authorization: Bearer {openai_api_key}`
  - Body: `{ "model": "tts-1", "voice": voice, "input": text }`
- Stream the binary audio response back to browser with `Content-Type: audio/mpeg`
- Truncate `text` to 4096 chars if longer (TTS API limit)
- Handle: missing API key → `{"error": "OpenAI API key not configured"}`

**VALIDATE**: `curl -X POST http://localhost:3000/api/speak -H 'Content-Type: application/json' -d '{"text":"Hello from Athena","voice":"nova"}' --output test.mp3 && file test.mp3` → shows audio/mpeg data.

---

### Task 6: REWRITE `voice-client/index.html`

Full UI structure. Key elements:

- **Header**: "Athena" title, subtitle "Your second brain, listening.", settings gear icon, mode toggle button
- **Settings panel** (hidden by default): connection status indicator, voice selector dropdown (nova/alloy/echo/fable/onyx/shimmer), auto-speak toggle
- **Chat area** (`#messages`): scrollable container for message bubbles, injected by JS
- **Input area** with two containers (one visible at a time):
  - **Text mode**: text `<input>` + Send `<button>`
  - **Voice mode** (hidden initially): large mic `<button>` with SVG icon, status text below
- Load `style.css` and `voice.js`
- No inline styles or scripts

**VALIDATE**: Open `http://localhost:3000/` in Chrome. Page loads with dark background, header visible, text input at bottom.

---

### Task 7: REWRITE `voice-client/style.css`

Dark theme with polished animations for demo video.

**Design tokens** (CSS custom properties):
```
--bg-primary: #0f1117        (near-black)
--bg-secondary: #1a1d27      (panels)
--bg-input: #252830          (input fields)
--text-primary: #e8eaed      (main text)
--text-secondary: #9aa0a6    (muted)
--accent: #7c4dff            (purple, Athena brand)
--accent-glow: rgba(124,77,255,0.3)
--user-bubble: #2d3142       (user messages)
--agent-bubble: #1e2233      (agent messages)
--danger: #ff5252            (recording)
--success: #69f0ae           (connected)
```

**Layout**: Full viewport height, flex column. Header fixed top, chat area flex-grow with `overflow-y: auto`, input area fixed bottom.

**Message bubbles**: User right-aligned (--user-bubble bg), agent left-aligned (--agent-bubble bg). Max-width 80%. Rounded corners.

**Mic button**: 72px circle, `--accent` background. Recording state: pulsing red ring via `@keyframes pulse-ring`. Disabled state: grayed out.

**Status indicators**:
- Recording: red dot + "Recording..."
- Transcribing: spinner + "Transcribing..."
- Thinking: spinner + "Athena is thinking..."
- Speaking: animated bars + "Speaking..."

**Settings panel**: slides down from header, absolute positioned, semi-transparent background.

**VALIDATE**: Visual inspection in Chrome. Toggle CSS classes manually in DevTools to verify all states look correct.

---

### Task 8: REWRITE `voice-client/voice.js` — Scaffolding + State Machine

IIFE wrapper with:

- **State machine**: `IDLE`, `RECORDING`, `TRANSCRIBING`, `THINKING`, `SPEAKING`
- `setState(newState)` function that updates `state` variable and calls `updateUI()`
- `updateUI()` function that shows/hides status indicators and enables/disables buttons based on state
- **DOM references**: cached on `DOMContentLoaded`
- `addMessage(role, text)` — creates and appends a message bubble div to `#messages`, roles: `'user'`, `'agent'`, `'system'` (errors)
- `scrollToBottom()` — smooth scroll chat area to latest message
- `init()` function called on DOMContentLoaded

**VALIDATE**: Open page in Chrome console. `addMessage('user', 'test')` creates a right-aligned bubble. `addMessage('agent', 'response')` creates a left-aligned bubble.

---

### Task 9: ADD text chat flow to `voice.js`

Implement the text-only chat path:

- `async function chat(text)` — POST to `/api/chat` with `{ input, conversation_id }`, returns `response.message`, stores `conversation_id` for continuity
- `async function handleTextInput(text)` — calls `addMessage('user', text)` → `setState('THINKING')` → `chat(text)` → `addMessage('agent', response)` → `setState('IDLE')`
- Wire up: text input `keydown` (Enter) + send button `click` → `handleTextInput()`
- Clear input field after sending

**VALIDATE**: Type "Hello" + Enter. User bubble appears. After a few seconds, agent response appears. Send follow-up "What did I just say?" — agent remembers context.

---

### Task 10: ADD voice recording to `voice.js`

MediaRecorder integration:

- `async function startRecording()` — `getUserMedia({audio: true})`, create `MediaRecorder` with `audio/webm;codecs=opus`, collect chunks, call `setState('RECORDING')`
- `function stopRecording()` → returns `Promise<Blob>` that resolves when recorder stops. Releases mic tracks.
- Mode toggle: `toggleMode()` switches `isVoiceMode`, shows/hides text vs voice input containers
- Wire mic button: click while IDLE → startRecording(), click while RECORDING → proceed to transcribe

**VALIDATE**: Click mode toggle → mic button appears. Click mic → browser asks mic permission → red pulse animation. Click again → recording stops.

---

### Task 11: ADD full voice pipeline to `voice.js`

Connect all pieces:

- `async function transcribe(audioBlob)` — POST to `/api/transcribe` as FormData with `file` + `model=whisper-1`, returns text string
- `async function speak(text)` — POST to `/api/speak` with `{ text, voice }`, create `Blob` → `URL.createObjectURL` → `new Audio()` → play. Returns promise that resolves on `audio.ended`.
- `async function handleVoiceInput()` — full pipeline:
  1. `stopRecording()` → audioBlob
  2. `setState('TRANSCRIBING')` → `transcribe(audioBlob)` → text
  3. `addMessage('user', text)`
  4. `setState('THINKING')` → `chat(text)` → response
  5. `addMessage('agent', response)`
  6. If voice mode: `setState('SPEAKING')` → `speak(response)`
  7. `setState('IDLE')`
  8. Wrap in try/catch → `addMessage('system', error.message)` on failure

**VALIDATE**: Full voice loop: click mic, say "What are my notes about API refactoring?", click mic. Transcription appears as user message, agent responds with text + plays audio.

---

### Task 12: ADD settings + polish to `voice.js`

- **Settings panel**: toggle visibility on gear icon click
- **Voice selector**: dropdown to choose TTS voice (nova/alloy/echo/fable/onyx/shimmer), stored in localStorage
- **Auto-speak toggle**: when off, agent responses are text-only even in voice mode
- **localStorage**: load settings on init, save on change
- **Keyboard shortcuts**: Escape cancels recording (stops and discards), Space toggles recording when text input not focused
- **Stop speaking**: clicking mic during SPEAKING state stops audio and returns to IDLE
- **Error handling**: network errors shown as system messages, never crashes

**VALIDATE**: Change voice → send message → TTS uses new voice. Refresh → settings persist. Disconnect proxy → error message appears gracefully.

---

### Task 13: UPDATE `.env.example`

Add voice server port (all other vars already exist):

```env
# --- Voice Client Proxy ---
VOICE_SERVER_PORT=3000
# Uses ELASTIC_URL (derives Kibana URL), ELASTIC_API_KEY, and OPENAI_API_KEY from above
```

**VALIDATE**: `.env.example` documents VOICE_SERVER_PORT and notes that ELASTIC_URL/ELASTIC_API_KEY/OPENAI_API_KEY are reused.

---

## VALIDATION COMMANDS

### Level 1: Proxy Server
```bash
cd voice-client && uv sync
uv run python serve.py &
curl http://localhost:3000/api/health
curl -X POST http://localhost:3000/api/chat -H 'Content-Type: application/json' -d '{"input":"Hello"}'
# Kill the server after testing
```

### Level 2: Linting
```bash
cd voice-client && uv run ruff check serve.py && uv run ruff format --check serve.py
```

### Level 3: Manual Browser Testing
1. Open `http://localhost:3000/` in Chrome
2. Text flow: type message → Enter → see response
3. Toggle to voice mode → click mic → speak → click mic → hear response
4. Check settings persistence across refresh
5. Check error handling (stop proxy, try to send)

### Level 4: Demo Rehearsal
Run the full demo scenario:
1. Voice: "What are my notes about the API refactoring project?"
2. Voice: "Read the sprint review notes"
3. Voice: "Extract tasks from the API refactoring note"
4. Text: Toggle to text, verify it still works
5. Verify conversation context is maintained across all messages

---

## ACCEPTANCE CRITERIA

- [ ] Proxy server starts and serves static files on port 3000
- [ ] `/api/chat` successfully communicates with Agent Builder and returns responses
- [ ] `/api/transcribe` converts audio to text via Whisper
- [ ] `/api/speak` returns audio via TTS
- [ ] Text chat flow works end-to-end (type → agent responds)
- [ ] Voice chat flow works end-to-end (speak → transcribe → agent → TTS → hear)
- [ ] Voice/text mode toggle works
- [ ] Conversation context maintained across messages (conversation_id reuse)
- [ ] Settings persist in localStorage (voice selection, auto-speak)
- [ ] Error states handled gracefully (network errors, API failures)
- [ ] UI is visually polished with dark theme (demo-ready)
- [ ] Recording animation visible during mic capture
- [ ] Status indicators show current state (recording/transcribing/thinking/speaking)

---

## RISKS

| Risk | Mitigation |
|------|------------|
| Agent response too long for TTS (>4096 chars) | Truncate at 4096 chars in the `/api/speak` proxy route. For demo, use focused queries. |
| Whisper latency in demo | Keep recordings short (<10s). Show "Transcribing..." status. Whisper-1 is typically 1-2s. |
| Agent converse latency (10-30s for tool chains) | Show "Athena is thinking..." with spinner. Sync API is simpler; streaming `/converse/async` can be added later for progressive display. |
| MediaRecorder mimeType unsupported | Check `MediaRecorder.isTypeSupported()`, fall back to `audio/webm` without codec. Chrome (demo browser) supports `audio/webm;codecs=opus`. |
| OPENAI_API_KEY not set | Proxy returns clear error: "OpenAI API key not configured". Text chat still works without it. |

---

## NOTES

- **Zero backend changes**: The MCP server and agent config are untouched. Voice is purely client + proxy.
- **All API keys stay server-side**: The browser never sees or sends API keys. The proxy holds them via `.env`.
- **Streaming chat is optional**: The sync converse API is used for simplicity. Streaming (`/api/agent_builder/converse/async`) can be added later for progressive text display.
- **The proxy server is ~150 lines**: Keep it simple. aiohttp for async server, httpx for async client. No framework overhead.
