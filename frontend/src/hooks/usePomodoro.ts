/**
 * TanStack Query hooks for pomodoro timer.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { pomodoroApi } from "@/lib/api"
import { taskKeys } from "./useTasks"

// Query keys
export const pomodoroKeys = {
  all: ["pomodoro"] as const,
  active: () => [...pomodoroKeys.all, "active"] as const,
  sessions: () => [...pomodoroKeys.all, "sessions"] as const,
  sessionsByTask: (taskId: string) => [...pomodoroKeys.sessions(), taskId] as const,
  session: (id: string) => [...pomodoroKeys.sessions(), "detail", id] as const,
}

// Queries
export function useActiveTimer(options?: { refetchInterval?: number }) {
  return useQuery({
    queryKey: pomodoroKeys.active(),
    queryFn: () => pomodoroApi.getActive(),
    // Refetch every second when timer is active
    refetchInterval: options?.refetchInterval,
  })
}

export function usePomodoroSessions(taskId?: string, limit?: number) {
  return useQuery({
    queryKey: taskId ? pomodoroKeys.sessionsByTask(taskId) : pomodoroKeys.sessions(),
    queryFn: () => pomodoroApi.listSessions(taskId, limit),
  })
}

export function usePomodoroSession(id: string) {
  return useQuery({
    queryKey: pomodoroKeys.session(id),
    queryFn: () => pomodoroApi.getSession(id),
    enabled: !!id,
  })
}

// Mutations
export function useStartSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (taskId?: string) => pomodoroApi.start(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pomodoroKeys.active() })
      queryClient.invalidateQueries({ queryKey: pomodoroKeys.sessions() })
    },
  })
}

export function useStopSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => pomodoroApi.stop(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pomodoroKeys.active() })
      queryClient.invalidateQueries({ queryKey: pomodoroKeys.sessions() })
    },
  })
}

export function useCompleteSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => pomodoroApi.complete(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pomodoroKeys.active() })
      queryClient.invalidateQueries({ queryKey: pomodoroKeys.sessions() })
      // Also invalidate tasks to update pomodoro_count
      queryClient.invalidateQueries({ queryKey: taskKeys.all })
    },
  })
}
