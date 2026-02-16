/**
 * ChatSidebar Component
 *
 * Right-side drawer for Athena chat with text and voice modes,
 * settings dialog, and keyboard shortcuts.
 */

import * as React from "react"
import { motion, AnimatePresence } from "motion/react"
import { X, Send, Mic, MessageSquare, Settings } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { marked } from "marked"
import DOMPurify from "dompurify"
import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"
import { useChatStore } from "@/stores/chatStore"
import { useAthenaChat } from "@/hooks/useAthenaChat"
import { useAthenaVoice } from "@/hooks/useAthenaVoice"
import type { ChatSidebarProps } from "./ChatSidebar.types"

marked.setOptions({ breaks: true })

const HINTS = [
  "What's in my vault?",
  "Plan my day",
  "Search for API notes",
]

const VOICES = [
  { id: "nova", label: "Nova" },
  { id: "alloy", label: "Alloy" },
  { id: "echo", label: "Echo" },
  { id: "fable", label: "Fable" },
  { id: "onyx", label: "Onyx" },
  { id: "shimmer", label: "Shimmer" },
]

function renderMarkdown(text: string): string {
  if (typeof text !== "string") return String(text ?? "")
  const raw = marked.parse(text)
  if (typeof raw !== "string") return text
  return DOMPurify.sanitize(raw)
}

function StatusIndicator({ status }: { status: string }) {
  if (status === "recording") {
    return (
      <div className="flex justify-start">
        <div className="backdrop-blur-md bg-luxury-card border border-luxury-border rounded-2xl px-4 py-3 flex items-center gap-2">
          <motion.div
            className="w-2.5 h-2.5 rounded-full bg-red-500"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
          <span className="text-luxury-text-secondary text-xs">Recording...</span>
        </div>
      </div>
    )
  }

  if (status === "transcribing") {
    return (
      <div className="flex justify-start">
        <div className="backdrop-blur-md bg-luxury-card border border-luxury-border rounded-2xl px-4 py-3 flex items-center gap-2">
          <motion.div
            className="w-2.5 h-2.5 rounded-full bg-luxury-indigo"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
          <span className="text-luxury-text-secondary text-xs">Transcribing...</span>
        </div>
      </div>
    )
  }

  if (status === "thinking") {
    return (
      <div className="flex justify-start">
        <div className="backdrop-blur-md bg-luxury-card border border-luxury-border rounded-2xl px-4 py-3 flex items-center gap-2">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="w-2 h-2 rounded-full bg-luxury-indigo"
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
              />
            ))}
          </div>
          <span className="text-luxury-text-secondary text-xs">Athena is thinking...</span>
        </div>
      </div>
    )
  }

  if (status === "speaking") {
    return (
      <div className="flex justify-start">
        <div className="backdrop-blur-md bg-luxury-card border border-luxury-border rounded-2xl px-4 py-3 flex items-center gap-2">
          <div className="flex items-end gap-0.5 h-4">
            {[0, 1, 2, 3].map((i) => (
              <motion.div
                key={i}
                className="w-1 bg-luxury-indigo rounded-full"
                animate={{ scaleY: [0.3, 1, 0.3] }}
                transition={{
                  duration: 0.8,
                  repeat: Infinity,
                  delay: i * 0.15,
                }}
                style={{ height: 16, originY: 1 }}
              />
            ))}
          </div>
          <span className="text-luxury-text-secondary text-xs">Speaking...</span>
        </div>
      </div>
    )
  }

  return null
}

