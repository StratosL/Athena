import { useState } from "react"
import { celebrateDailyPlanComplete } from "@/design-system/animations/confetti"
import { AppShell } from "../layout"
import { LuxuryPlanView, LuxuryTaskSelector, LuxuryBacklogSidebar } from "./components"
import { useTodayPlan, useAssignTask, useRemoveTask } from "@/hooks/useDailyPlan"
import { useTasks, useCompleteTask } from "@/hooks/useTasks"
import type { SlotType } from "@/lib/api"
import { useEffect, useRef } from "react"

export function DailyPlan() {
  const [selectorOpen, setSelectorOpen] = useState(false)
  const [targetSlot, setTargetSlot] = useState<SlotType>("major")
  const prevCompletionRef = useRef<number | null>(null)

  const { data: plan, isLoading: planLoading, error: planError } = useTodayPlan()
  const { data: tasksData, isLoading: tasksLoading } = useTasks()
  const assignTask = useAssignTask()
  const removeTask = useRemoveTask()
  const completeTask = useCompleteTask()

  // Celebrate 100% completion
  useEffect(() => {
    if (plan && prevCompletionRef.current !== null) {
      if (plan.completion_rate >= 100 && prevCompletionRef.current < 100) {
        celebrateDailyPlanComplete()
      }
    }
    if (plan) {
      prevCompletionRef.current = plan.completion_rate
    }
  }, [plan])

  const handleSlotClick = (slot: SlotType) => {
    setTargetSlot(slot)
    setSelectorOpen(true)
  }

  const handleAssignTask = (taskId: string) => {
    if (!plan) return
    assignTask.mutate({
      planId: plan.id,
      assignment: { task_id: taskId, slot: targetSlot },
    })
  }

  const handleRemoveTask = (taskId: string) => {
    if (!plan) return
    removeTask.mutate({ planId: plan.id, taskId })
  }

  const handleCompleteTask = (taskId: string) => {
    completeTask.mutate(taskId)
  }

  const assignedTaskIds = plan
    ? [
        plan.major_task_id,
        ...plan.medium_task_ids,
        ...plan.small_task_ids,
      ].filter((id): id is string => !!id)
    : []

  const allTasks = tasksData?.items ?? []
  const backlogTasks = allTasks.filter(
    (t) => t.status !== "completed" && !assignedTaskIds.includes(t.id)
  )

  const isLoading = planLoading || tasksLoading

  return (
    <AppShell
      title="Daily Planning"
      subtitle="Plan your day with the 1-3-5 rule"
      fillHeight
    >
      {isLoading ? (
        <div className="text-center py-12 text-luxury-text-secondary">
          Loading your daily plan...
        </div>
      ) : planError ? (
        <div className="text-center py-12 text-red-400">
          Failed to load daily plan. Is the backend running?
        </div>
      ) : plan ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0 lg:[&>*]:min-h-0 lg:[&>*]:overflow-auto">
          <div className="lg:col-span-2">
            <LuxuryPlanView
              plan={plan}
              onRemoveTask={handleRemoveTask}
              onCompleteTask={handleCompleteTask}
              onSlotClick={handleSlotClick}
            />
          </div>
          <div>
            <LuxuryBacklogSidebar
              tasks={backlogTasks}
              onComplete={handleCompleteTask}
            />
          </div>
        </div>
      ) : null}

      <LuxuryTaskSelector
        isOpen={selectorOpen}
        onClose={() => setSelectorOpen(false)}
        tasks={allTasks}
        assignedTaskIds={assignedTaskIds}
        onSelect={handleAssignTask}
        targetSlot={targetSlot}
      />

      <footer className="flex-shrink-0 mt-4 text-center text-luxury-text-secondary text-sm">
        <p>1 Major · 3 Medium · 5 Small = 9 focused tasks for your day</p>
      </footer>
    </AppShell>
  )
}
