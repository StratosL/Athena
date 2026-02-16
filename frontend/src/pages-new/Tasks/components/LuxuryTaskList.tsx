import { TaskCard } from "@/design-system/components"
import { celebrateTaskComplete } from "@/design-system/animations/confetti"
import type { Task } from "@/lib/api"

interface LuxuryTaskListProps {
  tasks: Task[]
  onComplete?: (id: string) => void
  onDelete?: (id: string) => void
  emptyMessage?: string
}

export function LuxuryTaskList({
  tasks,
  onComplete,
  onDelete,
  emptyMessage = "No tasks found",
}: LuxuryTaskListProps) {
  const handleComplete = (id: string) => {
    onComplete?.(id)
    celebrateTaskComplete()
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-luxury-text-secondary">
        <p>{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          id={task.id}
          title={task.title}
          description={task.description}
          quadrant={task.quadrant}
          pomodoroCount={task.pomodoro_count}
          completed={task.status === "completed"}
          onCompletedChange={() => handleComplete(task.id)}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
