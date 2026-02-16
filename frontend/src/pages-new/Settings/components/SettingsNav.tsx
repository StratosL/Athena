import { Settings as SettingsIcon, Palette, Clock, Bell, Database } from "lucide-react"
import { cn } from "@/lib/utils"
import { motion } from "motion/react"
import type { SettingsCategory } from "../types"

const categories: SettingsCategory[] = [
  { id: "general", label: "General", icon: "SettingsIcon", description: "Profile & Work Preferences" },
  { id: "appearance", label: "Appearance", icon: "Palette", description: "Theme & Colors" },
  { id: "pomodoro", label: "Pomodoro", icon: "Clock", description: "Timer Configuration" },
  { id: "notifications", label: "Notifications", icon: "Bell", description: "Alerts & Sounds" },
  { id: "data", label: "Data & Privacy", icon: "Database", description: "Export & Clear History" },
]

const iconMap = {
  SettingsIcon,
  Palette,
  Clock,
  Bell,
  Database,
}

interface SettingsNavProps {
  activeCategory: string
  onCategoryChange: (categoryId: string) => void
}

export function SettingsNav({ activeCategory, onCategoryChange }: SettingsNavProps) {
  return (
    <nav className="space-y-2">
      {categories.map((category) => {
        const Icon = iconMap[category.icon as keyof typeof iconMap]
        const isActive = activeCategory === category.id

        return (
          <motion.button
            key={category.id}
            onClick={() => onCategoryChange(category.id)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={cn(
              "w-full text-left px-4 py-3 rounded-lg transition-all duration-300",
              "backdrop-blur-md border border-luxury-border",
              isActive
                ? "bg-luxury-card shadow-glow-gold"
                : "bg-luxury-card/20 hover:bg-luxury-card/40"
            )}
          >
            <div className="flex items-center gap-3">
              <Icon
                className={cn(
                  "w-5 h-5",
                  isActive ? "text-luxury-gold" : "text-luxury-text-secondary"
                )}
              />
              <div>
                <p
                  className={cn(
                    "text-sm font-medium",
                    isActive ? "text-luxury-gold" : "text-luxury-text-primary"
                  )}
                >
                  {category.label}
                </p>
                <p className="text-xs text-luxury-text-secondary">
                  {category.description}
                </p>
              </div>
            </div>
          </motion.button>
        )
      })}
    </nav>
  )
}
