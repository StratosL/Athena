import { cn } from "@/lib/utils"
import { GlassCard, Badge } from "@/design-system/components"
import type { Task } from "@/lib/api"

interface LuxuryTaskLinkerProps {
  tasks: Task[]
  selectedTask: Task | null
  onSelect: (task: Task | null) => void
  className?: string
}

const quadrantBadgeVariant = {
  1: "q1" as const,
  2: "q2" as const,
  3: "q3" as const,
  4: "q4" as const,
}

export function LuxuryTaskLinker({ tasks, selectedTask, onSelect, className }: LuxuryTaskLinkerProps) {
  return (
    <GlassCard className={cn("p-5", className)} hoverable={false}>
      <h3 className="text-lg font-playfair font-semibold text-luxury-text-primary mb-3">
        Link to Task
      </h3>

      {selectedTask && (
        <div className="p-3 mb-3 rounded-lg bg-luxury-indigo/10 border border-luxury-indigo/20">
          <p className="text-base font-medium text-luxury-indigo">{selectedTask.title}</p>
          <button
            onClick={() => onSelect(null)}
            className="text-sm text-luxury-text-secondary hover:text-luxury-text-primary mt-1"
          >
            Remove link
          </button>
        </div>
      )}

      {tasks.length === 0 ? (
        <p className="text-base text-luxury-text-secondary">No pending tasks.</p>
      ) : (
        <div className="max-h-64 overflow-y-auto space-y-1">
          {tasks.slice(0, 10).map((task) => (
            <button
              key={task.id}
              onClick={() => onSelect(task)}
              className={cn(
                "w-full text-left p-2.5 rounded-lg text-base transition-colors",
                selectedTask?.id === task.id
                  ? "bg-luxury-indigo/20 text-luxury-indigo"
                  : "hover:bg-white/5 text-luxury-text-secondary"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="truncate">{task.title}</span>
                <Badge variant={quadrantBadgeVariant[task.quadrant]} className="flex-shrink-0 text-xs">
                  Q{task.quadrant}
                </Badge>
              </div>
              <span className="text-sm text-luxury-text-secondary">
                {task.pomodoro_count} pomodoros
              </span>
            </button>
          ))}
        </div>
      )}
    </GlassCard>
  )
}
