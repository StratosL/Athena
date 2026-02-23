# Development Log

**Project:** Athena — Second Brain Orchestrator Agent
**Developer:** Stratos Louvaris
**Timeline:** February 12, 2026 –
**Hackathon Deadline:** February 27, 2026, 1:00 PM EST

---

## At a Glance

| Metric | Value |
|--------|-------|
| Total time | ~34 hours (Days 1–37) |
| Sub-projects | 8 (indexer, mcp-server, voice-client, agent-config, heartbeat, artemis-backend, frontend, scripts) |
| ES indices | 2 (athena-notes, athena-conversations) |
| MCP tools implemented | 14 (3 vault + 7 Artemis + 1 knowledge + 2 research + 1 skills) |
| ES|QL tools defined | 5 + 1 index search |
| Sample vault | 23 notes across 7 folders, 135 wikilinks |
| Indexer status | Validated end-to-end — 17/17 indexed, dedup confirmed, semantic search working |
| Type checking | pyright (3 sub-projects) + TypeScript (frontend) — 0 errors across all |
| System prompt | 257 lines — persona, tool routing, workflows, Eisenhower, 1-3-5, guardrails, memory |
| Agent Builder | Athena agent live — 20 tools (6 ES|QL + 14 MCP), 16.3k char system prompt (synced) |
| Current state | Whisper language fix, demo prep |

---

## The Journey

### Day 37: Force English Whisper Transcription (Feb 23) — ~15 min

Fixed voice transcription producing Greek text instead of English. Whisper's auto-detect was picking up the user's Greek accent/environment and transcribing into Greek, which then caused the agent to reply in Greek.

**Bug fix — Whisper language parameter (1 file):**

- **Root cause:** The Whisper API call in `voice-client/serve.py` did not specify a `language` parameter. Whisper auto-detected Greek from the audio and transcribed accordingly.
- **`voice-client/serve.py`** — Added `"language": "en"` to the Whisper transcription request `data` dict. Forces English transcription regardless of accent or background audio.

---

### Day 36: Devpost Article + API Fix + Voice Research + Indexer Watcher (Feb 22) — ~1.5 hours

Wrote the Devpost hackathon submission article, fixed a converse API field name bug, researched real-time voice alternatives, and added the indexer watcher to Docker Compose for automatic vault→ES sync.

**Devpost submission (`devpost/submission.md`):**

- Wrote ~1,200 word submission covering all standard Devpost sections: Inspiration, What It Does, How We Built It, Challenges, Accomplishments, What We Learned, What's Next, Built With.
- Researched winning Agent Builder projects from Cal Hacks 12.0 (AgentOverflow, MarketMind) for positioning.
- Added 7 image/diagram placeholders for screenshots and architecture visuals.

**Bug fix — converse API `configuration_overrides` field name (3 files):**

- **Root cause:** `systemPromptAddition` is not a valid field in the Elastic Agent Builder converse API. The correct field is `instructions` inside `configuration_overrides`. This caused a 400 "definition for this key is missing" error when memory files existed in the vault (triggered on Windows where vault path pointed to a populated Obsidian vault).
- **`voice-client/serve.py`** — Renamed `systemPromptAddition` → `instructions` in converse API payload.
- **`heartbeat/src/heartbeat.py`** — Same rename.
- **`api-reference.md`** — Updated converse API docs to reflect correct field name.

**Real-time voice research:**

- Surveyed 10 platforms: OpenAI Realtime API, Gemini Live, ElevenLabs, LiveKit, Vapi, Deepgram, Hume AI, Retell, Pipecat, Ultravox.
- Key finding: native speech-to-speech APIs (OpenAI Realtime, Gemini Live) can't use Agent Builder as the brain — they require their own model. Best fit for Athena is streaming STT (Deepgram) + existing agent + streaming TTS, reducing latency from 3-8s to ~1.5-3s.
- Documented trade-offs for each approach (latency, cost, complexity, agent tool compatibility).

**Indexer watcher Docker service (3 new files):**

- **`indexer/Dockerfile`** — Multi-stage build (uv builder + slim runtime), runs `python -m src watch` by default.
- **`indexer/src/__main__.py`** — Entry point for `python -m src` invocation inside the container.
- **`docker-compose.yml`** — Added `indexer-watcher` service: mounts `VAULT_PATH` read-only, auto-syncs vault changes to Elasticsearch via watchdog. Starts automatically with `docker compose up` — no manual indexing step needed.

**Polling fallback for Windows/macOS Docker (4 files):**

- **Root cause:** Docker bind-mounted Windows volumes don't propagate inotify events to Linux containers, so watchdog's native `Observer` never fires.
- **`indexer/src/watcher.py`** — Auto-detects inotify support by writing a probe file and checking for events within 3s. Falls back to `PollingObserver` (every 30s) when events don't propagate. Also runs an initial `index_vault()` bulk sync on startup to catch notes created before the watcher started.
- **`indexer/src/config.py`** — Added `WATCHER_POLLING` (bool) and `WATCHER_POLL_INTERVAL` (int, default 30s) settings.
- **`indexer/src/cli.py`** — Passes new watcher settings through to `start_watcher()`.
- **`.env.example`** — Documented `WATCHER_POLLING` and `WATCHER_POLL_INTERVAL`.

---

### Day 35: E2E Bug Sweep — 6 Fixes (Feb 21) — ~1 hour

Ran comprehensive E2E browser tests (desktop 1280x800 + mobile 375x667) across all pages. Fixed the checkbox cache invalidation bug, then addressed 5 critical/medium issues found during testing.

**Bug fixes (7 files modified):**

- **`useTasks.ts`** — `useCompleteTask` now invalidates `dailyPlanKeys.all` so completing a task updates both Dashboard and Daily Plan without refresh.
- **`vite.config.ts` + `nginx.conf` + `athena-api.ts`** — Renamed API proxy from `/athena` to `/athena-api` to fix direct URL navigation to `/athena` page (was being proxied to backend instead of serving SPA).
- **`athena-api.ts`** — Improved error parsing: extracts `error`, `message`, or `detail` from response body instead of showing raw JSON to user.
- **`useAthenaChat.ts`** — Friendlier error message format when Athena API fails.
- **`Tasks/index.tsx`** — Added `window.confirm()` before task deletion.
- **`LuxuryQuickTaskInput.tsx`** — Stacked input vertically on mobile (`flex-col sm:flex-row`) so the text input gets full width instead of being squeezed to 88px.
- **`analytics/repository.py`** — `get_tasks_in_range` now includes tasks completed in the date range (not just created), fixing "0 Tasks Done" when tasks were created on previous days.

**Verification:** `tsc --noEmit` — 0 errors. All 4 browser regression tests passed.

---

### Day 34: Full-Height + Font Bump for Tasks, Daily Plan, Pomodoro (Feb 21) — ~30 min

Extended the Dashboard's `fillHeight` viewport-filling treatment to the three remaining content pages: Tasks, Daily Plan, and Pomodoro. Each page now fills the full desktop viewport with enlarged, readable font sizes and properly scrollable content areas.

**Changes (11 files modified, 0 new files):**

- **`Tasks/index.tsx`** — Added `fillHeight`, removed `max-w-3xl` constraint on quick input, QuadrantGrid and list view fill height with `flex-1 min-h-0`, footer pinned with `flex-shrink-0`.
- **`QuadrantGrid/index.tsx`** (full mode) — Task title `text-sm` → `text-base`, pomodoro count `text-xs` → `text-sm`, checkboxes `w-5` → `w-6` with `border-2`, delete icon `w-4` → `w-5`, card padding `p-3` → `p-4`, empty state `text-sm` → `text-base`, subtitle `text-sm` → `text-base`. Grid uses `auto-rows-fr` for equal quadrant height. Cards are flex columns with scrollable task lists.
- **`DailyPlan/index.tsx`** — Added `fillHeight`, grid columns fill height, footer pinned.
- **`LuxuryPlanView.tsx`** — Section headers `text-sm` → `text-base`, dots `w-2` → `w-2.5`.
- **`LuxuryTaskSlot.tsx`** — Slot min-heights bumped (+8px each), empty slot label `text-sm` → `text-base`, plus icon `w-4` → `w-5`, subtitle `text-xs` → `text-sm`, action buttons `w-7` → `w-8`, icons `w-4` → `w-5`.
- **`LuxuryPlanProgress.tsx`** — Labels `text-sm` → `text-base`, progress bar `h-2` → `h-2.5`, percentage `text-xs` → `text-sm`.
- **`LuxuryBacklogSidebar.tsx`** — Title added `text-lg`, subtitle `text-sm` → `text-base`, checkboxes `w-4` → `w-5`, task titles `text-sm` → `text-base`, removed `max-h-[600px]` cap.
- **`Pomodoro/index.tsx`** — Added `fillHeight`, timer column vertically centered, sidebar scrollable, tips `text-sm` → `text-base`.
- **`LuxuryPomodoroTimer.tsx`** — State label `text-sm` → `text-base`.
- **`LuxuryTaskLinker.tsx`** — Title added `text-lg`, task items `text-sm` → `text-base`, badge `text-[10px]` → `text-xs`, max-height `max-h-48` → `max-h-64`.
- **`LuxurySessionList.tsx`** — Title added `text-lg`, session text `text-sm` → `text-base`, timestamp `text-xs` → `text-sm`, padding `p-2` → `p-3`.

**Verification:** `tsc --noEmit` — 0 errors. `vite build` — success.

---

### Day 33: Dashboard Font Size Bump (Feb 21) — ~15 min

Dashboard card content was too small to read comfortably on desktop, especially with the cards now filling the full viewport. Bumped font sizes, checkbox sizes, and padding across all three dashboard sections (PlanWidget, QuadrantGrid compact mode, DashboardStatsBar).

**Changes (3 files modified, 0 new files):**

- **`PlanWidget/index.tsx`** — Task titles `text-sm` → `text-base`, section labels (Major/Medium/Small) `text-xs` → `text-sm`, card title added `text-lg`, checkboxes `w-4` → `w-5`, row padding `py-1.5` → `py-2.5`, progress bar `h-1.5` → `h-2`.
- **`QuadrantGrid/index.tsx`** — Compact headers `text-sm` → `text-base`, task titles `text-sm` → `text-base`, badge `text-[10px]` → `text-xs`, checkboxes `w-4` → `w-5`, removed `max-h-[120px]` cap so content fills available height. Removed hardcoded `slice(0, 5)` limit and "+N more" text — all tasks now render with `overflow-y-auto` scrolling.
- **`DashboardStatsBar.tsx`** — Stat labels `text-xs` → `text-sm`, timer state label `text-sm` → `text-base`, countdown `text-xl` → `text-2xl`.

**Verification:** `tsc --noEmit` — 0 errors.

---

### Day 32: Dashboard Full-Height Layout (Feb 21) — ~15 min

