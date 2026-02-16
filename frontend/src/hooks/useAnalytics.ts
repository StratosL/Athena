/**
 * TanStack Query hooks for analytics data.
 */

import { useQuery } from "@tanstack/react-query"
import { analyticsApi, TimeRange } from "@/lib/api"

// Query keys
export const analyticsKeys = {
  all: ["analytics"] as const,
  summary: (period: TimeRange) => [...analyticsKeys.all, "summary", period] as const,
  pomodoroTrends: (period: TimeRange) => [...analyticsKeys.all, "pomodoro-trends", period] as const,
  taskDistribution: () => [...analyticsKeys.all, "task-distribution"] as const,
}

/**
 * Hook for fetching analytics summary.
 */
export function useAnalyticsSummary(period: TimeRange = "week") {
  return useQuery({
    queryKey: analyticsKeys.summary(period),
    queryFn: () => analyticsApi.getSummary(period),
    staleTime: 1000 * 60, // 1 minute
  })
}

/**
 * Hook for fetching pomodoro trends.
 */
export function usePomodoroTrends(period: TimeRange = "week") {
  return useQuery({
    queryKey: analyticsKeys.pomodoroTrends(period),
    queryFn: () => analyticsApi.getPomodoroTrends(period),
    staleTime: 1000 * 60,
  })
}

/**
 * Hook for fetching task distribution.
 */
export function useTaskDistribution() {
  return useQuery({
    queryKey: analyticsKeys.taskDistribution(),
    queryFn: () => analyticsApi.getTaskDistribution(),
    staleTime: 1000 * 60,
  })
}
