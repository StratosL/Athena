import { useState, useEffect } from "react"
import type { Settings } from "../types"

const STORAGE_KEY = "artemis-settings"

const DEFAULT_SETTINGS: Settings = {
  // General
  userName: "User",
  workHoursStart: "09:00",
  workHoursEnd: "17:00",
  dailyTaskLimit: 9,

  // Appearance
  theme: "dark",
  accentColor: "indigo",
  fontSize: "medium",

  // Pomodoro
  pomodoroWorkDuration: 25,
  pomodoroShortBreakDuration: 5,
  pomodoroLongBreakDuration: 15,
  pomodoroSessionsBeforeLongBreak: 4,

  // Notifications
  notificationsEnabled: true,
  soundEnabled: true,
  desktopNotifications: false,
  breakReminders: true,

  // Data & Privacy
  analyticsEnabled: true,
  dataRetentionDays: 90,
}

export function useSettings() {
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS)
  const [isLoading, setIsLoading] = useState(true)

  // Load settings from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        setSettings(parsed)
      }
    } catch (error) {
      console.error("Failed to load settings:", error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Update a single setting
  const updateSetting = <K extends keyof Settings>(
    key: K,
    value: Settings[K]
  ) => {
    setSettings((prev) => {
      const updated = { ...prev, [key]: value }
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
        // Notify useApplySettings in the same tab
        window.dispatchEvent(new Event("artemis-settings-change"))
      } catch (error) {
        console.error("Failed to save settings:", error)
      }
      return updated
    })
  }

  // Reset to defaults
  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS)
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_SETTINGS))
      window.dispatchEvent(new Event("artemis-settings-change"))
    } catch (error) {
      console.error("Failed to reset settings:", error)
    }
  }

  // Export settings as JSON
  const exportSettings = () => {
    const dataStr = JSON.stringify(settings, null, 2)
    const dataBlob = new Blob([dataStr], { type: "application/json" })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement("a")
    link.href = url
    link.download = "artemis-settings.json"
    link.click()
    URL.revokeObjectURL(url)
  }

  return {
    settings,
    isLoading,
    updateSetting,
    resetSettings,
    exportSettings,
  }
}
