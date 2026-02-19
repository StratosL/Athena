import { useEffect, useMemo } from "react"
import { cn } from "@/lib/utils"
import { GlassCard } from "../../base/GlassCard"
import { Button } from "../../base/Button"
import { ProgressRing } from "../ProgressRing"
import { useTimerStore } from "@/stores/timerStore"
import { useActiveTimer, useStartSession, useStopSession, useCompleteSession } from "@/hooks/usePomodoro"
import { usePomodoroWebSocket } from "@/hooks/usePomodoroWebSocket"
import type { PomodoroWidgetProps } from "./PomodoroWidget.types"

function getPomodoroSettings() {
  try {
    const raw = localStorage.getItem("artemis-settings")
    if (raw) {
      const s = JSON.parse(raw)
      return { workDuration: s.pomodoroWorkDuration ?? 25 }
    }
  } catch { /* ignore */ }
  return { workDuration: 25 }
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
}

const stateLabels = {
  IDLE: "Ready",
  WORK: "Focus",
  SHORT_BREAK: "Short Break",
  LONG_BREAK: "Long Break",
} as const

export function PomodoroWidget({ className, compact }: PomodoroWidgetProps) {
  const {
    state,
    remainingSeconds,
    sessionId,
    pomodoroCount,
    setState,
    setRemainingSeconds,
    setSession,
  } = useTimerStore()

  const { workDuration } = useMemo(() => getPomodoroSettings(), [])
  const workDurationSeconds = workDuration * 60

  const startSession = useStartSession()
  const stopSession = useStopSession()
  const completeSession = useCompleteSession()
  const { isConnected, isConnecting, connect, disconnect } = usePomodoroWebSocket()

  // Only poll HTTP when WebSocket is not connected (fallback)
  const { data: activeTimer, refetch } = useActiveTimer({
    refetchInterval: state !== "IDLE" && !isConnected ? 1000 : undefined,
  })

  // Sync with server state
  useEffect(() => {
    if (activeTimer) {
      if (activeTimer.session) {
        const isDifferentSession = activeTimer.session.id !== sessionId
        if (isDifferentSession) {
          setSession(activeTimer.session.id, activeTimer.session.task_id)
          setState(activeTimer.state)
          setRemainingSeconds(activeTimer.remaining_seconds)
          if (!isConnected && !isConnecting) {
            connect(activeTimer.session.id)
          }
        } else {
          setState(activeTimer.state)
          setRemainingSeconds(activeTimer.remaining_seconds)
        }
      } else if (sessionId) {
        setSession(null, null)
        setState("IDLE")
        setRemainingSeconds(0)
      }
    }
  }, [activeTimer, sessionId, isConnected, isConnecting, connect, setSession, setState, setRemainingSeconds])

  // Auto-complete
  useEffect(() => {
    if (state === "WORK" && remainingSeconds === 0 && sessionId) {
      completeSession.mutate(undefined, {
        onSuccess: () => refetch(),
      })
    }
  }, [state, remainingSeconds, sessionId, completeSession, refetch])

  const handleStart = () => {
    startSession.mutate({ durationMinutes: workDuration }, {
      onSuccess: (session) => {
        setSession(session.id, session.task_id)
        setState("WORK")
        setRemainingSeconds(session.duration_minutes * 60)
        connect(session.id)
      },
    })
  }

  const handleStop = () => {
    stopSession.mutate(undefined, {
      onSuccess: () => {
        disconnect()
        setSession(null, null)
        setState("IDLE")
        setRemainingSeconds(0)
        setTimeout(() => refetch(), 500)
      },
    })
  }

  // Use the active session's duration for progress, fall back to settings for IDLE display
  const totalSeconds = activeTimer?.session
    ? activeTimer.session.duration_minutes * 60
    : workDurationSeconds
  const displaySeconds = state === "IDLE" ? workDurationSeconds : remainingSeconds
  const elapsed = totalSeconds - displaySeconds
  const percentage = state === "IDLE" ? 0 : (elapsed / totalSeconds) * 100
  const isActive = state !== "IDLE"
  const isLoading = startSession.isPending || stopSession.isPending || completeSession.isPending

  if (compact) {
    return (
      <GlassCard className={cn("p-4 flex flex-col items-center", className)} hoverable={false}>
        <h3 className="font-playfair font-semibold text-luxury-text-primary text-sm mb-2">
          Pomodoro Timer
        </h3>

        <p className={cn(
          "text-xs mb-2",
          state === "WORK" ? "text-luxury-indigo" :
          state === "SHORT_BREAK" || state === "LONG_BREAK" ? "text-luxury-gold" :
          "text-luxury-text-secondary"
        )}>
          {stateLabels[state]}
        </p>

        <p className="text-2xl font-bold font-inter text-luxury-text-primary mb-3">
          {formatTime(displaySeconds)}
        </p>

        {/* Horizontal progress bar */}
        <div className="w-full h-1.5 bg-white/5 rounded-full mb-3 overflow-hidden">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-500",
              state === "WORK" ? "bg-luxury-indigo" : "bg-luxury-gold"
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>

        <div className="flex gap-3 mb-2">
          {!isActive ? (
            <Button variant="primary" size="sm" onClick={handleStart} loading={isLoading}>
              Start Focus
            </Button>
          ) : (
            <Button variant="danger" size="sm" onClick={handleStop} loading={isLoading}>
              Stop
            </Button>
          )}
        </div>

        {pomodoroCount > 0 && (
          <p className="text-xs text-luxury-text-secondary">
            {pomodoroCount} session{pomodoroCount !== 1 ? "s" : ""} today
          </p>
        )}
      </GlassCard>
    )
  }

  return (
    <GlassCard className={cn("p-6 flex flex-col items-center", className)} hoverable={false}>
      <h3 className="font-playfair font-semibold text-luxury-text-primary mb-4">
        Pomodoro Timer
      </h3>

      <ProgressRing percentage={percentage} size={180} strokeWidth={8} active={isActive}>
        <div className="text-center">
          <p className="text-3xl font-bold font-inter text-luxury-text-primary">
            {formatTime(displaySeconds)}
          </p>
          <p className={cn(
            "text-xs mt-1",
            state === "WORK" ? "text-luxury-indigo" :
            state === "SHORT_BREAK" || state === "LONG_BREAK" ? "text-luxury-gold" :
            "text-luxury-text-secondary"
          )}>
            {stateLabels[state]}
          </p>
        </div>
      </ProgressRing>

      <div className="flex gap-3 mt-4">
        {!isActive ? (
          <Button variant="primary" size="sm" onClick={handleStart} loading={isLoading}>
            Start Focus
          </Button>
        ) : (
          <Button variant="danger" size="sm" onClick={handleStop} loading={isLoading}>
            Stop
          </Button>
        )}
      </div>

      {pomodoroCount > 0 && (
        <p className="text-xs text-luxury-text-secondary mt-3">
          {pomodoroCount} session{pomodoroCount !== 1 ? "s" : ""} today
        </p>
      )}
    </GlassCard>
  )
}

export default PomodoroWidget
export type { PomodoroWidgetProps } from "./PomodoroWidget.types"
