import { useState, useMemo, useCallback } from "react"
import { QuadrantGrid, SwipeableTabs } from "@/design-system/components"
import type { SwipeableTab } from "@/design-system/components"
import { celebrateTaskComplete } from "@/design-system/animations/confetti"
import { AppShell } from "../layout"
import { LuxuryQuickTaskInput, LuxuryTaskList, ViewToggle } from "./components"
import {
  useTasks,
  useCreateTask,
  useCompleteTask,
  useDeleteTask,
} from "@/hooks/useTasks"

type ViewMode = "matrix" | "list"

const quadrantLabels = {
  1: "Do First",
  2: "Schedule",
  3: "Delegate",
  4: "Eliminate",
} as const

export function Tasks() {
  const [viewMode, setViewMode] = useState<ViewMode>("matrix")
  const { data, isLoading, error } = useTasks()
  const createTask = useCreateTask()
  const completeTask = useCompleteTask()
  const deleteTask = useDeleteTask()

  const handleCreateTask = (title: string, quadrant: 1 | 2 | 3 | 4) => {
    createTask.mutate({ title, quadrant })
  }

  const handleCompleteTask = useCallback((id: string) => {
    completeTask.mutate(id)
    celebrateTaskComplete()
  }, [completeTask])

  const handleDeleteTask = useCallback((id: string) => {
    if (window.confirm("Delete this task? This cannot be undone.")) {
      deleteTask.mutate(id)
    }
  }, [deleteTask])

  const tasks = data?.items ?? []
  const pendingTasks = tasks.filter((t) => t.status !== "completed")

  // Mobile swipeable tabs for each quadrant
  const quadrantTabs: SwipeableTab[] = useMemo(
    () =>
      ([1, 2, 3, 4] as const).map((q) => ({
        label: `${quadrantLabels[q]} (${pendingTasks.filter((t) => t.quadrant === q).length})`,
        content: (
          <LuxuryTaskList
            tasks={pendingTasks.filter((t) => t.quadrant === q)}
            onComplete={handleCompleteTask}
            onDelete={handleDeleteTask}
            emptyMessage={`No ${quadrantLabels[q].toLowerCase()} tasks`}
          />
        ),
      })),
    [pendingTasks, handleCompleteTask, handleDeleteTask]
  )

  return (
    <AppShell
      title="Task Management"
      subtitle="Prioritize with the Eisenhower Matrix"
      actions={<ViewToggle value={viewMode} onChange={setViewMode} />}
      fillHeight
    >
      {/* Quick Task Input */}
      <div className="mb-6 flex-shrink-0">
        <LuxuryQuickTaskInput onSubmit={handleCreateTask} />
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="text-center py-12 text-luxury-text-secondary">Loading tasks...</div>
      ) : error ? (
        <div className="text-center py-12 text-red-400">
          Failed to load tasks. Is the backend running?
        </div>
      ) : viewMode === "matrix" ? (
        <>
          {/* Desktop: 2x2 grid */}
          <div className="hidden md:flex flex-1 min-h-0">
            <QuadrantGrid
              tasks={pendingTasks}
              onComplete={handleCompleteTask}
              onDelete={handleDeleteTask}
              className="flex-1 lg:[&>*]:min-h-0 lg:[&>*]:overflow-auto"
            />
          </div>
          {/* Mobile: Swipeable tabs per quadrant */}
          <div className="md:hidden">
            <SwipeableTabs tabs={quadrantTabs} />
          </div>
        </>
      ) : (
        <div className="flex-1 min-h-0 overflow-auto">
          <LuxuryTaskList
            tasks={pendingTasks}
            onComplete={handleCompleteTask}
            onDelete={handleDeleteTask}
            emptyMessage="No tasks yet. Add one above!"
          />
        </div>
      )}

      {/* Stats Footer */}
      <footer className="flex-shrink-0 mt-4 text-center text-luxury-text-secondary text-sm">
        <p>
          {pendingTasks.length} pending tasks |{" "}
          {tasks.filter((t) => t.status === "completed").length} completed
        </p>
      </footer>
    </AppShell>
  )
}
