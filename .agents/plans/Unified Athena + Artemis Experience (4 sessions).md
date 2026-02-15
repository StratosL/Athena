# Plan: Unified Athena + Artemis Experience

## Context

The current Athena setup requires 5 processes across 4 terminals and 3 browser tabs. This plan consolidates everything into **one `docker compose up` command** and **one browser URL** (`localhost:3000`) where the Artemis dashboard and Athena chat sidebar coexist.

The work is split into **4 sessions**, each independently completable in a fresh context window.

---

## Session 1: Backend Infrastructure

**Goal**: All backend services start with one command. Voice proxy gets CORS support.

### Changes

**1. Fix MCP server Dockerfile bug**
- File: `/home/stardust/Athena/mcp-server/Dockerfile` (line 38)
- Change `CMD ["python", "-m", "src.server"]` → `CMD ["python", "-m", "src"]`
- Reason: `src.server` causes double-import bug (documented in DEVLOG Day 7)

**2. Add CORS middleware to voice proxy**
- File: `/home/stardust/Athena/voice-client/serve.py`
- Add `@web.middleware` that sets `Access-Control-Allow-Origin`, `Allow-Methods`, `Allow-Headers` on all responses
- Handle `OPTIONS` preflight requests
- Apply middleware in `create_app()`: `web.Application(middlewares=[cors_middleware])`

**3. Create voice-client Dockerfile**
- File: `/home/stardust/Athena/voice-client/Dockerfile` (NEW)
- Pattern: same multi-stage uv build as `mcp-server/Dockerfile`
- Key difference: single-file app (`serve.py`) not a package — copy `serve.py` + static assets (index.html, style.css, voice.js, logos)
- CMD: `["python", "serve.py"]`
- EXPOSE: 3001

**4. Update docker-compose.yml**
- File: `/home/stardust/Athena/docker-compose.yml`
- Remove `profiles: [full]` from `artemis` service (always start it)
- Add `voice-proxy` service (build from `./voice-client`, port 3001, env_file: `.env`)
- Add `ngrok` service under `profiles: [tunnel]` (image `ngrok/ngrok:latest`, command `http mcp-server:8001`, port 4040 for inspector, requires `NGROK_AUTHTOKEN` env var)

### Verify
```bash
docker compose build                              # all 3 services build
docker compose up -d                              # starts artemis, mcp-server, voice-proxy
curl http://localhost:8000/health                  # Artemis OK
curl http://localhost:3001/api/health              # Voice proxy OK
curl -H "Origin: http://localhost:3000" -I http://localhost:3001/api/health  # CORS headers present
```

---

## Session 2: React Chat Component (Text Only)

**Goal**: Working text chat with Athena inside a right-side drawer in the Artemis React app.

### Prerequisites
- Voice proxy running on port 3001 (Session 1 or manual `python serve.py`)

### Changes (all in `/home/stardust/Artemis/frontend/`)

**1. Install npm dependencies**
```bash
npm install marked dompurify
npm install -D @types/dompurify
```

**2. Add Vite dev proxy**
- File: `vite.config.ts` — add inside `server: {}`:
```ts
proxy: {
  '/athena': {
    target: 'http://localhost:3001',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/athena/, '/api'),
  },
},
```
- Effect: `/athena/chat` → `localhost:3001/api/chat` (no CORS issues in dev)

**3. Create Athena API client**
- File: `src/lib/athena-api.ts` (NEW)
- Pattern: follows `src/lib/api.ts` fetch wrapper style
- Functions: `athenaChat(req) → ChatResponse`, `athenaTranscribe(blob) → string`, `athenaSpeak(text, voice) → Blob`
- Base URL: `"/athena"` (uses Vite proxy)

**4. Create Zustand chat store**
- File: `src/stores/chatStore.ts` (NEW)
- Pattern: follows `src/stores/timerStore.ts`
- State: `isOpen`, `messages[]`, `conversationId`, `status` (idle/recording/transcribing/thinking/speaking), `voiceMode`
- Actions: `toggle()`, `setOpen()`, `addMessage()`, `clearMessages()`, `setStatus()`, `setConversationId()`

**5. Create useAthenaChat hook**
- File: `src/hooks/useAthenaChat.ts` (NEW)
- Wires chatStore + athena-api together
- `sendMessage(text)`: adds user message → sets status to thinking → calls athenaChat → adds agent response → returns response text
- Tracks `conversationId` across turns

