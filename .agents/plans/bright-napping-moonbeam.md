# Plan: Demote Pomodoro Timer, Promote Daily Plan to Dashboard Hero

## Context

The dashboard's 3-column layout puts the Pomodoro timer (a 180px circular ring) in the center — the most prominent position. But the timer is low-information-density (one number + one button) compared to the Plan (9 task slots) and Matrix (4 quadrant cards). The timer deserves a supporting role, not the hero spot. The Plan — "what should I work on?" — is the natural center piece.

## Target Layout

```
Desktop (lg+):
┌──────────────┬──────────────┬──────────────┐
│  Eisenhower  │ Today's Plan │  ⏱ Compact   │
│  Matrix      │  (★ HERO)    │  Timer       │
│  (compact)   │  1-3-5 slots │  ─────────── │
│  2x2 grid    │  + progress  │  18:42       │
│              │              │  Focus       │
│              │              │  ▓▓▓▓░░░░░░  │
│              │              │  [Stop]      │
│              │              │  2 sessions  │
├──────────────┴──────────────┴──────────────┤
│              Stats Bar (unchanged)          │
└─────────────────────────────────────────────┘

Mobile (<lg): stacks Plan → Timer → Matrix (Plan first)
```

## Changes (4 files, ~40 lines, 0 new files)

### 1. Add `compact` prop to PomodoroWidget types
**File:** `frontend/src/design-system/components/features/PomodoroWidget/PomodoroWidget.types.ts`

Add `compact?: boolean` — mirrors the existing pattern in `QuadrantGrid.types.ts`.

### 2. Add compact rendering path to PomodoroWidget
**File:** `frontend/src/design-system/components/features/PomodoroWidget/index.tsx`

Destructure `compact` from props. When `compact` is true:
- **No ProgressRing** — replace with a horizontal progress bar (`h-1.5 bg-white/5 rounded-full`, same pattern as `PlanWidget/index.tsx:89`)
- Progress bar color: `bg-luxury-indigo` for WORK, `bg-luxury-gold` for breaks
- Countdown: `text-2xl` (down from `text-3xl`)
- Padding: `p-4` (down from `p-6`)
- Title: `text-sm`
- Tighter spacing throughout (`mb-2`/`mb-3` instead of `mb-4`)

All hook logic, state management, WebSocket handling — **zero changes**. Only the JSX return block changes conditionally.

### 3. Pass `compact` from dashboard
**File:** `frontend/src/pages-new/Dashboard/components/DashboardTimerColumn.tsx`

One-line change: `<PomodoroWidget compact />`

### 4. Reorder columns with CSS `order`
**File:** `frontend/src/pages-new/Dashboard/index.tsx`

Keep DOM order as Plan → Timer → Matrix (correct mobile stacking priority). Add `lg:order-*` wrapper divs for desktop visual reorder:
- Plan: `lg:order-2` (center)
- Timer: `lg:order-3` (right)
- Matrix: `lg:order-1` (left)

## Not Affected

- `/pomodoro` page — uses `LuxuryPomodoroTimer` (360px ring), not `PomodoroWidget`
- `DailyStatsBar` — unchanged
- Mobile FAB — unchanged
- All timer functionality (start/stop/WebSocket/auto-complete) — zero behavioral changes

## Verification

1. `npx tsc --noEmit` — 0 errors
2. Desktop: Matrix left, Plan center (hero), compact Timer right
3. Mobile: Plan stacks first, Timer second, Matrix third
4. Compact timer: state label, countdown, horizontal progress bar, button, session count — no ring
5. Start/stop a pomodoro from compact widget — works identically
6. Navigate to `/pomodoro` — full page timer unchanged (360px ring)
