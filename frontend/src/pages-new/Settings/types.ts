export interface Settings {
  // General
  userName: string
  workHoursStart: string
  workHoursEnd: string
  dailyTaskLimit: number

  // Appearance
  theme: "dark" | "light"
  accentColor: "indigo" | "cyan" | "orange" | "gold"
  fontSize: "small" | "medium" | "large"

  // Pomodoro
  pomodoroWorkDuration: number
  pomodoroShortBreakDuration: number
  pomodoroLongBreakDuration: number
  pomodoroSessionsBeforeLongBreak: number

  // Notifications
  notificationsEnabled: boolean
  soundEnabled: boolean
  desktopNotifications: boolean
  breakReminders: boolean

  // Data & Privacy
  analyticsEnabled: boolean
  dataRetentionDays: number
}

export interface SettingsCategory {
  id: string
  label: string
  icon: string
  description: string
}

export interface SettingItem {
  key: keyof Settings
  label: string
  description?: string
  type: "text" | "number" | "time" | "toggle" | "slider" | "select"
  min?: number
  max?: number
  step?: number
  options?: Array<{ value: string; label: string }>
}
