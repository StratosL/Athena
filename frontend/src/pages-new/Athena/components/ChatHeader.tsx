import { Mic, MessageSquare, Plus } from "lucide-react"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"
import { VoiceSettingsDialog } from "@/design-system/components/features/ChatSidebar/shared"

export function ChatHeader() {
  const status = useChatStore((s) => s.status)
  const voiceMode = useChatStore((s) => s.voiceMode)
  const setVoiceMode = useChatStore((s) => s.setVoiceMode)
  const newConversation = useChatStore((s) => s.newConversation)

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
          onClick={() => newConversation()}
          className="p-2 rounded-lg hover:bg-luxury-card text-luxury-text-secondary hover:text-luxury-text-primary transition-colors"
          aria-label="New conversation"
        >
          <Plus size={16} />
        </button>

        <VoiceSettingsDialog />
      </div>
    </div>
  )
}
