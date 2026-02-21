/**
 * TanStack Query hooks for task management.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { tasksApi, type CreateTaskData, type Task, type UpdateTaskData } from "@/lib/api"
import { dailyPlanKeys } from "@/hooks/useDailyPlan"

// Query keys
export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const,
  list: (filters: { quadrant?: number; status?: string }) =>
    [...taskKeys.lists(), filters] as const,
  details: () => [...taskKeys.all, "detail"] as const,
  detail: (id: string) => [...taskKeys.details(), id] as const,
}

// Queries
export function useTasks(filters?: { quadrant?: number; status?: string }) {
  return useQuery({
    queryKey: taskKeys.list(filters || {}),
    queryFn: () => tasksApi.list(filters),
  })
}

export function useTask(id: string) {
  return useQuery({
    queryKey: taskKeys.detail(id),
    queryFn: () => tasksApi.get(id),
    enabled: !!id,
  })
}

// Mutations
export function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateTaskData) => tasksApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() })
    },
  })
}

export function useUpdateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateTaskData }) =>
      tasksApi.update(id, data),
    onSuccess: (updatedTask: Task) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() })
      queryClient.setQueryData(taskKeys.detail(updatedTask.id), updatedTask)
    },
  })
}

export function useDeleteTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => tasksApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() })
    },
  })
}

export function useCompleteTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => tasksApi.complete(id),
    onSuccess: (updatedTask: Task) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() })
      queryClient.invalidateQueries({ queryKey: dailyPlanKeys.all })
      queryClient.setQueryData(taskKeys.detail(updatedTask.id), updatedTask)
    },
  })
}
