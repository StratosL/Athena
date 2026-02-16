/**
 * TanStack Query hooks for daily plan management.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  dailyPlansApi,
  type DailyPlan,
  type TaskAssignment,
} from "@/lib/api"

// Query keys
export const dailyPlanKeys = {
  all: ["dailyPlans"] as const,
  lists: () => [...dailyPlanKeys.all, "list"] as const,
  list: (filters?: { limit?: number; offset?: number }) =>
    [...dailyPlanKeys.lists(), filters] as const,
  details: () => [...dailyPlanKeys.all, "detail"] as const,
  detail: (id: string) => [...dailyPlanKeys.details(), id] as const,
  today: () => [...dailyPlanKeys.all, "today"] as const,
}

// Queries
export function useTodayPlan() {
  return useQuery({
    queryKey: dailyPlanKeys.today(),
    queryFn: () => dailyPlansApi.getToday(),
  })
}

export function useDailyPlan(id: string) {
  return useQuery({
    queryKey: dailyPlanKeys.detail(id),
    queryFn: () => dailyPlansApi.get(id),
    enabled: !!id,
  })
}

export function useDailyPlans(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: dailyPlanKeys.list(params),
    queryFn: () => dailyPlansApi.list(params),
  })
}

// Mutations
export function useCreateDailyPlan() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (date: string) => dailyPlansApi.create(date),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dailyPlanKeys.lists() })
    },
  })
}

export function useAssignTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      planId,
      assignment,
    }: {
      planId: string
      assignment: TaskAssignment
    }) => dailyPlansApi.assignTask(planId, assignment),
    onSuccess: (updatedPlan: DailyPlan) => {
      // Update the specific plan cache
      queryClient.setQueryData(dailyPlanKeys.detail(updatedPlan.id), updatedPlan)
      // Update today's plan if it matches
      queryClient.setQueryData(dailyPlanKeys.today(), (old: DailyPlan | undefined) => {
        if (old?.id === updatedPlan.id) {
          return updatedPlan
        }
        return old
      })
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: dailyPlanKeys.lists() })
    },
  })
}

export function useRemoveTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ planId, taskId }: { planId: string; taskId: string }) =>
      dailyPlansApi.removeTask(planId, taskId),
    onSuccess: (updatedPlan: DailyPlan) => {
      // Update the specific plan cache
      queryClient.setQueryData(dailyPlanKeys.detail(updatedPlan.id), updatedPlan)
      // Update today's plan if it matches
      queryClient.setQueryData(dailyPlanKeys.today(), (old: DailyPlan | undefined) => {
        if (old?.id === updatedPlan.id) {
          return updatedPlan
        }
        return old
      })
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: dailyPlanKeys.lists() })
    },
  })
}
