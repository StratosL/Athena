import * as React from "react"
import { cn } from "@/lib/utils"
import type { ChatMessage } from "@/stores/chatStore"
import { renderMarkdown } from "./renderMarkdown"
import { StatusIndicator } from "./StatusIndicator"

const HINTS = [
  "What's in my vault?",
  "Plan my day",
  "Search for API notes",
]

interface MessageListProps {
  messages: ChatMessage[]
  status: string
  onHintClick: (hint: string) => void
}

export function MessageList({ messages, status, onHintClick }: MessageListProps) {
  const messagesEndRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, status])

  return (
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
                onClick={() => onHintClick(hint)}
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
  )
}
