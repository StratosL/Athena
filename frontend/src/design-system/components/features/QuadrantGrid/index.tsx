import { cn } from "@/lib/utils"
import { GlassCard } from "../../base/GlassCard"
import { Badge } from "../../base/Badge"
import type { QuadrantGridProps } from "./QuadrantGrid.types"
import type { Task } from "@/lib/api"

const quadrantConfig = {
  1: {
    title: "Do First",
    subtitle: "Urgent & Important",
    variant: "q1" as const,
    glow: "shadow-[0_0_20px_rgba(99,102,241,0.15)]",
    borderColor: "border-luxury-indigo/20",
    headerColor: "text-luxury-indigo",
    dotColor: "bg-luxury-indigo",
  },
  2: {
    title: "Schedule",
    subtitle: "Important, Not Urgent",
    variant: "q2" as const,
    glow: "shadow-[0_0_20px_rgba(6,182,212,0.15)]",
    borderColor: "border-luxury-cyan/20",
    headerColor: "text-luxury-cyan",
    dotColor: "bg-luxury-cyan",
  },
  3: {
    title: "Delegate",
    subtitle: "Urgent, Not Important",
    variant: "q3" as const,
    glow: "shadow-[0_0_20px_rgba(249,115,22,0.15)]",
    borderColor: "border-luxury-orange/20",
    headerColor: "text-luxury-orange",
    dotColor: "bg-luxury-orange",
  },
  4: {
    title: "Eliminate",
    subtitle: "Neither",
    variant: "q4" as const,
    glow: "shadow-[0_0_20px_rgba(100,116,139,0.15)]",
    borderColor: "border-luxury-slate/20",
    headerColor: "text-luxury-slate",
    dotColor: "bg-luxury-slate",
  },
} as const

function CompactTaskItem({
  task,
  onComplete,
}: {
  task: Task
  quadrant: 1 | 2 | 3 | 4
  onComplete?: (id: string) => void
}) {
  const isCompleted = task.status === "completed"

  return (
    <div
      className={cn(
        "flex items-center gap-2 px-2 py-1.5 rounded-md transition-colors",
        "hover:bg-white/5",
        isCompleted && "opacity-50"
      )}
    >
      <button
        onClick={() => onComplete?.(task.id)}
        className={cn(
          "w-4 h-4 rounded border flex-shrink-0 flex items-center justify-center transition-colors",
          isCompleted
            ? "bg-luxury-gold border-luxury-gold"
            : `border-luxury-border hover:border-luxury-gold`
        )}
      >
        {isCompleted && (
          <svg className="w-3 h-3 text-luxury-obsidian" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </button>
      <span
        className={cn(
          "text-sm text-luxury-text-primary truncate",
          isCompleted && "line-through text-luxury-text-secondary"
        )}
      >
        {task.title}
      </span>
    </div>
  )
}

function FullTaskItem({
  task,
  quadrant,
  onComplete,
  onDelete,
  onClick,
}: {
  task: Task
  quadrant: 1 | 2 | 3 | 4
  onComplete?: (id: string) => void
  onDelete?: (id: string) => void
  onClick?: (task: Task) => void
}) {
  const isCompleted = task.status === "completed"
  const config = quadrantConfig[quadrant]

  return (
    <GlassCard
      className={cn(
        "p-3 cursor-pointer",
        config.glow,
        isCompleted && "opacity-50"
      )}
      hoverable={false}
      onClick={() => onClick?.(task)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 min-w-0 flex-1">
          <button
            onClick={(e) => {
              e.stopPropagation()
              onComplete?.(task.id)
            }}
            className={cn(
              "w-5 h-5 rounded border flex-shrink-0 flex items-center justify-center mt-0.5 transition-colors",
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
          <div className="min-w-0 flex-1">
            <p className={cn(
              "text-sm font-medium text-luxury-text-primary truncate",
              isCompleted && "line-through text-luxury-text-secondary"
            )}>
              {task.title}
            </p>
            {task.pomodoro_count > 0 && (
              <span className="text-xs text-luxury-text-secondary">
                {task.pomodoro_count} pomodoros
              </span>
            )}
          </div>
        </div>
        {onDelete && !isCompleted && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete(task.id)
            }}
            className="text-luxury-text-secondary hover:text-red-400 transition-colors flex-shrink-0"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        )}
      </div>
    </GlassCard>
  )
}

function QuadrantSection({
  quadrant,
  tasks,
  compact,
  onComplete,
  onDelete,
  onClick,
}: {
  quadrant: 1 | 2 | 3 | 4
  tasks: Task[]
  compact?: boolean
  onComplete?: (id: string) => void
  onDelete?: (id: string) => void
  onClick?: (task: Task) => void
}) {
  const config = quadrantConfig[quadrant]
  const quadrantTasks = tasks.filter((t) => t.quadrant === quadrant)

  return (
    <GlassCard
      className={cn(
        "p-4",
        compact ? "min-h-[160px]" : "min-h-[260px]",
        config.glow
      )}
      hoverable={false}
    >
      <div className={cn("mb-3 flex items-center gap-2", compact && "mb-2")}>
        <span className={cn("w-2 h-2 rounded-full", config.dotColor)} />
        <h3 className={cn("font-playfair font-semibold", config.headerColor, compact ? "text-sm" : "text-base")}>
          {config.title}
        </h3>
        {!compact && (
          <span className="text-xs text-luxury-text-secondary ml-auto">
            {config.subtitle}
          </span>
        )}
        <Badge variant={config.variant} className="ml-auto text-[10px] px-1.5 py-0">
          {quadrantTasks.length}
        </Badge>
      </div>

      <div className={cn("space-y-1", compact ? "max-h-[120px] overflow-y-auto" : "space-y-2")}>
        {quadrantTasks.length === 0 ? (
          <p className={cn(
            "text-luxury-text-secondary text-center",
            compact ? "text-xs py-4" : "text-sm py-8"
          )}>
            No tasks
          </p>
        ) : compact ? (
          quadrantTasks.slice(0, 5).map((task) => (
            <CompactTaskItem
              key={task.id}
              task={task}
              quadrant={quadrant}
              onComplete={onComplete}
            />
          ))
        ) : (
          quadrantTasks.map((task) => (
            <FullTaskItem
              key={task.id}
              task={task}
              quadrant={quadrant}
              onComplete={onComplete}
              onDelete={onDelete}
              onClick={onClick}
            />
          ))
        )}
        {compact && quadrantTasks.length > 5 && (
          <p className="text-xs text-luxury-text-secondary text-center">
            +{quadrantTasks.length - 5} more
          </p>
        )}
      </div>
    </GlassCard>
  )
}

export function QuadrantGrid({
  tasks,
  compact = false,
  onComplete,
  onDelete,
  onClick,
  className,
}: QuadrantGridProps) {
  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 gap-4", className)}>
      <QuadrantSection quadrant={1} tasks={tasks} compact={compact} onComplete={onComplete} onDelete={onDelete} onClick={onClick} />
      <QuadrantSection quadrant={2} tasks={tasks} compact={compact} onComplete={onComplete} onDelete={onDelete} onClick={onClick} />
      <QuadrantSection quadrant={3} tasks={tasks} compact={compact} onComplete={onComplete} onDelete={onDelete} onClick={onClick} />
      <QuadrantSection quadrant={4} tasks={tasks} compact={compact} onComplete={onComplete} onDelete={onDelete} onClick={onClick} />
    </div>
  )
}

export default QuadrantGrid
export type { QuadrantGridProps } from "./QuadrantGrid.types"
