import { useState } from "react"
import { RefreshCw } from "lucide-react"
import { Button } from "@/design-system/components"
import { AppShell } from "../layout"
import {
  LuxuryMetricCard,
  LuxuryPomodoroChart,
  LuxuryProductivityScore,
  LuxuryQuadrantChart,
  LuxuryDailyPlanStats,
  LuxuryTimeRangeSelector,
} from "./components"
import {
  useAnalyticsSummary,
  usePomodoroTrends,
  useTaskDistribution,
} from "@/hooks/useAnalytics"
import type { TimeRange } from "@/lib/api"

export function Analytics() {
  const [period, setPeriod] = useState<TimeRange>("week")

  const { data: summary, isLoading: summaryLoading, error: summaryError, refetch: refetchSummary } = useAnalyticsSummary(period)
  const { data: trends, isLoading: trendsLoading } = usePomodoroTrends(period)
  const { data: distribution, isLoading: distributionLoading } = useTaskDistribution()

  const isLoading = summaryLoading || trendsLoading || distributionLoading

  const handleRefresh = () => {
    refetchSummary()
  }

  return (
    <AppShell
      title="Analytics"
      subtitle="Track your productivity trends and insights"
      actions={
        <div className="flex items-center gap-3">
          <LuxuryTimeRangeSelector value={period} onChange={setPeriod} />
          <Button variant="ghost" size="sm" onClick={handleRefresh}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      }
    >
      {summaryError ? (
        <div className="text-center py-12">
          <p className="text-red-400 mb-4">Failed to load analytics. Please try again.</p>
          <Button variant="secondary" onClick={handleRefresh}>
            Retry
          </Button>
        </div>
      ) : isLoading ? (
        <div className="text-center py-12 text-luxury-text-secondary">
          <RefreshCw className="w-8 h-8 mx-auto animate-spin mb-4" />
          <p>Loading analytics...</p>
        </div>
      ) : summary ? (
        <div className="space-y-8">
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <LuxuryMetricCard
              label="Pomodoros"
              value={summary.total_pomodoros}
              subtext={`${summary.average_pomodoros_per_day.toFixed(1)} avg/day`}
              glowColor="indigo"
            />
            <LuxuryMetricCard
              label="Focus Time"
              value={`${(Math.round(summary.total_focus_minutes / 60 * 10) / 10)}h`}
              subtext={`${summary.total_focus_minutes} minutes`}
              glowColor="cyan"
            />
            <LuxuryMetricCard
              label="Tasks Completed"
              value={summary.tasks_completed}
              subtext={`of ${summary.tasks_created} created`}
              glowColor="gold"
            />
            <LuxuryMetricCard
              label="Completion Rate"
              value={`${summary.task_completion_rate}%`}
              trend={{
                direction: summary.productivity_score.trend,
                value: summary.productivity_score.trend_percentage,
              }}
              glowColor="orange"
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 overflow-x-auto">
              <div className="min-w-[400px]">
                {trends && <LuxuryPomodoroChart data={trends.data_points} />}
              </div>
            </div>
            <div>
              <LuxuryProductivityScore score={summary.productivity_score} />
            </div>
          </div>

          {/* Task Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="overflow-x-auto">
              <div className="min-w-[350px]">
                {distribution && (
                  <LuxuryQuadrantChart data={distribution.quadrants} />
                )}
              </div>
            </div>
            <LuxuryDailyPlanStats stats={summary.daily_plan_stats} />
          </div>
        </div>
      ) : null}

      {/* Footer */}
      <footer className="mt-12 text-center text-luxury-text-secondary text-sm">
        <p>
          Showing data for {period === "day" ? "today" : `last ${period}`}
          {summary && ` (${summary.start_date} to ${summary.end_date})`}
        </p>
      </footer>
    </AppShell>
  )
}