On desktop, the dashboard had wasted vertical space below the Plan and Matrix cards, plus a "Artemis v 0.6.0" footer adding visual noise. Made the dashboard content fill the full viewport height so cards expand to use all available screen real estate.

**Changes (2 files modified, 0 new files):**

- **`AppShell.tsx`** — Added optional `fillHeight?: boolean` prop. When enabled, the content wrapper becomes `h-screen flex flex-col` and `<main>` becomes `flex-1 flex flex-col min-h-0` on desktop (`lg:` breakpoint). Mobile layout unaffected.
- **`Dashboard/index.tsx`** — Enabled `fillHeight` on AppShell. The 2-column grid uses `flex-1 min-h-0` to expand vertically, with `overflow-auto` on each column for independent scrolling. Stats bar pinned to bottom with `flex-shrink-0`. Removed the "Artemis v 0.6.0" footer.

**Layout (desktop):**

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   Today's Plan      │   Eisenhower Matrix │
│   (fills height)    │   (fills height)    │
│                     │                     │
├─────────────────────┴─────────────────────┤
│  Focus  25:00  ████████░░░░  [Start]      │
│  2 pom  │  1.2h  │  5 done  │  72%       │
└───────────────────────────────────────────┘
```

**Verification:** `tsc --noEmit` — 0 errors.

---

### Day 31: Mobile "More" Bottom Sheet (Feb 19) — ~30 min

Replaced the 6-item horizontally scrollable mobile bottom nav with 5 direct tabs + a "More" button that opens an animated bottom sheet containing overflow items. Guide and Settings pages were previously unreachable on mobile because they only rendered in the desktop sidebar's `bottomItems`.

**Tab layout:**
- Direct tabs: Dashboard, Tasks, Daily Plan, Athena, More
- More sheet: Pomodoro, Analytics, Guide, Settings

**Changes (4 files modified, 0 new files):**

- **`navItems.ts`** — Added `primaryNavItems` (4 direct tabs) and `overflowNavItems` (4 overflow items). Existing `navItems`/`bottomNavItems` preserved for desktop sidebar.
- **`BottomNav.types.ts`** — Added `overflowItems?: SidebarNavItem[]` prop.
- **`BottomNav/index.tsx`** — Added `isMoreOpen` state, "More" button styled identically to nav items, animated bottom sheet with `AnimatePresence` + `motion.div` (spring transition, backdrop blur, glassmorphism). Sheet positioned above the nav bar. "More" button highlights gold when any overflow item is active. Removed `overflow-x-auto` since 5 items fit without scrolling.
- **`AppShell.tsx`** — Builds `primaryWithActive` and `overflowWithActive` arrays with active-state logic, passes both to `<BottomNav>`. Desktop sidebar unchanged.

**Verification:** `tsc --noEmit` — 0 errors. `vite build` — success. Browser tested with `agent-browser` on mobile (375x667) and desktop (1280x800) — all 6 test scenarios pass.

---

### Day 30: Dedicated Athena Chat Page (Feb 19) — ~1 hour

Added a full-page `/athena` route with 2-panel layout (conversation history + chat), replacing the cramped 420px sidebar for deeper conversations. Both the page and sidebar share the same Zustand store — state stays in sync.

**Step 1 — Extract shared components from ChatSidebar:**

Broke the 653-line `ChatSidebar/index.tsx` into 6 reusable shared modules under `ChatSidebar/shared/`:

| File | Purpose |
|------|---------|
| `renderMarkdown.ts` | Pure function: `marked` + DOMPurify |
| `StatusIndicator.tsx` | Recording/thinking/speaking status bubbles |
| `VoiceSettingsDialog.tsx` | Radix dialog for voice/auto-speak settings |
| `ConversationList.tsx` | History list with `showCloseButton` prop |
| `MessageList.tsx` | Messages, welcome screen, auto-scroll, hints |
| `ChatInput.tsx` | Text input + voice mic button with `autoFocus` prop |

Refactored `ChatSidebar/index.tsx` to import from `./shared` — slimmed to ~170 lines. Same public API.

**Step 2 — Athena page (`pages-new/Athena/`):**

- `index.tsx` — 2-panel layout: `ConversationPanel` (left, desktop-only `w-72`) + chat area (right, `flex-1`)
- `components/ChatHeader.tsx` — Avatar with status dot, voice toggle, new chat, settings
- `components/ConversationPanel.tsx` — Wraps `ConversationList` with glassmorphism card

**Step 3 — Routing + nav:**

- `navItems.ts` — Added 6th item: Athena with `Sparkles` icon
- `App.tsx` — Added `<Route path="/athena">` with lazy import
- `AppShell.tsx` — Hides ChatSidebar + FAB on `/athena`, removes right padding

**Step 4 — Mobile fixes:**

- `BottomNav` — Removed `slice(0, 5)`, now shows all items with `overflow-x-auto scrollbar-hide` for horizontal scroll
- `index.css` — Added `.scrollbar-hide` utility (hides scrollbar, keeps scroll)
- Athena FAB — Restored on mobile (`bottom-20 right-4`), dashboard "+" FAB moved to bottom-left to avoid overlap

**Step 5 — Cleanup:**

- Sidebar + BottomNav — Replaced `<a href>` with React Router `<Link to>` for client-side navigation (was causing full page reloads / "site can't be reached")
- Removed fake "Analytics Tracking" toggle from Settings → Data & Privacy (no telemetry exists, toggle was cosmetic)

**Verification:** `tsc --noEmit` — 0 errors. `vite build` — success. Browser tested on desktop (1280x720) and mobile (375x667).

---

### Day 29: Fix Daily Plan Task Assignment (Feb 19) — ~15 min

Clicking a task in the Daily Plan selector did nothing — task didn't appear in the slot. No error shown.

**Root Cause:** `find_plan_with_task()` in `DailyPlanService.assign_task()` searched ALL plans across ALL dates. If a task was assigned to yesterday's plan, the backend returned 409 `TaskAlreadyAssignedError`. The frontend mutation had no `onError` handler, so the modal closed silently with no feedback.

**Fix (1 file, 1 line changed):**

- **`services/artemis-backend/app/features/daily_plan/service.py`** — Changed the `find_plan_with_task` guard from blocking on ANY plan to only blocking when the task is already in the SAME plan (different slot). Tasks in previous days' plans are now freely assignable to today's plan.

**Before:** `if existing_plan:` — rejects if task is in any plan ever
**After:** `if existing_plan and existing_plan["id"] == plan_id:` — only rejects if task is already in this specific plan

**Verification:** pyright — 0 errors.

---

### Day 28: Dashboard Redesign — 2-Column Layout, Timer in Stats Bar (Feb 19) — ~30 min

The 3-column dashboard (Plan, Timer, Matrix) gave the Pomodoro timer its own column despite being low-information-density (one number + one button). Promoted Plan and Matrix to equal-width hero panels in a 2-column grid, and merged the timer into the bottom stats bar — combining it with the daily stats into a single card.

**Changes (3 files modified, 1 file deleted):**

- **`DashboardStatsBar.tsx`** — Rewrote from a thin `DailyStatsBar` wrapper into a combined timer + stats component. Top row: state label, countdown (`tabular-nums`), horizontal progress bar (flex-1), start/stop button. Divider. Bottom: 4-column stats grid (pomodoros, focus hours, tasks done, completion rate). All timer hooks wired in: `useTimerStore`, `usePomodoroWebSocket`, start/stop/complete mutations, server sync effect, auto-complete effect.
- **`Dashboard/index.tsx`** — Grid changed from `lg:grid-cols-3` to `lg:grid-cols-2`. Removed `DashboardTimerColumn` import and all `lg:order-*` wrappers. DOM order = visual order: Plan left, Matrix right.
- **`components/index.ts`** — Removed `DashboardTimerColumn` export.
- **`DashboardTimerColumn.tsx`** — Deleted.

**Layout:**

```
Desktop (lg+):
┌─────────────────────┬─────────────────────┐
│   Today's Plan      │   Eisenhower Matrix │
└─────────────────────┴─────────────────────┘
┌───────────────────────────────────────────┐
│  Focus  25:00  ████████░░░░░░  [Start]    │
│───────────────────────────────────────────│
│  2 pom  │  1.2h  │  5 done  │  72%       │
└───────────────────────────────────────────┘