function SettingsDialog() {
  const [voice, setVoice] = React.useState(() => {
    try { return localStorage.getItem("athena-voice") || "nova" } catch { return "nova" }
  })
  const [autoSpeak, setAutoSpeak] = React.useState(() => {
    try {
      const v = localStorage.getItem("athena-auto-speak")
      return v === null ? true : v === "true"
    } catch { return true }
  })

  const handleVoiceChange = (v: string) => {
    setVoice(v)
    localStorage.setItem("athena-voice", v)
  }

  const handleAutoSpeakChange = () => {
    const next = !autoSpeak
    setAutoSpeak(next)
    localStorage.setItem("athena-auto-speak", String(next))
  }

  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <button
          className="p-2 rounded-lg hover:bg-luxury-card text-luxury-text-secondary hover:text-luxury-text-primary transition-colors"
          aria-label="Settings"
        >
          <Settings size={16} />
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60]" />
        <Dialog.Content
          className={cn(
            "fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-[61]",
            "w-[340px] p-6 rounded-xl",
            glassmorphismClasses,
            "bg-luxury-obsidian/95 backdrop-blur-xl border border-luxury-border"
          )}
        >
          <Dialog.Title className="text-luxury-text-primary font-semibold text-base mb-4">
            Voice Settings
          </Dialog.Title>

          {/* Voice selection */}
          <div className="mb-4">
            <label className="text-luxury-text-secondary text-xs mb-2 block">Voice</label>
            <select
              value={voice}
              onChange={(e) => handleVoiceChange(e.target.value)}
              className="w-full bg-luxury-card border border-luxury-border rounded-lg px-3 py-2 text-sm text-luxury-text-primary focus:outline-none focus:border-luxury-indigo/50"
            >
              {VOICES.map((v) => (
                <option key={v.id} value={v.id}>{v.label}</option>
              ))}
            </select>
          </div>

          {/* Auto-speak toggle */}
          <div className="flex items-center justify-between">
            <label className="text-luxury-text-secondary text-sm">Auto-speak responses</label>
            <button
              onClick={handleAutoSpeakChange}
              className={cn(
                "w-10 h-6 rounded-full transition-colors relative",
                autoSpeak ? "bg-luxury-indigo" : "bg-luxury-card border border-luxury-border"
              )}
            >
              <div
                className={cn(
                  "w-4 h-4 rounded-full bg-white absolute top-1 transition-transform",
                  autoSpeak ? "translate-x-5" : "translate-x-1"
                )}
              />
            </button>
          </div>

          <Dialog.Close asChild>
            <button
              className="absolute top-4 right-4 p-1 rounded-md text-luxury-text-secondary hover:text-luxury-text-primary transition-colors"
              aria-label="Close settings"
            >
              <X size={14} />
            </button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

