import * as React from "react"
import { X, Settings } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"

const VOICES = [
  { id: "nova", label: "Nova" },
  { id: "alloy", label: "Alloy" },
  { id: "echo", label: "Echo" },
  { id: "fable", label: "Fable" },
  { id: "onyx", label: "Onyx" },
  { id: "shimmer", label: "Shimmer" },
]

export function VoiceSettingsDialog() {
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
