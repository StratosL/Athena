import { QuadrantGrid } from "@/design-system/components"
import { useTasks, useCompleteTask } from "@/hooks/useTasks"
import { celebrateTaskComplete } from "@/design-system/animations/confetti"

export function DashboardMatrixColumn() {
  const { data, isLoading } = useTasks()
  const completeTask = useCompleteTask()

  const tasks = data?.items ?? []
  const pendingTasks = tasks.filter((t) => t.status !== "completed")

  const handleComplete = (id: string) => {
    completeTask.mutate(id)
    celebrateTaskComplete()
  }

  if (isLoading) {
    return (
      <div className="text-center py-8 text-luxury-text-secondary text-sm">
        Loading tasks...
      </div>
    )
  }

  return <QuadrantGrid tasks={pendingTasks} compact onComplete={handleComplete} />
}
