import * as React from "react"
import { useChatStore } from "@/stores/chatStore"
import { useAthenaChat } from "@/hooks/useAthenaChat"
import { useAthenaVoice } from "@/hooks/useAthenaVoice"
import { MessageList, ChatInput } from "@/design-system/components/features/ChatSidebar/shared"
import { AppShell } from "../layout"
import { ChatHeader, ConversationPanel } from "./components"

export function Athena() {
  const messages = useChatStore((s) => s.messages)
  const status = useChatStore((s) => s.status)
  const voiceMode = useChatStore((s) => s.voiceMode)
  const { sendMessage } = useAthenaChat()
  const { isRecording, handleMicClick, handleCancel } = useAthenaVoice()

  // Keyboard shortcuts (voice mode space-to-record, escape to cancel)
  React.useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (status === "recording" || status === "speaking") {
          handleCancel()
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
  }, [voiceMode, status, handleMicClick, handleCancel])

  return (
    <AppShell title="Athena" subtitle="Your second brain assistant">
      <div className="flex gap-4 h-[calc(100vh-140px)]">
        {/* Left: Conversation History (desktop only) */}
        <ConversationPanel />

        {/* Right: Chat Area */}
        <div className="flex-1 flex flex-col backdrop-blur-md bg-luxury-card/50 border border-luxury-border rounded-xl overflow-hidden">
          <ChatHeader />
          <MessageList
            messages={messages}
            status={status}
            onHintClick={(hint) => sendMessage(hint)}
          />
          <ChatInput
            voiceMode={voiceMode}
            isRecording={isRecording}
            status={status}
            onSend={(text) => sendMessage(text)}
            onMicClick={handleMicClick}
            autoFocus
          />
        </div>
      </div>
    </AppShell>
  )
}
