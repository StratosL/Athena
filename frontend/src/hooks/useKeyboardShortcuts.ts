/**
 * Keyboard shortcuts hook for global app shortcuts.
 */

import { useEffect, useCallback } from "react"

interface ShortcutConfig {
  key: string
  ctrlKey?: boolean
  shiftKey?: boolean
  callback: () => void
  description: string
}

export function useKeyboardShortcuts(shortcuts: ShortcutConfig[]) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs
      const target = event.target as HTMLElement
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      ) {
        return
      }

      for (const shortcut of shortcuts) {
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase()
        const ctrlMatch = shortcut.ctrlKey ? event.ctrlKey || event.metaKey : !event.ctrlKey && !event.metaKey
        const shiftMatch = shortcut.shiftKey ? event.shiftKey : !event.shiftKey

        if (keyMatch && ctrlMatch && shiftMatch) {
          event.preventDefault()
          shortcut.callback()
          return
        }
      }
    },
    [shortcuts]
  )

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [handleKeyDown])
}

/**
 * Hook specifically for Pomodoro page shortcuts.
 */
export function usePomodoroShortcuts({
  onToggleTimer,
  onStopTimer,
}: {
  onToggleTimer: () => void
  onStopTimer: () => void
}) {
  const shortcuts: ShortcutConfig[] = [
    {
      key: " ", // Space
      callback: onToggleTimer,
      description: "Start/Pause Pomodoro",
    },
    {
      key: "Escape",
      callback: onStopTimer,
      description: "Stop Pomodoro",
    },
  ]

  useKeyboardShortcuts(shortcuts)
}
