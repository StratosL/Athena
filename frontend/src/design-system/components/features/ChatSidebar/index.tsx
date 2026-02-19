/**
 * ChatSidebar Component
 *
 * Right-side drawer for Athena chat with text and voice modes,
 * settings dialog, and keyboard shortcuts.
 */

import * as React from "react"
import { motion, AnimatePresence } from "motion/react"
import { X, Mic, MessageSquare, Plus, Clock } from "lucide-react"
import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"
import { useChatStore } from "@/stores/chatStore"
import { useAthenaChat } from "@/hooks/useAthenaChat"
import { useAthenaVoice } from "@/hooks/useAthenaVoice"
import type { ChatSidebarProps } from "./ChatSidebar.types"
import {
  ConversationList,
  MessageList,
  ChatInput,
  VoiceSettingsDialog,
} from "./shared"

export function ChatSidebar({ open, onClose }: ChatSidebarProps) {
  const messages = useChatStore((s) => s.messages)
  const status = useChatStore((s) => s.status)
  const voiceMode = useChatStore((s) => s.voiceMode)
  const setVoiceMode = useChatStore((s) => s.setVoiceMode)
  const newConversation = useChatStore((s) => s.newConversation)
  const { sendMessage } = useAthenaChat()
  const { isRecording, handleMicClick, handleCancel } = useAthenaVoice()

  const [showHistory, setShowHistory] = React.useState(false)

  // Keyboard shortcuts
  React.useEffect(() => {
    if (!open) return

    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (status === "recording" || status === "speaking") {
          handleCancel()
        } else {
          onClose()
        }
        return
      }

      if (
        e.code === "Space" &&
        voiceMode &&
        document.activeElement?.tagName !== "INPUT" &&
        document.activeElement?.tagName !== "TEXTAREA"
      ) {
        e.preventDefault()
        handleMicClick()
      }
    }

    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [open, voiceMode, status, handleMicClick, handleCancel, onClose])

  const statusLabel =
    status === "recording"
      ? "Recording..."
      : status === "transcribing"
        ? "Transcribing..."
        : status === "thinking"
          ? "Thinking..."
          : status === "speaking"
            ? "Speaking..."
            : "Online"

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Mobile backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Sidebar panel */}
          <motion.aside
            className={cn(
              "fixed right-0 top-0 h-full z-50 flex flex-col",
              "w-full lg:w-[420px]",
              glassmorphismClasses,
              "rounded-none lg:rounded-l-xl",
              "border-l border-luxury-border bg-luxury-obsidian/95 backdrop-blur-xl"
            )}
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-luxury-border">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-luxury-indigo to-luxury-gold flex items-center justify-center text-white text-sm font-bold">
                    A
                  </div>
                  <div
                    className={cn(
                      "absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-luxury-obsidian",
                      status === "thinking" || status === "transcribing"
                        ? "bg-luxury-indigo animate-pulse"
                        : status === "recording"
                          ? "bg-red-500 animate-pulse"
                          : status === "speaking"
                            ? "bg-luxury-gold animate-pulse"
                            : "bg-emerald-500"
                    )}
                  />
                </div>
                <div>
                  <h2 className="text-luxury-text-primary font-semibold text-base">
                    Athena
                  </h2>
                  <p className="text-luxury-text-secondary text-xs">
                    {statusLabel}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={() => setVoiceMode(!voiceMode)}
                  className={cn(
                    "p-2 rounded-lg transition-colors",
                    voiceMode
                      ? "bg-luxury-indigo/20 text-luxury-indigo"
                      : "text-luxury-text-secondary hover:text-luxury-text-primary hover:bg-luxury-card"
                  )}
                  aria-label={voiceMode ? "Switch to text mode" : "Switch to voice mode"}
                >
                  {voiceMode ? <MessageSquare size={16} /> : <Mic size={16} />}
                </button>

                <button
                  onClick={() => setShowHistory((v) => !v)}
                  className={cn(
                    "p-2 rounded-lg transition-colors",
                    showHistory
                      ? "bg-luxury-indigo/20 text-luxury-indigo"
                      : "text-luxury-text-secondary hover:text-luxury-text-primary hover:bg-luxury-card"
                  )}
                  aria-label="Conversation history"
                >
                  <Clock size={16} />
                </button>

                <button
                  onClick={() => { newConversation(); setShowHistory(false) }}
                  className="p-2 rounded-lg hover:bg-luxury-card text-luxury-text-secondary hover:text-luxury-text-primary transition-colors"
                  aria-label="New conversation"
                >
                  <Plus size={16} />
                </button>

                <VoiceSettingsDialog />

                <button
                  onClick={onClose}
                  className="p-2 rounded-lg hover:bg-luxury-card text-luxury-text-secondary hover:text-luxury-text-primary transition-colors"
                  aria-label="Close chat"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Messages area / History panel */}
            {showHistory ? (
              <div className="flex-1 overflow-y-auto px-5 py-4">
                <ConversationList onSelect={() => setShowHistory(false)} />
              </div>
            ) : (
              <MessageList
                messages={messages}
                status={status}
                onHintClick={(hint) => sendMessage(hint)}
              />
            )}

            {/* Input area */}
            {!showHistory && (
              <ChatInput
                voiceMode={voiceMode}
                isRecording={isRecording}
                status={status}
                onSend={(text) => sendMessage(text)}
                onMicClick={handleMicClick}
                autoFocus={open}
              />
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}

export default ChatSidebar
export type { ChatSidebarProps } from "./ChatSidebar.types"
