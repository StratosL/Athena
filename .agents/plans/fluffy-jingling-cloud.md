# Plan: Dedicated Athena Chat Page (`/athena`)

## Context

Athena's chat currently lives in a 420px right-side drawer (ChatSidebar), triggered by a floating action button. For deeper conversations — task extraction, research, daily planning — a full-page experience is needed. We'll add a dedicated `/athena` route with a 2-panel layout (conversation history + chat), while keeping the FAB + sidebar for quick access from other pages. Both share the same Zustand store.

## Approach

### Step 1: Extract shared components from ChatSidebar

Create `frontend/src/design-system/components/features/ChatSidebar/shared/` with 6 files extracted from the current 653-line `ChatSidebar/index.tsx`:

| File | Extracted From | What It Does |
|------|---------------|--------------|
| `renderMarkdown.ts` | Lines 38-43 | Pure function: `marked` + DOMPurify |
| `StatusIndicator.tsx` | Lines 45-122 | Stateless component, takes `status: string` |
| `VoiceSettingsDialog.tsx` | Lines 124-215 + VOICES constant | Radix Dialog for voice/auto-speak settings |
| `ConversationList.tsx` | Lines 217-299 | History list. Add `showCloseButton?: boolean` prop (default true) |
| `MessageList.tsx` | Lines 496-563 | Messages, welcome screen, auto-scroll, hints. Props: `messages`, `status`, `onHintClick` |
| `ChatInput.tsx` | Lines 566-643 | Text input + send / voice mic button. Props: `voiceMode`, `isRecording`, `status`, `onSend`, `onMicClick` |
| `index.ts` | — | Barrel export |

Then **refactor** `ChatSidebar/index.tsx` to import from `./shared`. The component shrinks to ~150 lines (just the drawer layout + header). Public API unchanged.

**Verify**: Sidebar still works identically on all pages after refactor.

### Step 2: Add Athena nav entry

**`frontend/src/pages-new/layout/navItems.ts`** — Add as the 6th item in `navItems`:
```ts
{ label: "Athena", href: "/athena", icon: createElement(Sparkles, { className: "w-5 h-5" }) }
```

6th item means `BottomNav.slice(0, 5)` naturally excludes it from mobile — no BottomNav changes needed.

### Step 3: Create the Athena page

New files:
```
frontend/src/pages-new/Athena/
  index.tsx                    ← main page
  components/
    index.ts                   ← barrel
    ChatHeader.tsx             ← header bar (avatar, status, voice toggle, new chat, settings)
    ConversationPanel.tsx      ← left panel wrapper around ConversationList
```

**Layout** (desktop):
```
┌───────────────┬──────────────────────────────────┐
│ Conversations │  ChatHeader (avatar, toggles)    │
│ [+ New]       ├──────────────────────────────────┤
│ • Conv 1      │  MessageList (messages/welcome)  │
│ • Conv 2      │                                  │
│ • Conv 3      │                                  │
│               ├──────────────────────────────────┤
│               │  ChatInput (text or voice)       │
└───────────────┴──────────────────────────────────┘
```

- Left panel: `w-72`, `hidden lg:flex` (desktop only), glassmorphism card
- Right panel: `flex-1`, glassmorphism card, 3 rows (header, messages, input)
- Height: `h-[calc(100vh-140px)]` to fill viewport minus AppShell PageHeader + padding
- Mobile: only the chat area shows (left panel hidden)

Reuses: `useChatStore`, `useAthenaChat`, `useAthenaVoice` hooks + all shared components from Step 1.

### Step 4: Add route

**`frontend/src/App.tsx`** — Add:
```tsx
import { Athena } from "@/pages-new/Athena"
<Route path="/athena" element={<Athena />} />
```

### Step 5: Hide FAB + sidebar on `/athena`

**`frontend/src/pages-new/layout/AppShell.tsx`**:
- Add `const isAthenaPage = location.pathname === "/athena"`
- Wrap ChatSidebar + FAB in `{!isAthenaPage && (...)}`
- Remove `lg:pr-[420px]` padding when on `/athena`

## Files Changed

| File | Type | Lines |
|------|------|-------|
| `ChatSidebar/shared/renderMarkdown.ts` | NEW | ~10 |
| `ChatSidebar/shared/StatusIndicator.tsx` | NEW | ~80 |
| `ChatSidebar/shared/VoiceSettingsDialog.tsx` | NEW | ~95 |
| `ChatSidebar/shared/ConversationList.tsx` | NEW | ~90 |
| `ChatSidebar/shared/MessageList.tsx` | NEW | ~80 |
| `ChatSidebar/shared/ChatInput.tsx` | NEW | ~80 |
| `ChatSidebar/shared/index.ts` | NEW | ~7 |
| `ChatSidebar/index.tsx` | MODIFY | 653→~150 (refactor to use shared) |
| `pages-new/Athena/index.tsx` | NEW | ~80 |
| `pages-new/Athena/components/ChatHeader.tsx` | NEW | ~60 |
| `pages-new/Athena/components/ConversationPanel.tsx` | NEW | ~20 |
| `pages-new/Athena/components/index.ts` | NEW | ~3 |
| `pages-new/layout/navItems.ts` | MODIFY | +2 lines |
| `App.tsx` | MODIFY | +2 lines |
| `pages-new/layout/AppShell.tsx` | MODIFY | +5 lines |

## Implementation Order

1. Extract shared components (Step 1) → verify sidebar works
2. Refactor ChatSidebar to use shared imports → verify sidebar works
3. Add nav entry (Step 2) → verify sidebar shows Athena
4. Create Athena page + components (Step 3)
5. Add route (Step 4) + hide FAB (Step 5)
6. Full verification pass

## Verification

1. **Sidebar regression**: On Dashboard, click FAB → sidebar opens → send message → toggle voice → open history → switch conversation → close. All works as before.
2. **Nav**: Athena appears in desktop sidebar with Sparkles icon. NOT in mobile BottomNav.
3. **Page layout**: `/athena` shows 2-panel desktop, single-panel mobile.
4. **FAB hidden**: No FAB or sidebar drawer on `/athena`.
5. **Shared state**: Send message on `/athena` → navigate to Dashboard → open sidebar → same conversation visible.
6. **Voice**: Toggle voice mode on `/athena` → mic button appears → record → response plays.
7. **TypeScript**: `npx tsc --noEmit` — 0 errors.