Mobile: Plan → Matrix → Timer+Stats (single column)
```

**Not Affected:** `/pomodoro` page (still uses `PomodoroWidget`), `DailyStatsBar` design-system component (stays for reuse), all timer stores/hooks.

**Verification:** TypeScript `tsc --noEmit` — 0 errors. `grep -r "DashboardTimerColumn"` — 0 results.

---

### Day 27: Dashboard Layout — Plan Hero, Compact Timer (Feb 19) — ~20 min

The dashboard's 3-column layout had the Pomodoro timer (180px circular ring) in the center — the most prominent position. But the timer is low-information-density (one number + one button) compared to the Plan (9 task slots) and Matrix (4 quadrant cards). Swapped the layout so the Daily Plan takes the hero center spot.

**Changes (4 files modified, 0 new files):**

- **`PomodoroWidget.types.ts`** — Added `compact?: boolean` prop to `PomodoroWidgetProps`
- **`PomodoroWidget/index.tsx`** — Added compact rendering path: replaces the 180px `ProgressRing` with a horizontal progress bar (`h-1.5`, indigo for work / gold for breaks), reduces countdown to `text-2xl`, tightens padding to `p-4`, shrinks title to `text-sm`. All hook logic, state management, and WebSocket handling unchanged — only JSX conditionally branches.
- **`DashboardTimerColumn.tsx`** — One-line change: `<PomodoroWidget compact />`
- **`Dashboard/index.tsx`** — Reordered columns via CSS `order`: DOM order is Plan → Timer → Matrix (correct mobile stacking), desktop uses `lg:order-2` (Plan center), `lg:order-3` (Timer right), `lg:order-1` (Matrix left)

**Layout:**

| Position | Desktop (lg+) | Mobile |
|----------|--------------|--------|
| Left | Eisenhower Matrix | Plan (first) |
| Center | Today's Plan (hero) | Timer (second) |
| Right | Compact Timer | Matrix (third) |

**Not Affected:** `/pomodoro` page (uses `LuxuryPomodoroTimer` with 360px ring), `DailyStatsBar`, mobile FAB, all timer functionality.

**Verification:** TypeScript `tsc --noEmit` — 0 errors.

---

### Day 26: Pomodoro Settings Actually Work (Feb 19) — ~30 min

Pomodoro timer settings (work duration, break durations) were saved to localStorage but never consumed by any code. The work duration was hardcoded to 25 minutes at three independent layers: backend service, frontend API client, and frontend timer display.

**Root Cause:** Same pattern as Day 25 (appearance settings) — `useSettings` hook writes to localStorage, but no code reads those values. The backend `start_session()` hardcoded `duration_minutes=25`, the frontend API client never sent `duration_minutes`, and both timer components used `const WORK_DURATION_SECONDS = 25 * 60`.

**Fix — 3-layer wiring (7 files modified, 0 new files):**

- **Backend `service.py`** — `start_session()` now accepts `duration_minutes` parameter instead of hardcoding 25
- **Backend `routes.py`** — Extracts `duration_minutes` from request body and passes it to the service (schema already supported it)
- **Frontend `api.ts`** — `pomodoroApi.start()` now accepts and sends `duration_minutes` in the POST body
- **Frontend `usePomodoro.ts`** — `useStartSession` mutation takes `{ taskId?, durationMinutes? }` object instead of bare string
- **`LuxuryPomodoroTimer.tsx`** — Reads `pomodoroWorkDuration` from localStorage via `getPomodoroSettings()`, sends it when starting a session, uses session's actual `duration_minutes` for progress ring calculation
- **`PomodoroWidget/index.tsx`** — Same fix for the dashboard widget
- **`Pomodoro/index.tsx`** — Updated keyboard shortcut caller to use new mutation signature; removed hardcoded "25-minute" from subtitle

**Design Decision:** Progress ring uses the active session's `duration_minutes` (from server response) rather than current settings — handles the case where settings change mid-session or a session was started with a different duration.

**Verification:** TypeScript `tsc --noEmit` — 0 errors. Ruff check — all passed.

---

### Day 25: Appearance Settings Actually Work (Feb 18) — ~1 hour

Settings for theme (dark/light), accent color (indigo/cyan/orange/gold), and font size (small/medium/large) were being saved to localStorage but never applied to the DOM. The `useSettings` hook only lived on the Settings page — no other component consumed the values.

**Root Cause:** No bridge between localStorage persistence and CSS. The Tailwind config used hardcoded hex colors, so there was no mechanism for runtime theme switching.

**Fix — CSS custom properties + settings applier (10 files modified, 1 new file):**

- **`index.css`** — Added CSS custom properties for all 6 theme-dependent colors (`--luxury-obsidian-rgb`, `--luxury-charcoal-rgb`, `--luxury-card`, `--luxury-text-primary-rgb`, `--luxury-text-secondary-rgb`, `--luxury-border`). Added `[data-theme="light"]` overrides that swap backgrounds to light slate, text to dark navy, borders to dark-tinted. Added `[data-accent="cyan|orange|gold"]` overrides for `--luxury-accent-rgb`. Added `html[data-font-size="small|large"]` font-size scaling (14px/18px).
- **`tailwind.config.js`** — Changed 6 theme-dependent luxury colors from hardcoded hex to `rgb(var(--x) / <alpha-value>)` so Tailwind opacity modifiers (e.g., `bg-luxury-obsidian/90`) still work. Added `luxury-accent` color. Kept quadrant colors (`indigo`, `cyan`, `orange`, `slate`, `gold`) hardcoded — they're semantic, not user-configurable.
- **`hooks/useApplySettings.ts`** (new) — Effect that reads `artemis-settings` from localStorage and sets `data-theme`, `data-accent`, `data-font-size` attributes on `<html>`. Listens for `StorageEvent` (cross-tab) and custom `artemis-settings-change` event (same-tab instant updates).
- **`App.tsx`** — Calls `useApplySettings()` at the top level so settings apply on every page load.
- **`hooks/useSettings.ts`** — Dispatches `artemis-settings-change` custom event after every `localStorage.setItem`, so changes apply instantly without page reload.
- **6 component files** — Swapped `luxury-indigo` → `luxury-accent` for UI accent usages (focus rings, buttons, FAB gradient), keeping `luxury-indigo` for Q1 quadrant semantics: `Input`, `Select`, `Settings`, `AppShell`, `TaskCreationModal`, `LuxuryTaskSelector`.

**Design Decision:** Used `rgb(var() / <alpha-value>)` pattern (Tailwind v3 standard) instead of raw CSS variable colors. This preserves opacity modifier support — critical since 30+ existing usages like `bg-luxury-obsidian/90` and `bg-luxury-indigo/20` depend on it.

**Verification:** TypeScript `tsc --noEmit` — 0 errors. Vite build — success (962KB JS, 57KB CSS).

---

### Day 24: Pomodoro Polling Fix + PRD Overhaul (Feb 18) — ~1.5 hours

Eliminated redundant HTTP polling during active Pomodoro sessions. Both `LuxuryPomodoroTimer` and `PomodoroWidget` were running two real-time channels simultaneously: a WebSocket (receiving `TICK` messages every second) and TanStack Query HTTP polling (`GET /pomodoro/active` every 1s). The HTTP poll was flooding the terminal with requests while the WebSocket was already doing the same job.

**Fix:** Conditioned `refetchInterval` on WebSocket connection status — HTTP polling now only activates as a fallback when the WebSocket is disconnected.

**Changes (2 files, 0 new files, 0 new deps):**

- **`LuxuryPomodoroTimer.tsx`** — Moved `useActiveTimer` call after `usePomodoroWebSocket` hook. Changed `refetchInterval` from `state !== "IDLE" ? 1000 : undefined` to `state !== "IDLE" && !isConnected ? 1000 : undefined`.
- **`PomodoroWidget/index.tsx`** — Same change: `useActiveTimer` moved after WebSocket hook, polling gated on `!isConnected`.

**Also included:** `frontend/Dockerfile` — added `# check=skip=SecretsUsedInArgOrEnv` directive (pre-existing uncommitted change).

**Verification:** TypeScript `tsc --noEmit` — 0 errors.

**PRD Overhaul (1 file, +289/-143 lines)**

Full audit and update of `PRD.md` to reflect 24 days of development beyond the original plan. The PRD was written on Day 1 and hadn't been updated since — now reflects the actual architecture.

**Sections updated:**
- **Section 1 (Executive Summary)** — Added embedded chat UI, memory system, heartbeat, skills
- **Section 4 (MVP Scope)** — 3 new in-scope groups (Memory, Skills, DX). Moved chat UI + weekly reviews from "Out of Scope" to done. Updated note count (23)
- **Section 6 (Architecture)** — Rewrote diagram (Streamable HTTP, skills, heartbeat). Replaced entire directory tree (added `services/`, `frontend/`, `heartbeat/`, `scripts/`, `supabase/`, `decisions/`, `Meta/`). Added 3 new design patterns (memory injection, heartbeat suppression, vault skills)
- **Section 7 (Tools)** — Added Skills MCP tool group (5 ops). Fixed knowledge tool desc. Updated priorities
- **Section 8 (Tech Stack)** — Fixed transport (SSE → Streamable HTTP), ES version. Rewrote voice client as Python proxy. Added Frontend, Heartbeat, Artemis Backend stacks. Replaced Railway/Render with ngrok static domain
- **Section 9 (Config)** — Fixed `ELASTIC_CLOUD_ID` → `ELASTIC_URL`. Added 10+ missing env vars. Rewrote networking (10 connections)
- **Sections 11-12 (Success + Phases)** — Fixed note count, added wow moments, rewrote all 4 phases to match actual timeline
- **Sections 13-15 (Future + Risks + Appendix)** — Removed completed items, updated risks, fixed paths, updated checklist

---

### Day 23: Persistent Chat Conversations (Feb 18) — ~1 hour

Chat messages and conversation history now survive page refresh. Added Zustand `persist` middleware to localStorage and a conversation history panel in the ChatSidebar.

**Changes (2 files, 0 new files, 0 new deps):**

- **`chatStore.ts`** — Wrapped store with `persist` middleware (key: `athena-chat`). Added `Conversation` type and `conversations[]` state. New actions: `newConversation()`, `switchConversation(id)`, `deleteConversation(id)`. `addMessage` auto-upserts active conversation in history. `setConversationId` creates history entry on first server ID. `onRehydrateStorage` reinitializes `messageCounter` from persisted IDs. Transient UI state (`isOpen`, `voiceMode`, `status`) excluded via `partialize`.
- **`ChatSidebar/index.tsx`** — Added `ConversationList` internal component (sorted history, active highlight, hover-reveal delete, "New conversation" button). Two new header buttons: Clock (history toggle) and Plus (new chat). Messages area conditionally renders history panel vs chat.

**Verification:** TypeScript `tsc --noEmit` — 0 errors. Vite build — success (961KB JS, 55KB CSS).

---

### Day 22: Full Validation Pass (Feb 16) — ~30 min

Comprehensive validation across all 8 sub-projects. Ran ruff lint, pyright type checks, pytest, TypeScript checks, and Vite build. Everything green — zero errors across the board.

**Validation Results — 13/13 PASS**

| # | Check | Sub-project | Result |
|---|-------|-------------|--------|
| 1 | Ruff lint | mcp-server | PASS |
| 2 | Ruff lint | indexer | PASS |
| 3 | Ruff lint | heartbeat | PASS |
| 4 | Ruff lint | voice-client | PASS |
| 5 | Ruff lint | artemis-backend | PASS |
| 6 | Pyright | mcp-server | PASS (0 errors) |
| 7 | Pyright | indexer | PASS (0 errors) |
| 8 | Pyright | artemis-backend | PASS (0 errors) |
| 9 | TypeScript `tsc --noEmit` | frontend | PASS (0 errors) |
| 10 | Vite build | frontend | PASS (952KB JS, 55KB CSS) |
| 11 | Pytest | artemis-backend | PASS (27 passed, 8 skipped) |
| 12 | MCP import check | mcp-server | PASS (14 tools registered) |
| 13 | Parser smoke test | indexer | PASS (23 notes parsed) |

**Notes:**
- 8 skipped tests are integration tests requiring a live Supabase database (expected)
- artemis-backend `dev` optional deps needed `uv sync --extra dev` to install ruff/pytest
- Frontend needed `npm install` (node_modules not tracked in git)
- Sample vault now has 23 notes (up from 17 — skills + memory files added in Days 16-20)

---

### Day 21: Ship Command (Feb 16) — ~30 min

Created a `/ship` slash command that chains three workflow steps: update devlog, commit, and push. Eliminates the manual three-step end-of-session ritual by wrapping `/update-devlog` and `/commit` skills with a final `git push` into a single invocation.

**New Command**

- [x] `.claude/commands/ship.md` — Wrapper command that sequentially invokes `/update-devlog`, then `/commit` (including the updated DEVLOG.md), then pushes to remote. Each step waits for the previous to succeed.

**Key Additions**

| File | Lines | Purpose |
|------|-------|---------|
| `.claude/commands/ship.md` | 40 | Chained workflow: devlog + commit + push |

**Design Decision:** Chose a wrapper command over modifying the existing `/commit` skill to preserve the ability to commit without devlog updates when needed.

---

