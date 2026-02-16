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
    deleteTask.mutate(id)
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
    >
      {/* Quick Task Input */}
      <div className="mb-6">
        <LuxuryQuickTaskInput onSubmit={handleCreateTask} className="max-w-3xl" />
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
          <div className="hidden md:block">
            <QuadrantGrid
              tasks={pendingTasks}
              onComplete={handleCompleteTask}
              onDelete={handleDeleteTask}
            />
          </div>
          {/* Mobile: Swipeable tabs per quadrant */}
          <div className="md:hidden">
            <SwipeableTabs tabs={quadrantTabs} />
          </div>
        </>
      ) : (
        <LuxuryTaskList
          tasks={pendingTasks}
          onComplete={handleCompleteTask}
          onDelete={handleDeleteTask}
          emptyMessage="No tasks yet. Add one above!"
        />
      )}

      {/* Stats Footer */}
      <footer className="mt-8 text-center text-luxury-text-secondary text-sm">
        <p>
          {pendingTasks.length} pending tasks |{" "}
          {tasks.filter((t) => t.status === "completed").length} completed
        </p>
      </footer>
    </AppShell>
  )
}
