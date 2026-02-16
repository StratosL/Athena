import { cn } from "@/lib/utils"
import { GlassCard } from "../../base/GlassCard"
import type { PlanWidgetProps } from "./PlanWidget.types"
import type { TaskInfo } from "@/lib/api"

function SlotItem({
  task,
  label,
  dotColor,
  onComplete,
}: {
  task?: TaskInfo
  label: string
  dotColor: string
  onComplete?: (taskId: string) => void
}) {
  const isCompleted = task?.status === "completed"

  if (!task) {
    return (
      <div className="flex items-center gap-2 px-2 py-1.5 rounded-md border border-dashed border-luxury-border/50">
        <span className={cn("w-2 h-2 rounded-full opacity-30", dotColor)} />
        <span className="text-xs text-luxury-text-secondary/50">{label}</span>
      </div>
    )
  }

  return (
    <div className={cn(
      "flex items-center gap-2 px-2 py-1.5 rounded-md transition-colors",
      "hover:bg-white/5",
      isCompleted && "opacity-50"
    )}>
      <button
        onClick={() => onComplete?.(task.id)}
        className={cn(
          "w-4 h-4 rounded border flex-shrink-0 flex items-center justify-center transition-colors",
          isCompleted
            ? "bg-luxury-gold border-luxury-gold"
            : "border-luxury-border hover:border-luxury-gold"
        )}
      >
        {isCompleted && (
          <svg className="w-3 h-3 text-luxury-obsidian" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </button>
      <span className={cn(
        "text-sm text-luxury-text-primary truncate",
        isCompleted && "line-through text-luxury-text-secondary"
      )}>
        {task.title}
      </span>
    </div>
  )
}

export function PlanWidget({ plan, isLoading, onCompleteTask, className }: PlanWidgetProps) {
  if (isLoading) {
    return (
      <GlassCard className={cn("p-6", className)} hoverable={false}>
        <p className="text-sm text-luxury-text-secondary text-center">Loading plan...</p>
      </GlassCard>
    )
  }

  const mediumSlots = Array.from({ length: 3 }, (_, i) => plan?.medium_tasks[i])
  const smallSlots = Array.from({ length: 5 }, (_, i) => plan?.small_tasks[i])
  const completionRate = plan?.completion_rate ?? 0

  return (
    <GlassCard className={cn("p-6", className)} hoverable={false}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-playfair font-semibold text-luxury-text-primary">
          Today's Plan
        </h3>
        <span className={cn(
          "text-xs font-medium px-2 py-0.5 rounded-full",
          completionRate >= 100
            ? "bg-green-500/20 text-green-400"
            : "bg-luxury-gold/20 text-luxury-gold"
        )}>
          {completionRate.toFixed(0)}%
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 bg-white/5 rounded-full mb-4 overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500",
            completionRate >= 100 ? "bg-green-500" : "bg-luxury-gold"
          )}
          style={{ width: `${Math.min(completionRate, 100)}%` }}
        />
      </div>

      <div className="space-y-3">
        {/* Major */}
        <div>
          <p className="text-xs font-medium text-luxury-indigo mb-1">Major (1)</p>
          <SlotItem
            task={plan?.major_task}
            label="Major Task"
            dotColor="bg-luxury-indigo"
            onComplete={onCompleteTask}
          />
        </div>

        {/* Medium */}
        <div>
          <p className="text-xs font-medium text-luxury-cyan mb-1">Medium (3)</p>
          <div className="space-y-1">
            {mediumSlots.map((task, i) => (
              <SlotItem
                key={task?.id ?? `m-${i}`}
                task={task}
                label={`Medium ${i + 1}`}
                dotColor="bg-luxury-cyan"
                onComplete={onCompleteTask}
              />
            ))}
          </div>
        </div>

        {/* Small */}
        <div>
          <p className="text-xs font-medium text-luxury-orange mb-1">Small (5)</p>
          <div className="space-y-1">
            {smallSlots.map((task, i) => (
              <SlotItem
                key={task?.id ?? `s-${i}`}
                task={task}
                label={`Small ${i + 1}`}
                dotColor="bg-luxury-orange"
                onComplete={onCompleteTask}
              />
            ))}
          </div>
        </div>
      </div>
    </GlassCard>
  )
}

export default PlanWidget
export type { PlanWidgetProps } from "./PlanWidget.types"
