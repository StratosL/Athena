import { DailyStatsBar } from "@/design-system/components"
import { useAnalyticsSummary } from "@/hooks/useAnalytics"

export function DashboardStatsBar() {
  const { data: summary, isLoading } = useAnalyticsSummary("day")

  return (
    <DailyStatsBar
      pomodoros={summary?.total_pomodoros ?? 0}
      focusMinutes={summary?.total_focus_minutes ?? 0}
      tasksCompleted={summary?.tasks_completed ?? 0}
      completionRate={summary?.task_completion_rate ?? 0}
      isLoading={isLoading}
    />
  )
}
