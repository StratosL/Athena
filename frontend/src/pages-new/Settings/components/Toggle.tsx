import { motion } from "motion/react"
import { cn } from "@/lib/utils"

interface ToggleProps {
  enabled: boolean
  onChange: (enabled: boolean) => void
  label?: string
  description?: string
  disabled?: boolean
}

export function Toggle({ enabled, onChange, label, description, disabled }: ToggleProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex-1">
        {label && (
          <label className="block text-sm font-medium text-luxury-text-primary mb-1">
            {label}
          </label>
        )}
        {description && (
          <p className="text-sm text-luxury-text-secondary">{description}</p>
        )}
      </div>

      <button
        type="button"
        role="switch"
        aria-checked={enabled}
        disabled={disabled}
        onClick={() => !disabled && onChange(!enabled)}
        className={cn(
          "relative inline-flex h-6 w-11 items-center rounded-full",
          "transition-colors duration-300 ease-in-out",
          "focus:outline-none focus:ring-2 focus:ring-luxury-gold focus:ring-offset-2 focus:ring-offset-luxury-obsidian",
          enabled ? "bg-luxury-gold" : "bg-luxury-border",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        <motion.span
          className={cn(
            "inline-block h-4 w-4 rounded-full bg-white shadow-lg",
            "ring-0 transition-transform duration-300 ease-in-out"
          )}
          animate={{
            x: enabled ? 24 : 4,
          }}
          transition={{
            type: "spring",
            stiffness: 500,
            damping: 30,
          }}
        />
      </button>
    </div>
  )
}