### Day 20: Skills System (Feb 16) — ~1 hour

Added a two-layer skills system: vault runtime skills (agent-native, stored in Obsidian) and Claude Code developer skills (for extending the codebase). Users can now say "run my morning routine" and the agent loads and executes a multi-step workflow from the vault. The agent can also create new skills from conversation.

**New MCP Tool: `skill_manager`**

- [x] `mcp-server/src/tools/skills.py` — 5 operations following the vault tool pattern: `list_skills` (scans `Meta/Skills/*.md`, extracts frontmatter), `load_skill` (reads full content), `create_skill` (writes with frontmatter + tags), `edit_skill` (preserves metadata, replaces content), `delete_skill` (requires `confirm_destructive=true`)
- [x] Registered in `server.py` — tool count 13 → 14

**Sample Vault Skills (3)**

- [x] `sample-vault/Meta/Skills/morning-routine.md` — Morning briefing: daily plan → pending tasks → recent changes → daily note → summary
- [x] `sample-vault/Meta/Skills/meeting-debrief.md` — Extract action items from meeting notes, classify by quadrant, create tasks, append debrief section
- [x] `sample-vault/Meta/Skills/weekly-review.md` — Weekly analytics → completed tasks → pending/overdue → vault activity → narrative review

**System Prompt Updates**

- [x] Added Skills tool documentation section (after Research tools)
- [x] Added tool selection row for multi-step workflows
- [x] Added Pattern 8 (Skill Execution) and Pattern 9 (Skill Creation)
- [x] Added Skills Awareness note to Memory & Context section

**Voice Proxy Skill Injection**

- [x] Extended `_read_memory_context()` in `serve.py` — scans `Meta/Skills/*.md`, parses frontmatter, injects "Available Skills" section with names and trigger phrases into `systemPromptAddition`
- [x] Added `python-frontmatter>=1.1.0` to voice-client dependencies

**Claude Code Developer Skills (2)**

- [x] `.claude/skills/customize/SKILL.md` — Documents both skill layers, how to add MCP tools, key files table, coding standards
- [x] `.claude/skills/add-integration/SKILL.md` — Step-by-step template for adding new service integrations (client adapter → tool module → config → server registration → system prompt → Agent Builder sync)

**Key Additions**

| File | Lines | Purpose |
|------|-------|---------|
| `mcp-server/src/tools/skills.py` | 130 | `skill_manager` MCP tool (5 operations) |
| `sample-vault/Meta/Skills/morning-routine.md` | 45 | Sample skill: morning briefing |
| `sample-vault/Meta/Skills/meeting-debrief.md` | 42 | Sample skill: meeting task extraction |
| `sample-vault/Meta/Skills/weekly-review.md` | 50 | Sample skill: weekly productivity review |
| `.claude/skills/customize/SKILL.md` | 75 | Developer skill: extending Athena |
| `.claude/skills/add-integration/SKILL.md` | 85 | Developer skill: adding integrations |

**Agent Builder Sync**

- [x] Synced updated system prompt to Agent Builder (14,508 → 16,277 chars)
- [x] Registered `athena.skill_manager` as MCP tool via Kibana API (`POST /api/agent_builder/tools`)
- [x] Added `athena.skill_manager` to agent's tool_ids (6 → 7 explicit IDs, 20 total tools)
- [x] Verified via converse API — "What skills do I have?" returns all 3 skills with trigger phrases

**Gotcha:** MCP tools require explicit registration in Agent Builder even though the connector auto-discovers the schema. The tool must also be added to the agent's `configuration.tools[0].tool_ids` list.

**Validation:** ruff check passes on all new/modified files, syntax verified, tool count confirmed at 14 MCP tools (20 total in Agent Builder). Converse API end-to-end test passes.

---

### Day 19: Setup Automation (Feb 16) — ~1.5 hours

Built a one-command project bootstrap (`./setup.sh`) that replaces the 5+ manual setup steps across Supabase, Elasticsearch, and Agent Builder. After filling in `.env`, a single command validates credentials, creates database tables, indexes the vault, registers all 19 tools in Kibana, creates the Athena agent, and verifies everything end-to-end.

**New Sub-project: `scripts/`**

- [x] `scripts/config.py` — Shared `SetupConfig` (pydantic-settings) loading all env vars from root `.env`
- [x] `scripts/validate_env.py` — Phase 1: checks required vars are set, tests ES + Supabase connectivity, warns on missing optional vars (voice, research, ngrok)
- [x] `scripts/setup_supabase.py` — Phase 2a: executes SQL migration via `psycopg` (pure Python Postgres driver), falls back to printing SQL + Supabase SQL Editor URL if `SUPABASE_DB_URL` not set, verifies tables via REST API
- [x] `scripts/setup_elasticsearch.py` — Phase 2b: runs `uv sync` + `athena-index setup-indices` + `athena-index index` via subprocess, verifies note count
- [x] `scripts/setup_agent_builder.py` — Phase 2c: creates ES|QL + index search tools from JSON files, creates MCP connector + 13 MCP tools (if ngrok reachable), creates/updates Athena agent with system prompt and all tool IDs. Handles "already exists" (HTTP 400/409) gracefully
- [x] `scripts/verify.py` — Phase 3: end-to-end health check table (Supabase tables, ES index, Agent Builder tools, agent, MCP connector, Docker services)
- [x] `scripts/setup.py` — Main orchestrator with `--phase` CLI flag for running individual phases

**SQL Migration**

- [x] Created `supabase/migrations/001_initial_schema.sql` — 3 tables (`tasks`, `daily_plans`, `pomodoro_sessions`), `updated_at` trigger function, `increment_pomodoro_count` RPC, RLS policies, role grants. All idempotent (`IF NOT EXISTS`, `CREATE OR REPLACE`)

**Shell Entry Points**

- [x] `setup.sh` — Linux/macOS: checks `.env`, Python, `uv`, installs deps, delegates to Python orchestrator
- [x] `setup.bat` — Windows equivalent

**Key Additions**

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/pyproject.toml` | 14 | Sub-project: httpx, pydantic-settings, rich, psycopg |
| `scripts/config.py` | 35 | Shared SetupConfig (pydantic-settings) |
| `scripts/validate_env.py` | 85 | Credential + connectivity validation |
| `scripts/setup_supabase.py` | 70 | Postgres DDL execution + REST API verification |
| `scripts/setup_elasticsearch.py` | 80 | ES indices + vault indexing via subprocess |
| `scripts/setup_agent_builder.py` | 220 | Kibana API: tools + connector + agent |
| `scripts/verify.py` | 105 | End-to-end health check table |
| `scripts/setup.py` | 95 | Main orchestrator with CLI |
| `supabase/migrations/001_initial_schema.sql` | 105 | Full database schema |
| `setup.sh` | 25 | Linux/macOS entry point |
| `setup.bat` | 28 | Windows entry point |

**API Discoveries**

- `GET /api/agent_builder/tools` returns `{"results": [...]}` (not a flat array)
- Agent tools are under `configuration.tools`, not top-level `tools`
- "Already exists" returns HTTP 400 with message, not HTTP 409

**Validation**

| Check | Result |
|-------|--------|
| `./setup.sh --phase validate` | All credentials valid, ES + Supabase reachable |
| `./setup.sh --phase supabase` | 3/3 tables verified |
| `./setup.sh --phase elasticsearch` | 20 notes indexed |
| `./setup.sh --phase agent-builder` | 6 tools (exists), agent updated |
| `./setup.sh --phase verify` | All critical checks pass |
| Full `./setup.sh` pipeline | End-to-end success |
| Idempotency (second run) | Identical output, no errors |

---

### Day 18: Heartbeat Service (Feb 16) — ~2 hours

Built a proactive heartbeat service that periodically wakes Athena to evaluate a user-defined checklist. Transforms the agent from purely reactive to proactive — nudges about overdue tasks, missing daily plans, and approaching deadlines.

**New Sub-project: `heartbeat/`**

- [x] Scaffolded `heartbeat/` sub-project with `uv` — APScheduler 3.11, httpx, pydantic-settings, python-frontmatter
- [x] `HeartbeatSettings` config class — interval, active hours, vault path, ES credentials, conversation ID persistence path
- [x] Core `heartbeat_tick()` function — reads checklist from vault, injects user profile + agent memory, calls Kibana converse API, parses response
- [x] `HEARTBEAT_OK` suppression — if agent finds nothing to report, response is silently discarded (debug log only)
- [x] Alert delivery to daily note — real alerts appended as `## Heartbeat Alert (HH:MM UTC)` blocks, creates daily note if missing
- [x] `CronTrigger` scheduler — runs every N minutes during active hours only (default: every 30 min, 8 AM - 10 PM)
- [x] Conversation ID persistence — file-based, maintains session continuity across ticks
- [x] Graceful shutdown via SIGTERM/SIGINT signal handling
- [x] Multi-stage Dockerfile matching mcp-server pattern

**Vault Checklist**

- [x] Created `sample-vault/Meta/heartbeat.md` — demo checklist with morning (plan check, deadline alerts), throughout-day (overdue Q1 tasks, late-day nudges), and evening (daily summary, carry-over suggestions) sections

**Docker Integration**

- [x] Added `heartbeat` service to `docker-compose.yml` under `heartbeat` profile (opt-in — costs LLM tokens per tick)
- [x] Added `HEARTBEAT_INTERVAL_MINUTES`, `HEARTBEAT_ACTIVE_HOUR_START`, `HEARTBEAT_ACTIVE_HOUR_END` to `.env.example`

**Key Additions**

| File | Lines | Purpose |
|------|-------|---------|
| `heartbeat/pyproject.toml` | 50 | Sub-project definition with APScheduler, httpx, pydantic-settings |
| `heartbeat/src/config.py` | 43 | HeartbeatSettings (pydantic-settings) |
| `heartbeat/src/heartbeat.py` | 245 | Core logic: scheduler, tick, memory injection, alert delivery |
| `heartbeat/src/__main__.py` | 15 | Entry point (`python -m src`) |
| `heartbeat/Dockerfile` | 30 | Multi-stage uv build |
| `sample-vault/Meta/heartbeat.md` | 30 | User-editable heartbeat checklist |

**Design Decisions**

- APScheduler v3 (stable) over v4 (alpha) — reliability for hackathon deadline
- `CronTrigger(minute="*/30", hour="8-21")` — native active-hours scheduling, no runtime guard
- Profile-gated Docker service — opt-in to avoid unintended LLM costs (~$0.50-2/day at 30-min intervals)
- Direct daily note writing for alerts — avoids circular dependency through converse API

**Validation:** ruff check (0 errors), ruff format (4 files clean), pyright (0 errors), Docker build succeeds, docker compose config validates.

---

### Day 17: System Prompt Sync to Agent Builder (Feb 16) — ~30 min

