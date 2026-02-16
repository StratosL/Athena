import { cn } from "@/lib/utils"
import { GlassCard } from "../../base/GlassCard"
import type { DailyStatsBarProps } from "./DailyStatsBar.types"

function StatItem({
  label,
  value,
  unit,
  color,
}: {
  label: string
  value: string | number
  unit?: string
  color: string
}) {
  return (
    <div className="flex flex-col items-center gap-1">
      <p className={cn("text-2xl font-bold font-inter", color)}>
        {value}
        {unit && <span className="text-sm font-normal ml-0.5">{unit}</span>}
      </p>
      <p className="text-xs text-luxury-text-secondary">{label}</p>
    </div>
  )
}

export function DailyStatsBar({
  pomodoros,
  focusMinutes,
  tasksCompleted,
  completionRate,
  isLoading,
  className,
}: DailyStatsBarProps) {
  if (isLoading) {
    return (
      <GlassCard className={cn("p-4", className)} hoverable={false}>
        <p className="text-sm text-luxury-text-secondary text-center">Loading stats...</p>
      </GlassCard>
    )
  }

  const focusHours = Math.round((focusMinutes / 60) * 10) / 10

  return (
    <GlassCard className={cn("p-4", className)} hoverable={false}>
      <div className="grid grid-cols-4 gap-4">
        <StatItem
          label="Pomodoros"
          value={pomodoros}
          color="text-luxury-indigo"
        />
        <StatItem
          label="Focus Time"
          value={focusHours}
          unit="h"
          color="text-luxury-cyan"
        />
        <StatItem
          label="Tasks Done"
          value={tasksCompleted}
          color="text-luxury-gold"
        />
        <StatItem
          label="Completion"
          value={completionRate}
          unit="%"
          color="text-luxury-orange"
        />
      </div>
    </GlassCard>
  )
}

export default DailyStatsBar
export type { DailyStatsBarProps } from "./DailyStatsBar.types"
