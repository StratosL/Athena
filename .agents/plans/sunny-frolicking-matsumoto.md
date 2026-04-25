# Plan: Persistent Chat Conversations

## Context

When the user refreshes the Artemis frontend page, all Athena chat messages and the `conversationId` are lost. There's also no way to view or switch between past conversations. The Zustand `chatStore` uses in-memory state only — no persistence. Kibana maintains server-side conversation state via `conversation_id`, but the frontend discards it on refresh.

## Approach

Add Zustand `persist` middleware to localStorage + a conversation history panel in the ChatSidebar. **2 files modified, 0 new files, 0 new dependencies.**

---

## File 1: `frontend/src/stores/chatStore.ts`

### Changes

1. **Import `persist` from `zustand/middleware`** (already bundled with zustand v4)

2. **Add `Conversation` type:**
   ```ts
   export interface Conversation {
     id: string          // Kibana conversation_id
     title: string       // first user message, truncated to 50 chars
     messages: ChatMessage[]
     updatedAt: number   // Date.now()
   }
   ```

3. **Add state + actions to ChatStore interface:**
   - `conversations: Conversation[]` — saved conversation list
   - `newConversation: () => void` — archive current, start fresh
   - `switchConversation: (id: string) => void` — load a past conversation
   - `deleteConversation: (id: string) => void` — remove from history

4. **Wrap `create` with `persist` middleware:**
   - `name: "athena-chat"` (localStorage key)
   - `partialize` — persist only `messages`, `conversationId`, `conversations` (exclude transient UI state: `isOpen`, `voiceMode`, `status`)
   - `onRehydrateStorage` — reinitialize `messageCounter` from highest existing message ID

5. **Modify `addMessage`** — after adding to `messages[]`, upsert the active conversation in `conversations[]` (sync messages + updatedAt)

6. **Modify `setConversationId`** — when receiving the first `conversationId` for a new chat, create a `Conversation` entry with the current messages and auto-title from first user message

---

## File 2: `frontend/src/design-system/components/features/ChatSidebar/index.tsx`

### Changes

1. **Add icon imports:** `Plus`, `Clock`, `Trash2` from `lucide-react`

2. **Add `ConversationList` internal component** (before the export):
   - Renders the `conversations[]` from the store as a scrollable list
   - Each item shows: truncated title + date + hover-reveal delete button
   - Active conversation highlighted with indigo border (matching user message bubble style)
   - "New conversation" button at top (dashed border, Plus icon)
   - Close button to return to messages view
   - Follows existing glassmorphism styling: `text-luxury-*`, `bg-luxury-card`, `border-luxury-border`, `rounded-lg`

3. **Add header buttons** (between mode toggle and settings):
   - History toggle (Clock icon) — toggles `showHistory` local state
   - New chat button (Plus icon) — calls `newConversation()`

4. **Conditional rendering** in the messages area:
   - `showHistory === true` → render `<ConversationList />`
   - `showHistory === false` → render existing messages area (unchanged)

---

## What stays unchanged

- `useAthenaChat.ts` — already reads `conversationId` from store and passes to API. Switching conversations in the store is sufficient.
- `ChatSidebar.types.ts` — no new props needed
- `athena-api.ts` — no changes
- `useAthenaVoice.ts` — no changes
- Voice mode — fully preserved

## What this does NOT add (YAGNI)

- No conversation renaming (auto-title from first message)
- No search/filter conversations
- No date grouping (today/yesterday)
- No server-side persistence beyond what Kibana already does
- No export/import

---

## Verification

1. `cd frontend && npx tsc --noEmit` — TypeScript compiles with 0 errors
2. `cd frontend && npx vite build` — Vite build succeeds
3. Manual test: send a message → refresh page → messages and conversationId persist
4. Manual test: send messages → click New Chat → old conversation appears in history list
5. Manual test: click a past conversation → messages load, can continue chatting with server
6. Manual test: voice mode still works after changes
