import { cn } from "@/lib/utils"
import type { TimeRange } from "@/lib/api"

interface LuxuryTimeRangeSelectorProps {
  value: TimeRange
  onChange: (value: TimeRange) => void
  className?: string
}

const ranges: { value: TimeRange; label: string }[] = [
  { value: "day", label: "Today" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
]

export function LuxuryTimeRangeSelector({ value, onChange, className }: LuxuryTimeRangeSelectorProps) {
  return (
    <div className={cn("flex gap-1 backdrop-blur-md bg-luxury-card border border-luxury-border rounded-lg p-1", className)}>
      {ranges.map((range) => (
        <button
          key={range.value}
          onClick={() => onChange(range.value)}
          className={cn(
            "px-4 py-1.5 rounded-md transition-all text-sm font-medium",
            value === range.value
              ? "bg-luxury-gold text-luxury-obsidian shadow-glow-gold"
              : "text-luxury-text-secondary hover:text-luxury-text-primary hover:bg-white/5"
          )}
        >
          {range.label}
        </button>
      ))}
    </div>
  )
}
