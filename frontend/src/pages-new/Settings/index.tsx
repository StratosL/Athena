import { useState } from "react"
import { Input } from "@/design-system/components"
import { AppShell } from "../layout"
import {
  SettingsNav,
  SettingsSection,
  SettingRow,
  Toggle,
  Slider,
  Select,
} from "./components"
import { useSettings } from "./hooks/useSettings"

export function Settings() {
  const { settings, isLoading, updateSetting, resetSettings, exportSettings } = useSettings()
  const [activeCategory, setActiveCategory] = useState("general")

  if (isLoading) {
    return (
      <div className="min-h-screen bg-luxury-obsidian flex items-center justify-center">
        <p className="text-luxury-text-secondary">Loading settings...</p>
      </div>
    )
  }

  return (
    <AppShell
      title="Settings"
      subtitle="Customize your Artemis experience"
    >
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Navigation Sidebar */}
        <div className="lg:col-span-1">
          <SettingsNav
            activeCategory={activeCategory}
            onCategoryChange={setActiveCategory}
          />
        </div>

        {/* Content Area */}
        <div className="lg:col-span-3">
          {/* General Settings */}
          {activeCategory === "general" && (
            <SettingsSection
              title="General"
              description="Profile and work preferences"
            >
              <SettingRow>
                <Input
                  value={settings.userName}
                  onChange={(e) => updateSetting("userName", e.target.value)}
                  placeholder="Enter your name"
                />
              </SettingRow>

              <SettingRow>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    type="time"
                    value={settings.workHoursStart}
                    onChange={(e) => updateSetting("workHoursStart", e.target.value)}
                  />
                  <Input
                    type="time"
                    value={settings.workHoursEnd}
                    onChange={(e) => updateSetting("workHoursEnd", e.target.value)}
                  />
                </div>
              </SettingRow>

              <SettingRow>
                <Slider
                  value={settings.dailyTaskLimit}
                  onChange={(value) => updateSetting("dailyTaskLimit", value)}
                  min={5}
                  max={20}
                  step={1}
                  label="Daily Task Limit"
                  description="Maximum number of tasks in your daily plan"
                  unit=" tasks"
                />
              </SettingRow>
            </SettingsSection>
          )}

          {/* Appearance Settings */}
          {activeCategory === "appearance" && (
            <SettingsSection
              title="Appearance"
              description="Theme, colors, and visual preferences"
            >
              <SettingRow>
                <Select
                  value={settings.theme}
                  onChange={(value) => updateSetting("theme", value as "dark" | "light")}
                  options={[
                    { value: "dark", label: "Dark Mode" },
                    { value: "light", label: "Light Mode" },
                  ]}
                  label="Theme"
                  description="Choose your preferred color scheme"
                />
              </SettingRow>

              <SettingRow>
                <Select
                  value={settings.accentColor}
                  onChange={(value) =>
                    updateSetting("accentColor", value as "indigo" | "cyan" | "orange" | "gold")
                  }
                  options={[
                    { value: "indigo", label: "Electric Indigo" },
                    { value: "cyan", label: "Cyan" },
                    { value: "orange", label: "Orange" },
                    { value: "gold", label: "Champagne Gold" },
                  ]}
                  label="Accent Color"
                  description="Primary accent color for the interface"
                />
              </SettingRow>

              <SettingRow>
                <Select
                  value={settings.fontSize}
                  onChange={(value) =>
                    updateSetting("fontSize", value as "small" | "medium" | "large")
                  }
                  options={[
                    { value: "small", label: "Small" },
                    { value: "medium", label: "Medium" },
                    { value: "large", label: "Large" },
                  ]}
                  label="Font Size"
                  description="Adjust text size for readability"
                />
              </SettingRow>
            </SettingsSection>
          )}

          {/* Pomodoro Settings */}
          {activeCategory === "pomodoro" && (
            <SettingsSection
              title="Pomodoro Timer"
              description="Configure your focus and break durations"
            >
              <SettingRow>
                <Slider
                  value={settings.pomodoroWorkDuration}
                  onChange={(value) => updateSetting("pomodoroWorkDuration", value)}
                  min={15}
                  max={60}
                  step={5}
                  label="Work Duration"
                  description="Length of focused work sessions"
                  unit=" min"
                />
              </SettingRow>

              <SettingRow>
                <Slider
                  value={settings.pomodoroShortBreakDuration}
                  onChange={(value) => updateSetting("pomodoroShortBreakDuration", value)}
                  min={3}
                  max={15}
                  step={1}
                  label="Short Break Duration"
                  description="Length of short breaks between work sessions"
                  unit=" min"
                />
              </SettingRow>

              <SettingRow>
                <Slider
                  value={settings.pomodoroLongBreakDuration}
                  onChange={(value) => updateSetting("pomodoroLongBreakDuration", value)}
                  min={10}
                  max={30}
                  step={5}
                  label="Long Break Duration"
                  description="Length of long breaks after multiple sessions"
                  unit=" min"
                />
              </SettingRow>

              <SettingRow>
                <Slider
                  value={settings.pomodoroSessionsBeforeLongBreak}
                  onChange={(value) =>
                    updateSetting("pomodoroSessionsBeforeLongBreak", value)
                  }
                  min={2}
                  max={8}
                  step={1}
                  label="Sessions Before Long Break"
                  description="Number of work sessions before taking a long break"
                  unit=" sessions"
                />
              </SettingRow>
            </SettingsSection>
          )}

          {/* Notifications Settings */}
          {activeCategory === "notifications" && (
            <SettingsSection
              title="Notifications"
              description="Manage alerts and sound preferences"
            >
              <SettingRow>
                <Toggle
                  enabled={settings.notificationsEnabled}
                  onChange={(value) => updateSetting("notificationsEnabled", value)}
                  label="Enable Notifications"
                  description="Receive alerts for timer completions and reminders"
                />
              </SettingRow>

              <SettingRow>
                <Toggle
                  enabled={settings.soundEnabled}
                  onChange={(value) => updateSetting("soundEnabled", value)}
                  label="Sound Effects"
                  description="Play audio when timers complete"
                  disabled={!settings.notificationsEnabled}
                />
              </SettingRow>

              <SettingRow>
                <Toggle
                  enabled={settings.desktopNotifications}
                  onChange={(value) => updateSetting("desktopNotifications", value)}
                  label="Desktop Notifications"
                  description="Show system notifications (requires browser permission)"
                  disabled={!settings.notificationsEnabled}
                />
              </SettingRow>

              <SettingRow>
                <Toggle
                  enabled={settings.breakReminders}
                  onChange={(value) => updateSetting("breakReminders", value)}
                  label="Break Reminders"
                  description="Get reminded to take breaks during long work sessions"
                  disabled={!settings.notificationsEnabled}
                />
              </SettingRow>
            </SettingsSection>
          )}

          {/* Data & Privacy Settings */}
          {activeCategory === "data" && (
            <SettingsSection
              title="Data & Privacy"
              description="Manage your data and privacy preferences"
            >
              <SettingRow>
                <Toggle
                  enabled={settings.analyticsEnabled}
                  onChange={(value) => updateSetting("analyticsEnabled", value)}
                  label="Analytics Tracking"
                  description="Help improve Artemis by sharing anonymous usage data"
                />
              </SettingRow>

              <SettingRow>
                <Slider
                  value={settings.dataRetentionDays}
                  onChange={(value) => updateSetting("dataRetentionDays", value)}
                  min={30}
                  max={365}
                  step={30}
                  label="Data Retention"
                  description="How long to keep historical task and session data"
                  unit=" days"
                />
              </SettingRow>

              <SettingRow>
                <div className="flex gap-3">
                  <button
                    onClick={exportSettings}
                    className="px-4 py-2 rounded-lg bg-luxury-indigo text-white hover:bg-luxury-indigo/90 transition-colors"
                  >
                    Export Settings
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Are you sure? This will reset all settings to defaults.")) {
                        resetSettings()
                      }
                    }}
                    className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors"
                  >
                    Reset to Defaults
                  </button>
                </div>
              </SettingRow>
            </SettingsSection>
          )}
        </div>
      </div>
    </AppShell>
  )
}
