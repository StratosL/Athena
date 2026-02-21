import { cn } from "@/lib/utils"

interface LuxuryPlanProgressProps {
  completedTasks: number
  totalTasks: number
  completionRate: number
  className?: string
}

export function LuxuryPlanProgress({
  completedTasks,
  totalTasks,
  completionRate,
  className,
}: LuxuryPlanProgressProps) {
  const isComplete = completionRate >= 100

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between text-base">
        <span className="text-luxury-text-secondary font-medium">Today's Progress</span>
        <span className={cn("font-medium", isComplete ? "text-green-400" : "text-luxury-text-primary")}>
          {completedTasks}/{totalTasks} tasks
        </span>
      </div>
      <div className="h-2.5 bg-white/5 rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full transition-all duration-500 rounded-full",
            isComplete ? "bg-green-500" : "bg-luxury-gold"
          )}
          style={{ width: `${Math.min(completionRate, 100)}%` }}
        />
      </div>
      <p className="text-sm text-luxury-text-secondary text-right">
        {completionRate.toFixed(0)}% complete
      </p>
    </div>
  )
}