Re-synced the updated system prompt (with comprehensive memory guidance) to the live Athena agent in Elastic Agent Builder via Kibana REST API.

**System Prompt Sync**

- [x] Fetched current agent config via `GET /api/agent_builder/agents/athena` — confirmed old 4-line Memory & Context section was still deployed
- [x] Updated agent via `PUT /api/agent_builder/agents/athena` with full `agent-config/system-prompt.md` content
- [x] System prompt grew from 13,351 to 14,508 chars — new Memory & Context section adds Injected Memory, Updating Memory, and Conversation Summaries guidance
- [x] Verified 19/19 tools preserved in response (6 ES|QL + 13 MCP)
- [x] Confirmed memory keywords (`Injected Memory`, `Updating Memory`, `Conversation Summaries`) present in deployed instructions

**API Note:** Agent PUT endpoint rejects `id` in the request body (it's in the URL path) — different from the POST creation endpoint which required it.

**Result:** Agent Builder now running the latest system prompt. Memory injection (via voice proxy) and memory guidance (in system prompt) are both live. Ready for demo.

---

### Day 16: Memory System (Feb 16) — ~2 hours

Implemented persistent memory across sessions. The agent now knows who the user is, remembers past decisions, and writes conversation summaries to daily notes. Based on patterns from ADR-003 (OpenClaw/NanoClaw research).

**Memory Files**

- [x] Created `sample-vault/Meta/user-profile.md` — demo profile for "Stratos" with identity, communication preferences, vault organization, current focus, team members, and work patterns
- [x] Created `sample-vault/Meta/memory.md` — starter long-term memory with key decisions, project relationships, and discovered preferences
- [x] Added `"meta": "meta"` to `NOTE_TYPE_FOLDER_MAP` in both `mcp-server/src/vault_manager.py` and `indexer/src/parser.py`

**Memory Injection (Voice Proxy)**

- [x] Added `vault_path` setting to `VoiceSettings` class
- [x] Added `_read_memory_context()` helper — reads both Meta files, strips YAML frontmatter, truncates at 20K chars per file, graceful degradation on missing files
- [x] Injected memory into every chat request via `configuration_overrides.systemPromptAddition` in the converse API payload
- [x] Added vault volume mount (`/vault:ro`) and `VAULT_PATH` env var to `voice-proxy` service in `docker-compose.yml`

**Daily Note Write-back**

- [x] Enhanced `save_conversation_summary` to append `## Conversation Summary (HH:MM UTC)` blocks to daily notes via `vault_manager`
- [x] Creates daily note with proper frontmatter if it doesn't exist, matching existing daily note format
- [x] Non-fatal: vault write failures are logged but don't break the ES write-back
- [x] Return value now includes both `es_document_id` and `daily_note` path

**System Prompt Update**

- [x] Replaced 4-line Memory & Context section with comprehensive guide: injected memory usage, how to update `Meta/memory.md` via existing `vault_manage` tool, never modify profile without permission, distinction between memory updates and conversation summaries

**Key Additions**

| File | Lines | Purpose |
|------|-------|---------|
| `sample-vault/Meta/user-profile.md` | 39 | Demo user profile for memory injection |
| `sample-vault/Meta/memory.md` | 30 | Starter agent long-term memory |

**Validation:** All ruff lint/format checks pass. `_read_memory_context()` verified to read and format both files (2,744 chars). Docker Compose config validates with new volume mount.

---

### Day 15: Full End-to-End Validation (Feb 16) — ~1 hour

Systematic validation of every component and integration path. Tested indexer, MCP server (local + Docker), all 4 tool groups, Docker Compose (5 containers + ngrok), and full Agent Builder chat loop through Kibana converse API.

**Validation Results — 28/28 PASS**

| # | Component | Test | Result |
|---|-----------|------|--------|
| 1 | Indexer | Parse sample vault (17 notes) | PASS |
| 2 | Indexer | ES `athena-notes` count = 17 | PASS |
| 3 | Indexer | ELSER semantic search ("API refactoring plan" → #1 correct) | PASS |
| 4 | MCP Server | Streamable HTTP initialize (Athena v1.26.0) | PASS |
| 5 | MCP Server | tools/list (13 tools) | PASS |
| 6 | MCP Tool | `vault_query` → `list_structure` (17 notes) | PASS |
| 7 | MCP Tool | `vault_query` → `search_content` | PASS |
| 8 | MCP Tool | `vault_read` → `read_note` (full content + metadata) | PASS |
| 9 | MCP Tool | `vault_read` → `daily_note` (missing date — graceful error) | PASS |
| 10 | MCP Tool | `save_conversation_summary` → ES write-back | PASS |
| 11 | MCP Tool | `web_search` (Brave API) | PASS |
| 12 | MCP Tool | `artemis_list_tasks` (Artemis down — graceful error) | PASS |
| 13 | Docker | `docker compose config` (default + tunnel profile) | PASS |
| 14 | Docker | Build all 4 images | PASS |
| 15 | Docker | All 5 containers start (artemis, mcp-server, voice-proxy, frontend, ngrok) | PASS |
| 16 | Docker | Artemis health (`/health` — healthy, DB connected) | PASS |
| 17 | Docker | Voice proxy health (`/api/health`) | PASS |
| 18 | Docker | Frontend HTTP 200 | PASS |
| 19 | Docker | ngrok tunnel → static domain | PASS |
| 20 | Integration | MCP → Artemis (Docker network, 5 tasks returned) | PASS |
| 21 | Integration | MCP → Vault (Docker volume mount, 17 notes) | PASS |
| 22 | Integration | MCP → ES (conversation write-back) | PASS |
| 23 | Integration | ngrok → MCP (public URL) | PASS |
| 24 | Agent Builder | Converse API — semantic search query | PASS |
| 25 | Agent Builder | Converse API — vault read via MCP tools | PASS |

**Bug Found and Fixed**

- [x] `.env` had Windows line endings (`\r`) — fixed with `tr -d '\r'`. Caused `source .env` to fail in bash. File was likely edited on Windows at some point.

**Result:** All components, integrations, and the full Agent Builder → ngrok → MCP → Artemis/Vault/ES chain working. Ready for demo recording.

---

### Day 14: Monorepo Merge — Artemis into Athena (Feb 16) — ~1 hour

Executed ADR-004 Phase A: merged the Artemis backend and frontend into the Athena monorepo. Anyone can now `git clone` this single repo and run `docker compose up` — no sibling directory setup required.

**Monorepo Merge**

- [x] Copied 58 tracked files from `Artemis/backend/` to `services/artemis-backend/` using `git ls-files` (no `.venv`, `__pycache__`, or cache dirs)
- [x] Copied 122 tracked files from `Artemis/frontend/` to `frontend/` using same method
- [x] Updated `docker-compose.yml` — replaced `${ARTEMIS_PATH:-../Artemis/backend}` with `./services/artemis-backend`, `${ARTEMIS_ENV_FILE:-../Artemis/.env}` with `.env`, `${ARTEMIS_FRONTEND_PATH:-../Artemis/frontend}` with `./frontend`
- [x] Updated `.env.example` — removed `ARTEMIS_FRONTEND_PATH` variable, consolidated Artemis vars into single section with `CORS_ORIGINS`
- [x] Updated `.gitignore` — added `node_modules/`, `npm-debug.log*`, `frontend/dist/`, `*.tsbuildinfo`
- [x] Updated `README.md` — Artemis listed as included (not external prerequisite), project structure reflects `services/artemis-backend/` + `frontend/`
- [x] Updated `CLAUDE.md` — project structure shows new layout

**Validation**

| Check | Result |
|-------|--------|
| Backend file count | 58 (exact match) |
| Frontend file count | 122 (exact match) |
| `docker compose config` | PASS |
| `docker compose build artemis` | PASS |
| `docker compose build artemis-frontend` | PASS |
| No `../Artemis` references in config | PASS |
| Zero source code changes | Confirmed — no .py or .tsx files modified |

**Key decision:** Used `git ls-files` + copy instead of `git subtree add` (ADR-004 mentioned subtree, but it imports the entire Artemis repo — we only need 2 subdirectories). Commit message preserves provenance (Artemis commit `4ee701f`).

**Result:** Single-repo, single-command deployment. ADR-004 Phase A complete. Phase B (uv workspaces unification) deferred to post-hackathon.

**ngrok Static Domain**

- [x] Claimed free ngrok static domain: `sylas-saporific-ilona.ngrok-free.dev`
- [x] Updated `docker-compose.yml` ngrok service — added `--url=${NGROK_DOMAIN}` flag for stable URL across restarts
- [x] Added `NGROK_AUTHTOKEN` and `NGROK_DOMAIN` to `.env.example`
- [x] Updated MCP connector `serverUrl` in Kibana to permanent URL — no more URL churn on ngrok restart

---

### Day 13: Monorepo Strategy Research + Housekeeping (Feb 15) — ~1 hour

Researched how to merge the Artemis and Athena repositories into a single monorepo for hackathon submission and long-term maintainability. Evaluated 5 approaches (Bazel/Nx, subtree/submodule, file copy, fresh start, uv workspaces) against industry practices at Google, Meta, and startups. Decision: two-phase uv workspaces approach — Phase A (subtree merge, 2-4h) before deadline, Phase B (workspace unification) after hackathon.

**Research & Decisions**

- [x] Evaluated 5 monorepo strategies: full monorepo (Bazel/Nx/Pants), git subtree/submodule, file copy, fresh start, uv workspaces + Docker Compose
- [x] Researched industry patterns — Google (Bazel), Meta (Buck2), Microsoft (Rush), Apache Airflow (uv workspaces), startup practices
- [x] Chose two-phase approach: Phase A brings Artemis into Athena via `git subtree add` with path updates; Phase B adds root `pyproject.toml` with `[tool.uv.workspace]` post-hackathon
- [x] Created `decisions/004-monorepo-merge-strategy.md` — full ADR with target directory structure, step-by-step implementation plan, risk assessment, and rejected alternatives

**Housekeeping**

- [x] Archived 2 completed plans to `.agents/plans/archived/`: "Unified Athena + Artemis Experience (4 sessions)" (Days 8-9), "Add Artemis Frontend to Docker Compose" (Day 12)
- [x] Plans directory cleaned — all 10 historical plans now in `archived/`

**Key Additions**

| File | Lines | Purpose |
|------|-------|---------|
| `decisions/004-monorepo-merge-strategy.md` | 210 | ADR for Artemis→Athena monorepo merge strategy |

**Result:** Clear decision and implementation plan for merging repos. Phase A (subtree + path updates) is next actionable item, estimated 2-4 hours.

---

### Day 12: Artemis Frontend in Docker Compose (Feb 15) — ~30 min

Added the Artemis React frontend as a fourth Docker Compose service, so the entire stack starts with a single `docker compose up`. Created a custom nginx config that proxies `/athena/*` requests to the voice-proxy, matching the Vite dev proxy behavior.

**Changes**

- [x] Created `nginx.conf` — SPA routing with `try_files`, reverse proxy `location ^~ /athena/` → `voice-proxy:3001/api/`, static asset caching with 1-year expiry for hashed bundles
- [x] Added `artemis-frontend` service to `docker-compose.yml` — builds from `../Artemis/frontend` Dockerfile, injects `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `VITE_API_URL` as build args, volume-mounts custom nginx config over the Dockerfile's inline default
- [x] Updated `.env.example` — added Supabase variables and `ARTEMIS_FRONTEND_PATH`

**Code Review**

- [x] Verified proxy route chain: frontend `BASE_URL="/athena"` → nginx `/athena/` → `voice-proxy:3001/api/` → voice-proxy routes (`/api/chat`, `/api/transcribe`, `/api/speak`, `/api/health`)
- [x] Applied `^~` modifier to nginx `/athena/` location — prevents regex static asset location from intercepting proxy requests

**Key Additions**

| File | Lines | Purpose |
|------|-------|---------|
| `nginx.conf` | 25 | SPA routing + `/athena` reverse proxy + static asset caching |

**Result:** `docker compose up --build` starts 4 services. `http://localhost:3000` serves the full Artemis dashboard with Athena chat sidebar, voice, and all features.

---

### Day 11: End-to-End Validation on Linux (Feb 15) — ~1 hour

Systematic validation of every component on Linux. Tested indexer, MCP server (local + Docker), voice proxy, Artemis integration, ES write-back, web search, and full agent chat loop through Kibana. Fixed 3 bugs found during testing.

**Validation Results**

| Component | Test | Result |
|-----------|------|--------|
| Indexer | `parse_vault()` — 17 notes | PASS |
| Indexer | `athena-index index` — ES bulk sync | PASS (17 skipped, checksums match) |
| MCP Server | Streamable HTTP initialize + tools/list (13 tools) | PASS |
| MCP Server | `vault_query` → `list_structure` (17 notes) | PASS |
| MCP Server | `vault_read` → `read_note` (full content + metadata) | PASS |
| MCP Server | `vault_query` → `search_content` "API refactoring" | PASS (#1 hit correct) |
| MCP Server | `save_conversation_summary` → ES write-back | PASS |
| MCP Server | `web_search` → Brave API | PASS (3 results) |
| MCP Server | `artemis_list_tasks` (Artemis down) — graceful error | PASS |
| Voice Proxy | `/api/health`, static files, `/api/chat` → Kibana | PASS |
| Voice Proxy | Full agent loop (query → tools → rich response) | PASS |
| Docker Compose | `docker compose config` | PASS (after fix) |
| Docker Compose | Build all 3 images (artemis, mcp-server, voice-proxy) | PASS |
| Docker Compose | All 3 containers start and respond | PASS |
| Docker (MCP→Artemis) | `artemis_list_tasks` through container network | PASS |
| Docker (MCP→Vault) | `vault_query` with mounted volume (17 notes) | PASS |

**Bugs Fixed**

- [x] `indexer/src/config.py` — `env_file` only looked for `.env` in CWD; fixed to `(".env", "../.env")` matching MCP server pattern
- [x] `docker-compose.yml` — Artemis `env_file` pointed to `../Artemis/backend/.env` but actual file is at `../Artemis/.env`; added `ARTEMIS_ENV_FILE` variable
- [x] `docker-compose.yml` — Vault volume mount `"${VAULT_PATH:-.}/sample-vault:/vault:rw"` would double-nest when `VAULT_PATH` was set; fixed to `"${VAULT_PATH:-./sample-vault}:/vault:rw"`

**Known Issue**

- Agent in Elastic Cloud still references old ngrok URL — when starting a new tunnel, MCP connector URL must be updated in Kibana (documented in `deployment-gotchas.md`)

---

### Day 10: OpenClaw/NanoClaw Pattern Research (Feb 15) — ~1.5 hours

Deep research session analyzing OpenClaw and NanoClaw projects for patterns to adopt in Athena. Spawned 4 parallel research agents to cover architecture, memory, security, and heartbeat systems. No code changes — research and documentation only.

**Research Scope**

- [x] OpenClaw agent architecture — gateway, bootstrap files, session model, 70+ skills
- [x] OpenClaw memory system — SOUL.md/USER.md/MEMORY.md hierarchy, pre-compaction flush, hybrid search (70% vector / 30% BM25), session-memory hook
- [x] NanoClaw secure variant — container isolation (Apple Container/Docker), CLAUDE.md-based memory per group, PreCompact conversation archiving, task scheduler
- [x] Heartbeat patterns — OpenClaw's 30-min cron with HEARTBEAT_OK suppression, NanoClaw's idle timeout model, proactive agent reference project in `reference/`
- [x] Elastic Agent Builder integration analysis — `configuration_overrides.systemPromptAddition` for memory injection, converse API for heartbeat

**Key Findings**

| Pattern | OpenClaw | Athena Equivalent |
|---------|----------|-------------------|
| SOUL.md (personality) | Workspace bootstrap file | `agent-config/system-prompt.md` (exists) |
| USER.md (user identity) | Workspace bootstrap file | New — `vault: Meta/user-profile.md` |
| MEMORY.md (decisions/lessons) | Workspace bootstrap file | New — `vault: Meta/memory.md` |
| HEARTBEAT.md (proactive checklist) | Cron-triggered agent turn | New — APScheduler or cron calling converse API |
| Daily memory logs | `memory/YYYY-MM-DD.md` | Obsidian Daily Notes (already supported) |
| Session summaries | Hook on `/new` command | `save_conversation_summary` (already implemented) |

**Decisions**

- Memory files live in the Obsidian vault (`Meta/` folder) — stays in user's knowledge graph, editable in Obsidian
- Memory injection via `configuration_overrides.systemPromptAddition` — no agent code changes needed
- Heartbeat: cron script for hackathon, APScheduler service post-hackathon
- Skills system deferred — MCP tools already provide modularity

**Prioritization for remaining 12 days:**
1. End-to-end validation (~2h)
2. Memory files + injection (~4h)
3. Demo video recording (~3h)
4. Heartbeat service (~3h, if time allows)
5. Artemis sidebar integration (~7-8h, post-hackathon)

**Output:** `decisions/003-openclaw-patterns-research.md` (329 lines) — full ADR with research findings, mapping tables, feasibility matrix, and 4-step implementation plan.

---

### Day 9: End-to-End Integration Fixes (Feb 14) — ~1 hour

Bugs discovered during Windows end-to-end testing. Fixed Docker build failures, container health checks, and two critical Artemis frontend issues that broke the chat sidebar when talking to the live Agent Builder.

**Docker Build Fixes**

- [x] Tracked `uv.lock` files in git — removed `uv.lock` from `.gitignore` and committed lock files for indexer, mcp-server, and voice-client. Docker builds use `--frozen`/`--locked` which require these files to exist
- [x] Fixed `docker-compose.yml` healthcheck — replaced `curl` (not installed in `python:3.12-slim`) with Python `urllib.request.urlopen()`, matching the Dockerfile's own HEALTHCHECK approach
- [x] Softened `mcp-server` → `artemis` dependency from `service_healthy` to `service_started` — all services now start in parallel, mcp-server handles Artemis unavailability gracefully at runtime
- [x] Added `start_period: 10s` and `retries: 5` to healthcheck — gives Artemis time to boot before declaring unhealthy

**Artemis Frontend Integration Fixes (cross-repo)**

- [x] Fixed black screen crash — Kibana Agent Builder returns `{ response: { message: "..." } }` but React client expected `{ response: "..." }`. Passing an object to `marked.parse()` crashed React's entire render tree. Added nested extraction matching original `voice.js` pattern
- [x] Added TanStack Query cache invalidation after every agent response — invalidates pomodoro, tasks, dailyPlans, and analytics query keys so dashboard reflects agent-triggered actions immediately without manual refresh

**Validation:**

| Check | Result |
|-------|--------|
| `docker compose up --build -d` (Windows) | All 3 services start |
| Chat "hi" via sidebar | Agent responds, renders correctly |
| "Start a Pomodoro" via sidebar | Pomodoro starts, timer widget updates live |
| "Create a task" via sidebar | Task appears on Tasks page immediately |

---

### Day 8: Unified Athena + Artemis Experience (Feb 14) — ~3.5 hours

Consolidated the multi-terminal setup into one `docker compose up` command and embedded Athena as a chat sidebar inside the Artemis React app. Three implementation sessions: backend infrastructure, React chat component, and voice polish.

**Backend Infrastructure**

- [x] Fixed MCP server Dockerfile CMD bug — `src.server` → `src` (avoids double-import, documented in Day 7)
- [x] Added CORS middleware to voice proxy (`@web.middleware` with preflight handling) — required for cross-origin requests from Artemis frontend
- [x] Created voice-client Dockerfile — multi-stage uv build matching mcp-server pattern, serves `serve.py` + static assets
- [x] Consolidated `docker-compose.yml` — removed `profiles: [full]` from Artemis (always starts), added `voice-proxy` service (port 3001), added `ngrok` service under `profiles: [tunnel]` (image `ngrok/ngrok:latest`, exposes inspector at port 4040)

**React Chat Component (Artemis frontend)**

- [x] Installed `marked` + `dompurify` for markdown rendering in chat bubbles
- [x] Added Vite dev proxy: `/athena/*` → `localhost:3001/api/*` (no CORS issues in dev)
- [x] Created `athena-api.ts` — fetch-based API client (`athenaChat`, `athenaTranscribe`, `athenaSpeak`) following existing `api.ts` wrapper pattern
- [x] Created `chatStore.ts` — Zustand store (messages, conversationId, status, voiceMode) following `timerStore.ts` pattern
- [x] Created `useAthenaChat` hook — wires store + API, manages conversation ID across turns, returns response text for voice hook
- [x] Created `ChatSidebar` component — 420px right drawer on desktop, full-screen on mobile, spring slide-in animation, glassmorphism styling, markdown rendering with DOMPurify sanitization, welcome screen with hint chips, thinking indicator with pulsing dots
- [x] Integrated into `AppShell` — floating action button (gradient indigo→gold, positioned above mobile BottomNav), content right-padding shift when sidebar open on desktop

**Voice + Polish**

- [x] Created `useVoiceRecorder` hook — MediaRecorder with opus codec preference, mic track cleanup on stop/cancel
- [x] Created `useAthenaVoice` hook — orchestrates record → transcribe → chat → speak pipeline, reads voice/auto-speak settings from localStorage
- [x] Enhanced ChatSidebar with voice mode toggle, large animated mic button (red pulse when recording, animated ring), settings dialog (Radix Dialog with voice selection dropdown + auto-speak toggle), status indicators for all states (recording/transcribing/thinking/speaking with distinct animations), keyboard shortcuts (Space to toggle recording in voice mode, Escape to cancel/close)

**Key Additions**

| File | Location | Purpose |
|------|----------|---------|
| `voice-client/Dockerfile` | Athena | Docker image for voice proxy |
| `src/lib/athena-api.ts` | Artemis frontend | Athena API client |
| `src/stores/chatStore.ts` | Artemis frontend | Chat state management |
| `src/hooks/useAthenaChat.ts` | Artemis frontend | Text chat hook |
| `src/hooks/useVoiceRecorder.ts` | Artemis frontend | MediaRecorder wrapper |
| `src/hooks/useAthenaVoice.ts` | Artemis frontend | Voice pipeline orchestration |
| `src/design-system/.../ChatSidebar/` | Artemis frontend | Chat sidebar component + types |

**Validation:** TypeScript compiles with 0 errors, Vite build succeeds (952KB JS, 55KB CSS).

---

### Day 1: Scaffold + Elasticsearch Setup (Feb 12) — ~1 hour

Started from the PRD. Built the full project skeleton and connected to Elastic Cloud.

**Project scaffold:** Created 4 sub-projects with `uv` — `indexer/` (Obsidian → ES sync CLI), `mcp-server/` (unified MCP server), `voice-client/` (thin HTML/JS voice UI), `agent-config/` (Agent Builder system prompt + ES|QL tools). All with `pyproject.toml`, ruff config, pytest setup, and proper `.gitignore`.

**Configuration:** `pydantic-settings` configs for both indexer and MCP server. `.env.example` with all variables documented. Docker Compose with vault volume mount and optional Artemis profile.

**Elasticsearch Cloud Serverless:** Signed up for trial. Discovered ELSER v2 is available as a built-in inference endpoint (`.elser-2-elastic`) on Serverless — no model deployment needed. Updated `mappings.py` to reference it. Created both indices via REST API:
- `athena-notes` — `semantic_text` field for ELSER-powered search, keyword fields for tags/path/type, date fields for temporal queries
- `athena-conversations` — `semantic_text` for conversation memory search, keyword arrays for topics and task IDs

**MCP server Dockerfile:** Multi-stage build with `uv` for fast installs — builder stage resolves deps, runtime stage copies only the venv. Vault mounted at `/vault` via Docker Compose volume.

**Key decisions:**
- `.elser-2-elastic` (Elastic-hosted) over `.elser-2-elasticsearch` (self-hosted) — managed model, zero ML node config, automatic scaling on Serverless
- `semantic_text` field type — handles chunking and embedding automatically at index time, no client-side embedding code needed
- Single unified MCP server — all tools (vault, Artemis, knowledge, research) in one process, one SSE connection for Agent Builder to manage

---

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Elastic Agent Builder | Orchestrator with built-in conversation management, tool routing, and LLM connector — no custom agent framework needed |
| Dual-path knowledge access | ES for semantic search + analytics; direct vault filesystem for real-time read/write |
| 3-tool vault consolidation | `vault_query`, `vault_read`, `vault_manage` with operation parameters — fewer tools for the LLM to choose from |
| ELSER v2 via `semantic_text` | Zero embedding code — ES handles chunking, inference, and sparse vector storage automatically |
| MCP protocol (Streamable HTTP) | Standard protocol supported by Agent Builder; switched from SSE to Streamable HTTP (Elastic's connector requirement) |
| `pydantic-settings` for config | Type-safe env var loading with `.env` file support, consistent across both sub-projects |
| Docker volume mount for vault | Scoped filesystem access (`/vault:rw`), same path resolution in dev and production |
| Checksum-based dedup | MD5 of file content for change detection, SHA-256 of vault-relative path for deterministic ES `_id` — two hashes for two purposes |
| `confirm_destructive` pattern | Vault delete operations require explicit flag — prevents accidental data loss from LLM tool calls |
| Voice as pure client layer | Agent never knows if input was typed or spoken — zero backend changes for voice support |
| `ELASTIC_URL` over `ELASTIC_CLOUD_ID` | Serverless uses a direct HTTPS URL, not a cloud ID — clearer naming |
| Scroll API for checksum fetch | Handles vaults with >1000 notes; paginated retrieval of all (path, checksum) pairs |
| `extra: ignore` in settings | Shared `.env` has vars for all services — each sub-project ignores what it doesn't need |
| Streamable HTTP over SSE | Elastic Agent Builder's MCP connector only supports Streamable HTTP transport |
| `streamable_http_path="/"` | Elastic's connector POSTs to root `/`, not the FastMCP default `/mcp` |
| `__main__.py` entry point | Avoids Python double-import when running `python -m src` vs `src.server` |
| Kibana API for setup | All Agent Builder config (tools, connectors, agents) done via REST API — reproducible, scriptable |

---

## Tool Surface

**ES|QL Tools (Agent Builder):** `search_notes`, `get_recent_notes`, `get_notes_by_tag`, `get_conversation_history`, `count_notes_by_tag` + `semantic_search` (index search)

**MCP — Vault:** `vault_query` (4 operations), `vault_read` (3 operations), `vault_manage` (6 operations)

**MCP — Artemis:** `artemis_create_task`, `artemis_list_tasks`, `artemis_complete_task`, `artemis_get_daily_plan`, `artemis_assign_to_plan`, `artemis_get_analytics`, `artemis_start_pomodoro`

**MCP — Knowledge:** `save_conversation_summary`

**MCP — Research:** `web_search`, `fetch_url`

**MCP — Skills:** `skill_manager` (5 operations: list_skills, load_skill, create_skill, edit_skill, delete_skill)

### Day 2: Indexer Core Implementation (Feb 12) — ~1 hour

Built the full indexer pipeline: vault parsing → checksum dedup → bulk ES indexing → live filesystem watch.

**`parser.py`** — `ParsedNote` Pydantic model matching the `athena-notes` ES mapping. `parse_note()` reads a single `.md` file with `python-frontmatter`, extracts title/tags/dates from YAML frontmatter (with filesystem stat fallback for missing dates), infers `note_type` from folder name, computes MD5 checksum for change detection. `parse_vault()` iterates all `.md` files via `rglob`, skipping hidden directories (`.obsidian`, `.trash`). SHA-256 of `vault_relative_path` used as deterministic ES `_id` for upserts.

**`indexer.py`** — `VaultIndexer` class with async Elasticsearch client. `setup_indices()` creates both indices from `mappings.py` definitions if they don't exist. `index_vault()` parses the full vault, fetches existing checksums via scroll API, skips unchanged files, then bulk-indexes the rest via `async_bulk`. `index_single_note()` and `delete_note()` methods support the watcher. `IndexResult` dataclass tracks counts and errors.

**`cli.py`** — argparse CLI with 3 subcommands: `setup-indices` (create ES indices), `index` (bulk sync vault → ES), `watch` (live filesystem sync). Rich console output with tables and panels. `asyncio.run()` at the CLI boundary, async internals.

**`watcher.py`** — watchdog `FileSystemEventHandler` subclass that bridges sync filesystem callbacks to async ES operations via `asyncio.run_coroutine_threadsafe()`. Handles create, modify, delete, and move events for `.md` files.

**Config fix:** Renamed `ELASTIC_CLOUD_ID` → `ELASTIC_URL` across all 4 config files (`.env`, `.env.example`, `indexer/src/config.py`, `mcp-server/src/config.py`). Elasticsearch Serverless uses a direct URL, not a cloud ID. Added `"extra": "ignore"` to `IndexerSettings` since the shared `.env` contains vars for all services.

**Build fix:** Added `[build-system]` (hatchling) and `[tool.hatch.build.targets.wheel]` to `indexer/pyproject.toml` — required for `uv` to install the `src` package and expose the `athena-index` CLI entry point.

**Validated end-to-end:**
- `athena-index setup-indices` → both indices reported as existing (created on Day 1)
- `athena-index index` on empty `sample-vault/` → 0 files, 0 errors
- All files pass `ruff check` and `ruff format --check`

### Day 3: Sample Vault + Indexer Pipeline Validation (Feb 12) — ~1 hour

Created 17 realistic demo notes and validated the full indexer pipeline end-to-end against Elasticsearch.

**Sample vault** — 17 markdown notes across 5 folders using a "Stratos/Helios" productivity app narrative. All notes have valid YAML frontmatter (title, tags list, created/updated dates). Content includes 135 `[[wikilinks]]` for cross-referencing, code blocks, tables, and task lists. Covers all PRD user stories:

| Folder | Notes | Type |
|--------|-------|------|
| Research/ | 3 | research |
| Ideas/ | 3 | idea |
| Projects/ | 4 | project |
| Meeting Notes/ | 3 | meeting |
| Daily Notes/ | 4 | daily |

**Key content for demo scenarios:**
- `API Refactoring.md` — 7 extractable tasks (5 `- [ ]`, 1 `TODO:`, 1 `Action item:`) for US-7 task extraction
- `Sprint Review 2026-02-07.md` — 5 numbered action items for meeting follow-up demo
- `2026-02-11.md` — 5 pomodoro entries with timestamps for US-8 productivity analytics
- `2026-02-12.md` — Today's priorities with P0/P1/P2 for US-5 daily planning
- All 17 notes contain wikilinks for cross-note relationship demos

**Pipeline validation results:**

| Check | Result |
|-------|--------|
| Parser dry-run | 17 parsed, 0 errors |
| Bulk index (first run) | 17 indexed, 0 skipped, 0 errors |
| Checksum dedup (re-run) | 0 indexed, 17 skipped |
| ES document count | 17 |
| Type distribution | daily=4, project=4, idea=3, meeting=3, research=3 |
| Semantic: "API refactoring plan" | API Refactoring at #1 |
| Semantic: "user authentication login" | Authentication Module at #1 |
| Semantic: "sprint review discussion" | Sprint Review at #1 |

**Config update:** Set `VAULT_PATH=/home/stardust/Athena/sample-vault` in `.env`. Removed `.gitkeep` placeholder files from all 5 folders.

**ELSER semantic search quality:** Queries with zero keyword overlap still return correct results. "How to handle user login" matches Authentication Module and JWT Patterns despite neither containing the word "login" verbatim — ELSER's semantic expansion working as expected.

### Day 6: Agent Builder Configuration (Feb 13) — ~1 hour

Wrote the complete Athena system prompt, defined all ES|QL tool specifications, and created the setup guide. The agent now has a brain.

**System prompt** (`agent-config/system-prompt.md`, 244 lines) — Complete Athena persona following Elastic's recommended `Goal / Steps / Guardrails` structure with patterns adapted from the Paddy reference agent. Encodes:
- Identity and conversational tone
- Full tool inventory (6 ES|QL + 13 MCP tools) with descriptions
- Tool selection decision matrix (semantic vs keyword, ES|QL vs vault MCP, when to use which)
- 7 workflow patterns (knowledge search, task extraction, daily planning, idea capture, research, productivity check-in, conversation memory)
- Eisenhower Matrix classification rules with concrete vault examples
- 1-3-5 daily planning rule with step-by-step process
- Human-in-the-loop guardrails (never create/edit/delete without confirmation)
- Error recovery and search fallback strategy
- Output formatting guidelines

**ES|QL tool definitions** (5 JSON files in `agent-config/tools/`):

| Tool | Query Pattern | Key Technique |
|------|--------------|---------------|
| `search-notes.json` | Hybrid semantic + full-text | `MATCH(content_semantic, ..., {"boost": 0.7}) OR MATCH(content, ..., {"boost": 0.3})` |
| `get-recent-notes.json` | Temporal filter | `NOW() - TO_TIMEDURATION(?time_range)` for parameterized date ranges |
| `get-notes-by-tag.json` | Tag filter | `MV_EXPAND tags` before `WHERE tags == ?tag` for keyword arrays |
| `count-notes-by-tag.json` | Tag aggregation | `MV_EXPAND tags` then `STATS COUNT(*) BY tags` — no parameters |
| `get-conversation-history.json` | Conversation search | Queries `athena-conversations` index with `MATCH(summary_semantic, ?topic)` |

**Index search tool** (`notes-semantic-search.json`) — Dynamic natural-language search that auto-generates ES|QL queries. Complements the predefined templates for complex/ad-hoc queries.

**Setup guide** (`agent-config/setup-guide.md`, 128 lines) — Step-by-step instructions covering LLM connector setup, ES|QL tool creation (UI + API), MCP server registration, agent creation with all tools, end-to-end verification queries, and troubleshooting table.

**Validation results:**

| Check | Result |
|-------|--------|
| JSON syntax (6 files) | All valid |
| Field name cross-reference | All fields match `mappings.py` |
| Tool-prompt consistency | 18/18 tools referenced in prompt |
| Prompt length | 244 lines (under 400 target) |

### Day 7: Deployment — ngrok + Agent Builder Registration (Feb 13) — ~1 hour

Deployed the MCP server to the public internet via ngrok and registered everything in Elastic Agent Builder via API. The agent is now live and responding.

**ngrok setup** — Installed ngrok binary to `~/.local/bin/ngrok` (apt unavailable without sudo). Authenticated with auth token. Tunneling port 8001 to a public HTTPS URL.

**Transport migration: SSE → Streamable HTTP** — Elastic's MCP connector requires Streamable HTTP transport, not SSE. Changed `mcp.run(transport="streamable-http")` in the server. Also set `streamable_http_path="/"` in the FastMCP constructor because Elastic's connector POSTs to the root path `/`, not the default `/mcp`.

**Double-import fix** — Discovered that `python -m src.server` causes a Python double-import: the module loads as `__main__`, but tool modules `from src.server import mcp` load it again as `src.server`, creating a second `mcp` instance. Tools register on the second instance while `run()` is called on the first (empty) one. Fixed by adding `src/__main__.py` as the entry point — now `python -m src` works correctly.

**Config fix** — MCP server config was only loading `.env` from its own directory. Updated `env_file` to `(".env", "../.env")` so it finds the project root `.env` when running locally (not in Docker).

**Agent Builder API registration** — All configuration done via Kibana REST API:
- Created MCP connector (type `.mcp`, `serverUrl` pointing to ngrok URL)
- Created 5 ES|QL tools + 1 index search tool from `agent-config/tools/*.json`
- Registered 13 MCP tools (type `mcp` with `connector_id` and `tool_name`)
- Created Athena agent with 19 tools and 13,351-char system prompt (field name: `instructions`)

**API discoveries:**

| Field | Expected | Actual |
|-------|----------|--------|
| MCP connector URL field | `url` | `serverUrl` |
| Agent system prompt field | `system_prompt` | `instructions` |
| Agent `type` field | Required | Auto-set, must be omitted |
| ES|QL param types | `keyword` allowed | Only `string`, `integer`, `float`, `boolean`, `date`, `array` |

**ES|QL tool fix** — `get-notes-by-tag.json` had `"type": "keyword"` for the tag parameter, which the API rejected. Changed to `"type": "string"`.

**Verification results:**

| Check | Result |
|-------|--------|
| MCP server starts | Streamable HTTP on port 8001 |
| ngrok tunnel | HTTPS URL proxying to localhost:8001 |
| Elastic connector discovers tools | 13/13 MCP tools found |
| Agent created | 19 tools + system prompt loaded |
| Athena responds in Kibana chat | Working — searches vault, reads notes |

**Key files changed:**

| File | Change |
|------|--------|
| `mcp-server/src/server.py` | Streamable HTTP transport, `streamable_http_path="/"` |
| `mcp-server/src/__main__.py` | New entry point to avoid double-import |
| `mcp-server/src/config.py` | `env_file: (".env", "../.env")`, `extra: "ignore"` |
| `agent-config/tools/get-notes-by-tag.json` | Param type `keyword` → `string` |

---

### Day 5: Validation + Type Checking (Feb 13) — ~30 min

Ran comprehensive validation across both sub-projects and added static type checking.

**Full project validation:**

| Check | indexer/ | mcp-server/ |
|-------|---------|-------------|
| `ruff check` | All passed | All passed |
| `ruff format --check` | 7 files formatted | 7 files formatted |
| Module imports | All 6 modules OK | All 11 modules OK |
| `docker-compose.yml` | N/A | Depends on undefined `artemis` service |
| Tests | No test files yet | No test files yet |

**Added pyright to both sub-projects** as a dev dependency (`>=1.1.390`). Pyright over mypy — faster, better inference, less config, good pydantic v2 support out of the box.

**mcp-server:** Passed pyright with 0 errors immediately — clean types throughout.

**indexer:** Had 15 type errors across 3 files, all fixed:

| File | Errors | Fix |
|------|--------|-----|
| `config.py` | 1 (missing args) | `# type: ignore[call-arg]` — pydantic-settings loads required fields from env vars |
| `indexer.py` | 2 (iterable + param) | `isinstance` guard on `async_bulk` return; `# type: ignore` on ES `ignore=` runtime param |
| `watcher.py` | 12 (`bytes \| str`) | Extract `str(event.src_path)` into local vars — watchdog types `src_path` as `bytes \| str` |

**Known issue found:** `docker-compose.yml` has `mcp-server` depending on an undefined `artemis` service — needs the service definition added or the dependency removed.

### Day 4: MCP Server Implementation (Feb 12) — ~1 hour

Built the entire MCP server — 3 adapter classes, 13 MCP tools across 4 groups, and the FastMCP entry point with SSE transport.

**Adapter classes (Phase 1 — no MCP dependency):**

- `vault_manager.py` (~465 lines) — `VaultManager` class with path validation (directory traversal prevention via `resolve()` + `startswith()`), frontmatter parsing via `python-frontmatter`, full CRUD (create, read, append, edit, delete, move), folder creation, and 3 search modes (keyword with filename/title/content scoring, metadata filtering by tags/folder/date, recency by mtime). Pydantic models `NoteSummary` and `NoteContent` for structured output. `confirm_destructive` gate on deletes.
- `artemis_client.py` (~100 lines) — Thin `httpx.AsyncClient` wrapper over 7 Artemis REST endpoints plus health check. Query param construction for `list_tasks`, JSON body building for `create_task`/`assign_to_plan`/`start_pomodoro`.
- `es_client.py` (~44 lines) — `KnowledgeStore` with single `save_conversation()` method indexing to `athena-conversations`. Sets `summary_semantic` = `summary` (ELSER embeds at index time).

**MCP tools (Phase 2 — 13 tools across 4 modules):**

| Module | Tools | Pattern |
|--------|-------|---------|
| `tools/artemis.py` | 7 tools | Direct proxy to ArtemisClient with `httpx.HTTPStatusError`/`ConnectError` handling |
| `tools/vault.py` | 3 tools | Operation dispatch (`vault_query` 4 ops, `vault_read` 3 ops, `vault_manage` 6 ops) |
| `tools/knowledge.py` | 1 tool | `save_conversation_summary` with ES-not-configured graceful fallback |
| `tools/research.py` | 2 tools | `web_search` (Tavily preferred, Brave fallback), `fetch_url` (html2text, 5K char truncation) |

**Server wiring (Phase 3):**

- `server.py` — Creates `FastMCP("Athena")` with host/port config, initializes adapter singletons at module level, conditionally creates `KnowledgeStore` (ES credentials optional), imports tool modules to trigger `@mcp.tool()` registration. Tool modules import `mcp` and adapters from `server.py` (circular import safe because adapters are defined before tool imports).

**Key findings:**

- FastMCP v1.26 moved `host`/`port` from `run()` to the constructor — plan specified the older API
- Dockerfile was missing `uv.lock` in COPY directive — fixed to support `--locked` builds

**Validation results:**

| Check | Result |
|-------|--------|
| `ruff check` | All checks passed |
| `ruff format --check` | 11 files formatted |
| Adapter imports | All resolve OK |
| VaultManager smoke test | 17 notes, read/search/recent all work |
| Server startup | Starts on port 8001, serves SSE |
| Docker build | `athena-mcp:latest` built successfully |

---

## What's Next

Phases 1-2 complete. Unified experience built. Linux E2E validated. Remaining work:

- ~~Build the indexer, sample vault, MCP server, vault tools~~ done
- ~~Configure Agent Builder, deploy via ngrok~~ done
- ~~Unified Docker Compose + Artemis chat sidebar~~ done
- ~~End-to-end validation via sidebar~~ done
- ~~OpenClaw/NanoClaw pattern research~~ done (ADR-003)
- ~~End-to-end validation on Linux~~ done (Day 11)
- ~~Artemis frontend in Docker Compose~~ done (Day 12)
- ~~Monorepo strategy research~~ done (ADR-004, Day 13)
- ~~Monorepo merge: Phase A~~ done (Day 14) — Artemis copied into `services/artemis-backend/` + `frontend/`
- ~~Memory system~~ done (Day 16) — profile + memory files, voice proxy injection, daily note write-back
- ~~Re-sync system prompt in Agent Builder~~ done (Day 17) — 14.5k chars, memory guidance live
- ~~Heartbeat service~~ done (Day 18) — APScheduler + converse API, HEARTBEAT_OK suppression, daily note alerts
- ~~Setup automation~~ done (Day 19) — `./setup.sh` one-command bootstrap, SQL migration, Kibana API automation
- ~~Skills system~~ done (Day 20) — vault runtime skills + Claude Code developer skills, 3 sample skills
- Demo video recording (while Elastic Cloud trial is active)
- Optional: streaming support (SSE token-by-token responses)

---

*Last updated: February 23, 2026 (Day 37)*
