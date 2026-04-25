# Dashboard Redesign: Pomodoro → Stats Bar, 2-Column Layout

## Context

The dashboard currently uses a 3-column grid (Plan, Timer, Matrix) where the Pomodoro timer gets its own column. The timer is low-information-density (one number + one button) for the space it occupies. The goal is to promote Plan and Matrix to equal-width hero panels, and demote the timer into the stats bar at the bottom — merging it with the daily stats into a single combined card.

## Target Layout

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   Today's Plan      │   Eisenhower Matrix │
│   (1-3-5 slots)     │   (2×2 quadrants)   │
│                     │                     │
└─────────────────────┴─────────────────────┘
┌───────────────────────────────────────────┐
│  Focus  25:00  ████████░░░░░░  [Stop]     │
│───────────────────────────────────────────│
│  2 pom  │  1.2h  │  5 done  │  72%       │
└───────────────────────────────────────────┘
```

Mobile: Plan → Matrix → Timer+Stats (single column stack).

## Changes (4 files modified, 1 file deleted)

### 1. Rewrite `DashboardStatsBar.tsx` — merge timer + stats

**File:** `frontend/src/pages-new/Dashboard/components/DashboardStatsBar.tsx`

- Remove `DailyStatsBar` design-system import (we inline the stats grid directly)
- Add all pomodoro imports: `useTimerStore`, `useActiveTimer`, `useStartSession`, `useStopSession`, `useCompleteSession`, `usePomodoroWebSocket`
- Add `GlassCard`, `Button` from `@/design-system/components`
- Copy `getPomodoroSettings()`, `formatTime()`, `stateLabels` helpers from `PomodoroWidget/index.tsx`
- Copy `StatItem` local component from `DailyStatsBar/index.tsx`
- Hook setup: same as PomodoroWidget compact (timer store, sessions, WebSocket, active timer polling, sync effect, auto-complete effect, handleStart/handleStop)
- Rename analytics `isLoading` → `isStatsLoading` to avoid collision with timer `isLoading`
- Render a single `<GlassCard>`:
  - Top: flex row with state label, countdown, progress bar, start/stop button
  - Thin `border-t` divider
  - Bottom: 4-column stats grid (same as current DailyStatsBar)

### 2. Simplify `Dashboard/index.tsx` — 2-column grid

**File:** `frontend/src/pages-new/Dashboard/index.tsx`

- Remove `DashboardTimerColumn` from import
- Change grid: `lg:grid-cols-3` → `lg:grid-cols-2`
- Remove the `<DashboardTimerColumn />` div entirely
- Remove all `lg:order-*` classes (DOM order = visual order: Plan left, Matrix right)

### 3. Delete `DashboardTimerColumn.tsx`

**File:** `frontend/src/pages-new/Dashboard/components/DashboardTimerColumn.tsx`

Delete — no longer used.

### 4. Update barrel export

**File:** `frontend/src/pages-new/Dashboard/components/index.ts`

Remove `DashboardTimerColumn` export line.

## Files NOT Modified

- `PomodoroWidget/index.tsx` — `/pomodoro` page still uses it
- `DailyStatsBar/index.tsx` — stays in design system for reuse
- `timerStore.ts`, all hooks — shared, unchanged

## Verification

1. `cd frontend && npx tsc --noEmit` — 0 errors
2. Dashboard shows 2 equal columns (Plan left, Matrix right)
3. Bottom bar: timer row on top (label, time, progress, button), divider, stats grid below
4. Timer starts/stops, WebSocket ticks, progress bar fills, auto-complete works
5. `/pomodoro` page still works independently
6. `grep -r "DashboardTimerColumn" frontend/src/` returns 0 results
