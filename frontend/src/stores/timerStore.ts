/**
 * Zustand store for client-side timer state.
 */

import { create } from "zustand"
import type { TimerState } from "@/lib/api"

interface TimerStore {
  // State
  state: TimerState
  remainingSeconds: number
  sessionId: string | null
  taskId: string | null
  pomodoroCount: number
  isConnected: boolean

  // Actions
  setState: (state: TimerState) => void
  setRemainingSeconds: (seconds: number) => void
  setSession: (sessionId: string | null, taskId: string | null) => void
  incrementPomodoro: () => void
  setConnected: (connected: boolean) => void
  reset: () => void
}

const initialState = {
  state: "IDLE" as TimerState,
  remainingSeconds: 0,
  sessionId: null,
  taskId: null,
  pomodoroCount: 0,
  isConnected: false,
}

export const useTimerStore = create<TimerStore>((set) => ({
  ...initialState,

  setState: (state) => set({ state }),

  setRemainingSeconds: (seconds) => set({ remainingSeconds: seconds }),

  setSession: (sessionId, taskId) => set({ sessionId, taskId }),

  incrementPomodoro: () =>
    set((prev) => ({ pomodoroCount: prev.pomodoroCount + 1 })),

  setConnected: (connected) => set({ isConnected: connected }),

  reset: () => set(initialState),
}))