**6. Create ChatSidebar component**
- Directory: `src/design-system/components/features/ChatSidebar/` (NEW)
- Files: `ChatSidebar.types.ts`, `index.tsx`
- Pattern: follows `TaskCard`, `PomodoroWidget` structure — types file + index.tsx
- Design:
  - Fixed right panel, 420px wide on desktop, full-screen on mobile
  - `motion` slide-in from right (spring animation, matching Sidebar collapse pattern)
  - Mobile: semi-transparent backdrop overlay (click to close)
  - Header: "Athena" title with status dot + close button (X icon)
  - Messages area: scrollable, auto-scrolls to bottom on new messages
  - Agent messages: left-aligned, glassmorphism bubble, markdown rendered via `marked` + `DOMPurify`
  - User messages: right-aligned, indigo-tinted bubble
  - Thinking indicator: pulsing indigo dot
  - Input area: text input + send button (gradient indigo→gold, matching Button primary style)
  - Welcome screen when empty: greeting + 3 hint chips (clickable suggestions)
- Styling: uses `glassmorphismClasses`, `cn()`, `luxury-*` color tokens, `lucide-react` icons (X, Send, MessageCircle)
- Export from `src/design-system/components/index.ts`

**7. Integrate into AppShell**
- File: `src/pages-new/layout/AppShell.tsx`
- Add floating action button (FAB): fixed `bottom-20 right-6` (clears mobile BottomNav), gradient indigo→gold, MessageCircle icon, hides when sidebar open
- Render `<ChatSidebar open={isOpen} onClose={...} />`
- Import `useChatStore` for toggle state
- Adjust main content right padding when sidebar is open on desktop: `lg:pr-[420px]` transition

### Key patterns to reuse
- `glassmorphismClasses` from `@/design-system` → `backdrop-blur-md bg-luxury-card border border-luxury-border rounded-xl`
- `cn()` from `@/lib/utils` → conditional class merging
- `motion` from `motion/react` → animations (AnimatePresence, slide-in)
- `lucide-react` → icons (X, Send, MessageCircle, Mic, Settings)
- Color tokens: `luxury-obsidian`, `luxury-indigo`, `luxury-gold`, `luxury-text-primary`, `luxury-text-secondary`, `luxury-border`, `luxury-card`

### Verify
1. `npm run dev` — compiles without errors
2. Open `localhost:3000` — FAB visible in bottom-right
3. Click FAB — sidebar slides in, FAB disappears
4. Type message, press Enter — user bubble appears, thinking indicator shows, agent response renders with markdown
5. Click X or backdrop — sidebar closes, FAB reappears
6. Check 375px mobile viewport — sidebar goes full-screen

---

## Session 3: Voice + Polish

**Goal**: Add voice recording, TTS playback, settings, keyboard shortcuts, and status indicators.

### Prerequisites
- Session 2 complete (ChatSidebar exists and works with text)

### Changes (all in `/home/stardust/Artemis/frontend/`)

**1. Create useVoiceRecorder hook**
- File: `src/hooks/useVoiceRecorder.ts` (NEW)
- Encapsulates MediaRecorder: `startRecording()`, `stopRecording() → Blob`, `cancelRecording()`
- Codec priority: `audio/webm;codecs=opus` → `audio/webm` fallback
- Cleans up mic tracks on stop/cancel

**2. Create useAthenaVoice hook**
- File: `src/hooks/useAthenaVoice.ts` (NEW)
- Orchestrates: record → transcribe → chat → speak
- Uses `useVoiceRecorder`, `useAthenaChat`, `athenaTranscribe`, `athenaSpeak`
- `handleMicClick()`: state-dependent behavior (idle→record, recording→process, speaking→stop)
- `speakText(text)`: creates Audio element, plays blob URL, cleans up on end
- Reads settings from localStorage: `athena-voice` (default "nova"), `athena-auto-speak` (default true)

**3. Refactor useAthenaChat.sendMessage**
- File: `src/hooks/useAthenaChat.ts` (MODIFY)
- Make `sendMessage` return `Promise<string | null>` (the agent response text)
- Voice hook needs the response text to pass to TTS

**4. Enhance ChatSidebar with voice**
- File: `src/design-system/components/features/ChatSidebar/index.tsx` (MODIFY)
- Header additions:
  - Mode toggle button: Mic ↔ MessageSquare icon (like voice-client header)
  - Settings gear icon → opens settings dialog
- Input area: conditional render
  - Text mode: text input + send button (existing)
  - Voice mode: large circular mic button with animated rings (gradient indigo→gold, turns red when recording)
- Status indicators in messages area:
  - Recording: red pulsing dot + "Recording..."
  - Transcribing: indigo pulsing dot + "Transcribing..."
  - Thinking: indigo pulsing dot + "Athena is thinking..."
  - Speaking: 4 animated bars (using `motion` scaleY animation, staggered delays)
