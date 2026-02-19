import { useState } from "react"
import { AppShell } from "../layout"
import { LuxuryPomodoroTimer, LuxuryTaskLinker, LuxurySessionList } from "./components"
import { useTasks } from "@/hooks/useTasks"
import { usePomodoroSessions } from "@/hooks/usePomodoro"
import { usePomodoroShortcuts } from "@/hooks/useKeyboardShortcuts"
import { useTimerStore } from "@/stores/timerStore"
import { useStartSession, useStopSession } from "@/hooks/usePomodoro"
import type { Task } from "@/lib/api"

export function Pomodoro() {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const { data: tasksData } = useTasks({ status: "pending" })
  const { data: sessionsData } = usePomodoroSessions(undefined, 5)

  const { state } = useTimerStore()
  const startMutation = useStartSession()
  const stopMutation = useStopSession()

  // Keyboard shortcuts
  usePomodoroShortcuts({
    onToggleTimer: () => {
      if (state !== "IDLE") {
        stopMutation.mutate()
      } else {
        startMutation.mutate({ taskId: selectedTask?.id })
      }
    },
    onStopTimer: () => {
      if (state !== "IDLE") {
        stopMutation.mutate()
      }
    },
  })

  const pendingTasks = tasksData?.items ?? []
  const recentSessions = sessionsData?.items ?? []

  return (
    <AppShell
      title="Pomodoro Timer"
      subtitle="Focused work sessions with breaks"
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Timer - main column */}
        <div className="lg:col-span-2 flex flex-col items-center">
          <LuxuryPomodoroTimer
            taskId={selectedTask?.id}
            taskTitle={selectedTask?.title}
            className="max-w-xl w-full"
          />

          <p className="mt-6 text-center text-luxury-text-secondary text-sm">
            Tip: Stay focused during the work session, take a real break during breaks
          </p>
          <p className="text-xs text-luxury-text-secondary mt-1 text-center">
            Keyboard: Space to start/pause, Escape to stop
          </p>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <LuxuryTaskLinker
            tasks={pendingTasks}
            selectedTask={selectedTask}
            onSelect={setSelectedTask}
          />
          <LuxurySessionList sessions={recentSessions} />
        </div>
      </div>
    </AppShell>
  )
}
