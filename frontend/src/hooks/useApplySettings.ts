import { useEffect } from "react"

const STORAGE_KEY = "artemis-settings"

/**
 * Reads appearance settings from localStorage and applies them
 * as data attributes on <html> so CSS variables respond.
 */
export function useApplySettings() {
  useEffect(() => {
    const apply = () => {
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (!raw) return

        const settings = JSON.parse(raw)
        const root = document.documentElement

        // Theme
        if (settings.theme) {
          root.setAttribute("data-theme", settings.theme)
        }

        // Accent color
        if (settings.accentColor) {
          root.setAttribute("data-accent", settings.accentColor)
        }

        // Font size
        if (settings.fontSize) {
          root.setAttribute("data-font-size", settings.fontSize)
        }
      } catch {
        // Ignore parse errors
      }
    }

    // Apply immediately on mount
    apply()

    // Re-apply when other tabs/components update localStorage
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY) apply()
    }
    window.addEventListener("storage", onStorage)

    // Also listen for same-tab updates via a custom event
    const onSettingsChange = () => apply()
    window.addEventListener("artemis-settings-change", onSettingsChange)

    return () => {
      window.removeEventListener("storage", onStorage)
      window.removeEventListener("artemis-settings-change", onSettingsChange)
    }
  }, [])
}
