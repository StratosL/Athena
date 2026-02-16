import { cn } from "@/lib/utils"
import { GlassCard } from "@/design-system/components"
import type { DailyPlanStats } from "@/lib/api"

interface LuxuryDailyPlanStatsProps {
  stats: DailyPlanStats
  className?: string
}

export function LuxuryDailyPlanStats({ stats, className }: LuxuryDailyPlanStatsProps) {
  return (
    <GlassCard className={cn("p-6", className)} hoverable={false}>
      <h3 className="font-playfair font-semibold text-luxury-text-primary mb-1">
        Daily Planning
      </h3>
      <p className="text-sm text-luxury-text-secondary mb-4">1-3-5 plan completion stats</p>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-luxury-text-secondary text-sm">Plans Created</span>
          <span className="text-xl font-bold text-luxury-text-primary">
            {stats.total_plans}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-luxury-text-secondary text-sm">Plans Completed</span>
          <span className="text-xl font-bold text-green-400">
            {stats.plans_completed}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-luxury-text-secondary text-sm">Avg Completion Rate</span>
          <span className="text-xl font-bold text-luxury-cyan">
            {stats.average_completion_rate}%
          </span>
        </div>
        <div className="pt-4 border-t border-luxury-border">
          <div className="flex items-center justify-between text-sm">
            <span className="text-luxury-text-secondary">Tasks in Plans</span>
            <span className="text-luxury-text-primary">
              {stats.tasks_completed}/{stats.tasks_planned} completed
            </span>
          </div>
        </div>
      </div>
    </GlassCard>
  )
}