- Settings dialog (Radix Dialog, already a dep):
  - Voice selection dropdown (nova, alloy, echo, fable, onyx, shimmer)
  - Auto-speak toggle switch
  - Stored in localStorage
- Keyboard shortcuts (useEffect with keydown listener):
  - `Space` (voice mode, input not focused): toggle recording
  - `Escape`: cancel recording / stop speaking / close sidebar
- Welcome screen: 3 hint chips (e.g. "What's in my vault?", "Plan my day", "Search for API notes")

### Verify
1. Toggle to voice mode — mic button appears, text input hides
2. Click mic — browser asks permission, recording starts, button pulses red
3. Click mic again — "Transcribing..." → "Thinking..." → response appears → audio plays
4. Open settings — change voice to "echo", disable auto-speak
5. Next voice interaction — no audio playback, response is text only
6. Press Space (voice mode) — toggles recording
7. Press Escape while recording — cancels, returns to idle
8. Press Escape while speaking — stops audio playback

---

## Session 4: Integration Testing + Demo Prep

**Goal**: End-to-end validation, Docker verification, DEVLOG update.

### Test checklist

**Infrastructure:**
- [ ] `docker compose up` starts artemis + mcp-server + voice-proxy
- [ ] `docker compose --profile tunnel up` adds ngrok
- [ ] Copy ngrok URL from `localhost:4040`, update Elastic MCP connector

**Chat flow (via sidebar at localhost:3000):**
- [ ] "Hello" → agent responds (validates full proxy chain)
- [ ] "Search my vault for API refactoring" → agent searches ES, returns notes
- [ ] "Read the sprint review notes" → agent reads from vault via MCP
- [ ] "Create a task: Fix login bug, Q1" → task appears in Artemis Tasks page
- [ ] "Plan my day" → agent uses daily plan tools

**Voice flow:**
- [ ] Record a question → transcription → response → TTS playback
- [ ] Change voice in settings → different voice on next response
- [ ] Auto-speak off → no audio, text only

**Cross-feature:**
- [ ] Task created via Athena visible on Tasks page without refresh (React Query invalidation)
- [ ] Mobile viewport: sidebar is full-screen drawer, FAB clears bottom nav

### Optional: Streaming support (time permitting)
- Add `POST /api/chat/stream` to `voice-client/serve.py` — calls `/api/agent_builder/converse/async` (SSE), streams chunks to client
- Frontend: fetch with `ReadableStream` reader, parse SSE `data:` lines, append tokens to message incrementally
- This makes responses appear token-by-token instead of after full completion

### Deliverables
- [ ] Update `DEVLOG.md` with Session 1-4 work
- [ ] Update `docker-compose.yml` comments with startup instructions
- [ ] Update `README.md` quickstart section

---

## File Summary

| Session | File | Action |
|---------|------|--------|
| 1 | `Athena/mcp-server/Dockerfile` | Fix CMD bug |
| 1 | `Athena/voice-client/Dockerfile` | NEW |
| 1 | `Athena/voice-client/serve.py` | Add CORS middleware |
| 1 | `Athena/docker-compose.yml` | Add voice-proxy, ngrok; remove artemis profile |
| 2 | `Artemis/frontend/vite.config.ts` | Add proxy |
| 2 | `Artemis/frontend/src/lib/athena-api.ts` | NEW — API client |
| 2 | `Artemis/frontend/src/stores/chatStore.ts` | NEW — Zustand store |
| 2 | `Artemis/frontend/src/hooks/useAthenaChat.ts` | NEW — chat hook |
| 2 | `Artemis/frontend/src/design-system/components/features/ChatSidebar/` | NEW — component |
| 2 | `Artemis/frontend/src/design-system/components/index.ts` | Add export |
| 2 | `Artemis/frontend/src/pages-new/layout/AppShell.tsx` | Add FAB + sidebar |
| 3 | `Artemis/frontend/src/hooks/useVoiceRecorder.ts` | NEW |
| 3 | `Artemis/frontend/src/hooks/useAthenaVoice.ts` | NEW |
| 3 | `Artemis/frontend/src/hooks/useAthenaChat.ts` | Refactor return type |
| 3 | `Artemis/frontend/src/design-system/components/features/ChatSidebar/index.tsx` | Add voice, settings, keyboard shortcuts |
| 4 | `Athena/DEVLOG.md` | Update |

## Estimated Effort

| Session | Effort | Can skip? |
|---------|--------|-----------|
| 1: Backend infrastructure | ~1.5h | No |
| 2: React chat (text only) | ~3-4h | No |
| 3: Voice + polish | ~2-3h | Yes (text-only still works for demo) |
| 4: Integration + demo prep | ~1-2h | No |
| **Total** | **~8-10h** | |
