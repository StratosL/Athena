import { Link } from "react-router-dom"
import { cn } from "@/lib/utils"
import { GlassCard, Badge } from "@/design-system/components"
import type { Task } from "@/lib/api"

interface LuxuryBacklogSidebarProps {
  tasks: Task[]
  onComplete?: (id: string) => void
  className?: string
}

const quadrantBadgeVariant = {
  1: "q1" as const,
  2: "q2" as const,
  3: "q3" as const,
  4: "q4" as const,
}

export function LuxuryBacklogSidebar({ tasks, onComplete, className }: LuxuryBacklogSidebarProps) {
  return (
    <GlassCard className={cn("p-6", className)} hoverable={false}>
      <h3 className="text-lg font-playfair font-semibold text-luxury-text-primary mb-1">
        Task Backlog
      </h3>
      <p className="text-base text-luxury-text-secondary mb-4">
        {tasks.length} tasks available
      </p>

      {tasks.length === 0 ? (
        <p className="text-center py-8 text-luxury-text-secondary text-sm">
          No tasks in backlog.{" "}
          <Link to="/tasks" className="text-luxury-indigo hover:underline">
            Create some tasks
          </Link>{" "}
          to get started.
        </p>
      ) : (
        <div className="space-y-2 overflow-y-auto pr-1">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="flex items-center justify-between p-3 rounded-lg border border-luxury-border hover:bg-white/5 transition-colors"
            >
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <button
                  onClick={() => onComplete?.(task.id)}
                  className="w-5 h-5 rounded border border-luxury-border hover:border-luxury-gold flex-shrink-0 transition-colors"
                />
                <span className="text-base text-luxury-text-primary truncate">
                  {task.title}
                </span>
              </div>
              <Badge variant={quadrantBadgeVariant[task.quadrant]} className="ml-2 flex-shrink-0">
                Q{task.quadrant}
              </Badge>
            </div>
          ))}
        </div>
      )}
    </GlassCard>
  )
}