export function ChatSidebar({ open, onClose }: ChatSidebarProps) {
  const messages = useChatStore((s) => s.messages)
  const status = useChatStore((s) => s.status)
  const voiceMode = useChatStore((s) => s.voiceMode)
  const setVoiceMode = useChatStore((s) => s.setVoiceMode)
  const { sendMessage } = useAthenaChat()
  const { isRecording, handleMicClick, handleCancel } = useAthenaVoice()

  const [input, setInput] = React.useState("")
  const messagesEndRef = React.useRef<HTMLDivElement>(null)
  const inputRef = React.useRef<HTMLInputElement>(null)

  // Auto-scroll on new messages
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, status])

  // Focus input when opened (text mode)
  React.useEffect(() => {
    if (open && !voiceMode) {
      setTimeout(() => inputRef.current?.focus(), 300)
    }
  }, [open, voiceMode])

  // Keyboard shortcuts
  React.useEffect(() => {
    if (!open) return

    const handler = (e: KeyboardEvent) => {
      // Escape: cancel recording / stop speaking / close sidebar
      if (e.key === "Escape") {
        if (status === "recording" || status === "speaking") {
          handleCancel()
        } else {
          onClose()
        }
        return
      }

      // Space in voice mode (when input not focused): toggle recording
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

  const handleSend = async () => {
    const text = input.trim()
    if (!text || status === "thinking") return
    setInput("")
    await sendMessage(text)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleHint = (hint: string) => {
    sendMessage(hint)
  }

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
                {/* Mode toggle */}
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

                <SettingsDialog />

                <button
                  onClick={onClose}
                  className="p-2 rounded-lg hover:bg-luxury-card text-luxury-text-secondary hover:text-luxury-text-primary transition-colors"
                  aria-label="Close chat"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Messages area */}
            <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
              {messages.length === 0 && status === "idle" ? (
                /* Welcome screen */
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-luxury-indigo to-luxury-gold flex items-center justify-center mb-4">
                    <span className="text-2xl font-bold text-white">A</span>
                  </div>
                  <h3 className="text-luxury-text-primary text-lg font-semibold mb-1">
                    Hey there!
                  </h3>
                  <p className="text-luxury-text-secondary text-sm mb-6 max-w-[280px]">
                    I'm Athena, your second brain assistant. Ask me anything about your vault, tasks, or plans.
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {HINTS.map((hint) => (
                      <button
                        key={hint}
                        onClick={() => handleHint(hint)}
                        className={cn(
                          "px-3 py-1.5 rounded-full text-xs",
                          "border border-luxury-border text-luxury-text-secondary",
                          "hover:border-luxury-indigo hover:text-luxury-indigo transition-colors"
                        )}
                      >
                        {hint}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={cn(
                        "flex",
                        msg.role === "user" ? "justify-end" : "justify-start"
                      )}
                    >
                      <div
                        className={cn(
                          "max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                          msg.role === "user"
                            ? "bg-luxury-indigo/20 text-luxury-text-primary border border-luxury-indigo/30"
                            : "backdrop-blur-md bg-luxury-card border border-luxury-border text-luxury-text-primary"
                        )}
                      >
                        {msg.role === "agent" ? (
                          <div
                            className="prose prose-invert prose-sm max-w-none [&_p]:mb-2 [&_p:last-child]:mb-0 [&_code]:bg-white/10 [&_code]:px-1 [&_code]:rounded [&_pre]:bg-white/5 [&_pre]:p-3 [&_pre]:rounded-lg [&_ul]:list-disc [&_ul]:pl-4 [&_ol]:list-decimal [&_ol]:pl-4"
                            dangerouslySetInnerHTML={{
                              __html: renderMarkdown(msg.text),
                            }}
                          />
                        ) : (
                          msg.text
                        )}
                      </div>
                    </div>
                  ))}

                  <StatusIndicator status={status} />
                </>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input area */}
            <div className="px-5 py-4 border-t border-luxury-border">
              {voiceMode ? (
                /* Voice mode: mic button */
                <div className="flex flex-col items-center gap-2">
                  <motion.button
                    onClick={handleMicClick}
                    disabled={status === "transcribing" || status === "thinking"}
                    className={cn(
                      "w-16 h-16 rounded-full flex items-center justify-center relative",
                      "disabled:opacity-40 transition-colors",
                      isRecording
                        ? "bg-red-500"
                        : status === "speaking"
                          ? "bg-luxury-gold"
                          : "bg-gradient-to-r from-luxury-indigo to-luxury-gold"
                    )}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    aria-label={
                      isRecording
                        ? "Stop recording"
                        : status === "speaking"
                          ? "Stop speaking"
                          : "Start recording"
                    }
                  >
                    {/* Animated ring when recording */}
                    {isRecording && (
                      <motion.div
                        className="absolute inset-0 rounded-full border-2 border-red-400"
                        animate={{ scale: [1, 1.3, 1], opacity: [0.6, 0, 0.6] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      />
                    )}
                    <Mic size={24} className="text-white" />
                  </motion.button>
                  <p className="text-luxury-text-secondary text-xs">
                    {isRecording
                      ? "Tap to stop"
                      : status === "speaking"
                        ? "Tap to stop"
                        : "Tap to speak"}
                  </p>
                </div>
              ) : (
                /* Text mode: input + send */
                <div className="flex items-center gap-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask Athena..."
                    disabled={status === "thinking"}
                    className={cn(
                      "flex-1 bg-luxury-card border border-luxury-border rounded-xl px-4 py-2.5 text-sm",
                      "text-luxury-text-primary placeholder:text-luxury-text-secondary/50",
                      "focus:outline-none focus:border-luxury-indigo/50",
                      "disabled:opacity-50 transition-colors"
                    )}
                  />
                  <motion.button
                    onClick={handleSend}
                    disabled={!input.trim() || status === "thinking"}
                    className={cn(
                      "p-2.5 rounded-xl transition-colors",
                      "bg-gradient-to-r from-luxury-indigo to-luxury-gold",
                      "text-white disabled:opacity-40"
                    )}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    aria-label="Send message"
                  >
                    <Send size={16} />
                  </motion.button>
                </div>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}

export default ChatSidebar
export type { ChatSidebarProps } from "./ChatSidebar.types"
