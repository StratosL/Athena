import { cn } from "@/lib/utils"
import { GlassCard, ProgressRing } from "@/design-system/components"
import type { ProductivityScore } from "@/lib/api"

interface LuxuryProductivityScoreProps {
  score: ProductivityScore
  className?: string
}

const componentLabels: Record<string, string> = {
  focus_sessions: "Focus Sessions",
  task_completion: "Task Completion",
  plan_adherence: "Plan Adherence",
}

export function LuxuryProductivityScore({ score, className }: LuxuryProductivityScoreProps) {
  return (
    <GlassCard className={cn("p-6", className)} hoverable={false}>
      <h3 className="font-playfair font-semibold text-luxury-text-primary mb-4">
        Productivity Score
      </h3>

      <div className="flex justify-center mb-6">
        <ProgressRing percentage={score.score} size={140} strokeWidth={10} active={false}>
          <div className="text-center">
            <span className="text-3xl font-bold text-luxury-text-primary">{score.score}</span>
            <p className="text-xs text-luxury-text-secondary">/100</p>
          </div>
        </ProgressRing>
      </div>

      <div className="space-y-3">
        {Object.entries(score.components).map(([key, value]) => (
          <div key={key}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-luxury-text-secondary">
                {componentLabels[key] || key}
              </span>
              <span className="text-luxury-text-primary font-medium">{value}%</span>
            </div>
            <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-luxury-indigo to-luxury-gold transition-all duration-500 rounded-full"
                style={{ width: `${Math.min(value, 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  )
}
