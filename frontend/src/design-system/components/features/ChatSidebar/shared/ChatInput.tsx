import * as React from "react"
import { motion } from "motion/react"
import { Send, Mic } from "lucide-react"
import { cn } from "@/lib/utils"

interface ChatInputProps {
  voiceMode: boolean
  isRecording: boolean
  status: string
  onSend: (text: string) => void
  onMicClick: () => void
  autoFocus?: boolean
}

export function ChatInput({ voiceMode, isRecording, status, onSend, onMicClick, autoFocus }: ChatInputProps) {
  const [input, setInput] = React.useState("")
  const inputRef = React.useRef<HTMLInputElement>(null)

  React.useEffect(() => {
    if (autoFocus && !voiceMode) {
      setTimeout(() => inputRef.current?.focus(), 300)
    }
  }, [autoFocus, voiceMode])

  const handleSend = () => {
    const text = input.trim()
    if (!text || status === "thinking") return
    setInput("")
    onSend(text)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (voiceMode) {
    return (
      <div className="px-5 py-4 border-t border-luxury-border">
        <div className="flex flex-col items-center gap-2">
          <motion.button
            onClick={onMicClick}
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
      </div>
    )
  }

  return (
    <div className="px-5 py-4 border-t border-luxury-border">
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
    </div>
  )
}
