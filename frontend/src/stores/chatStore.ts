/**
 * Zustand store for Athena chat sidebar state.
 */

import { create } from "zustand"

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

interface ChatStore {
  // State
  isOpen: boolean
  messages: ChatMessage[]
  conversationId: string | null
  status: ChatStatus
  voiceMode: boolean

  // Actions
  toggle: () => void
  setOpen: (open: boolean) => void
  addMessage: (role: ChatMessage["role"], text: string) => void
  clearMessages: () => void
  setStatus: (status: ChatStatus) => void
  setConversationId: (id: string | null) => void
  setVoiceMode: (voice: boolean) => void
}

let messageCounter = 0

export const useChatStore = create<ChatStore>((set) => ({
  isOpen: false,
  messages: [],
  conversationId: null,
  status: "idle",
  voiceMode: false,

  toggle: () => set((s) => ({ isOpen: !s.isOpen })),
  setOpen: (open) => set({ isOpen: open }),

  addMessage: (role, text) =>
    set((s) => ({
      messages: [
        ...s.messages,
        { id: String(++messageCounter), role, text, timestamp: Date.now() },
      ],
    })),

  clearMessages: () => set({ messages: [], conversationId: null }),
  setStatus: (status) => set({ status }),
  setConversationId: (id) => set({ conversationId: id }),
  setVoiceMode: (voice) => set({ voiceMode: voice }),
}))
