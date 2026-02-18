/**
 * Zustand store for Athena chat sidebar state.
 * Persists messages and conversations to localStorage via zustand/middleware.
 */

import { create } from "zustand"
import { persist } from "zustand/middleware"

export type ChatStatus =
  | "idle"
  | "recording"
  | "transcribing"
  | "thinking"
  | "speaking"

export interface ChatMessage {
  id: string
  role: "user" | "agent"
  text: string
  timestamp: number
}

export interface Conversation {
  id: string          // Kibana conversation_id
  title: string       // first user message, truncated to 50 chars
  messages: ChatMessage[]
  updatedAt: number   // Date.now()
}

interface ChatStore {
  // State
  isOpen: boolean
  messages: ChatMessage[]
  conversationId: string | null
  status: ChatStatus
  voiceMode: boolean
  conversations: Conversation[]

  // Actions
  toggle: () => void
  setOpen: (open: boolean) => void
  addMessage: (role: ChatMessage["role"], text: string) => void
  clearMessages: () => void
  setStatus: (status: ChatStatus) => void
  setConversationId: (id: string | null) => void
  setVoiceMode: (voice: boolean) => void
  newConversation: () => void
  switchConversation: (id: string) => void
  deleteConversation: (id: string) => void
}

let messageCounter = 0

function deriveTitle(messages: ChatMessage[]): string {
  const first = messages.find((m) => m.role === "user")
  if (!first) return "New conversation"
  return first.text.length > 50 ? first.text.slice(0, 50) + "…" : first.text
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      isOpen: false,
      messages: [],
      conversationId: null,
      status: "idle",
      voiceMode: false,
      conversations: [],

      toggle: () => set((s) => ({ isOpen: !s.isOpen })),
      setOpen: (open) => set({ isOpen: open }),

      addMessage: (role, text) =>
        set((s) => {
          const newMsg: ChatMessage = {
            id: String(++messageCounter),
            role,
            text,
            timestamp: Date.now(),
          }
          const updatedMessages = [...s.messages, newMsg]

          // Upsert active conversation in history
          let updatedConversations = s.conversations
          if (s.conversationId) {
            const idx = s.conversations.findIndex(
              (c) => c.id === s.conversationId
            )
            const entry: Conversation = {
              id: s.conversationId,
              title: deriveTitle(updatedMessages),
              messages: updatedMessages,
              updatedAt: Date.now(),
            }
            if (idx >= 0) {
              updatedConversations = [...s.conversations]
              updatedConversations[idx] = entry
            } else {
              updatedConversations = [entry, ...s.conversations]
            }
          }

          return {
            messages: updatedMessages,
            conversations: updatedConversations,
          }
        }),

      clearMessages: () => set({ messages: [], conversationId: null }),
      setStatus: (status) => set({ status }),

      setConversationId: (id) =>
        set((s) => {
          if (!id) return { conversationId: id }

          // If this is the first conversationId for a new chat, create a Conversation entry
          if (!s.conversationId && s.messages.length > 0) {
            const exists = s.conversations.some((c) => c.id === id)
            if (!exists) {
              const entry: Conversation = {
                id,
                title: deriveTitle(s.messages),
                messages: s.messages,
                updatedAt: Date.now(),
              }
              return {
                conversationId: id,
                conversations: [entry, ...s.conversations],
              }
            }
          }

          return { conversationId: id }
        }),

      setVoiceMode: (voice) => set({ voiceMode: voice }),

      newConversation: () => {
        const { conversationId, messages, conversations } = get()
        // Archive current conversation if it has messages and a server id
        let updated = conversations
        if (conversationId && messages.length > 0) {
          const idx = conversations.findIndex((c) => c.id === conversationId)
          const entry: Conversation = {
            id: conversationId,
            title: deriveTitle(messages),
            messages,
            updatedAt: Date.now(),
          }
          if (idx >= 0) {
            updated = [...conversations]
            updated[idx] = entry
          } else {
            updated = [entry, ...conversations]
          }
        }
        set({
          messages: [],
          conversationId: null,
          status: "idle",
          conversations: updated,
        })
      },

      switchConversation: (id) => {
        const { conversationId, messages, conversations } = get()
        // Archive current conversation first
        let updated = [...conversations]
        if (conversationId && messages.length > 0) {
          const idx = updated.findIndex((c) => c.id === conversationId)
          const entry: Conversation = {
            id: conversationId,
            title: deriveTitle(messages),
            messages,
            updatedAt: Date.now(),
          }
          if (idx >= 0) {
            updated[idx] = entry
          } else {
            updated = [entry, ...updated]
          }
        }
        // Load the target conversation
        const target = updated.find((c) => c.id === id)
        if (target) {
          set({
            messages: target.messages,
            conversationId: target.id,
            status: "idle",
            conversations: updated,
          })
        }
      },

      deleteConversation: (id) =>
        set((s) => ({
          conversations: s.conversations.filter((c) => c.id !== id),
        })),
    }),
    {
      name: "athena-chat",
      partialize: (state) => ({
        messages: state.messages,
        conversationId: state.conversationId,
        conversations: state.conversations,
      }),
      onRehydrateStorage: () => (state) => {
        if (!state) return
        // Reinitialize messageCounter from highest existing message ID
        let max = 0
        for (const msg of state.messages) {
          const n = Number(msg.id)
          if (n > max) max = n
        }
        for (const conv of state.conversations) {
          for (const msg of conv.messages) {
            const n = Number(msg.id)
            if (n > max) max = n
          }
        }
        messageCounter = max
      },
    }
  )
)
