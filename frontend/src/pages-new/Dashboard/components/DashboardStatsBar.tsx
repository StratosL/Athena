import { useEffect, useMemo } from "react"
import { cn } from "@/lib/utils"
import { GlassCard, Button } from "@/design-system/components"
import { useTimerStore } from "@/stores/timerStore"
import { useActiveTimer, useStartSession, useStopSession, useCompleteSession } from "@/hooks/usePomodoro"
import { usePomodoroWebSocket } from "@/hooks/usePomodoroWebSocket"
import { useAnalyticsSummary } from "@/hooks/useAnalytics"

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

function StatItem({
  label,
  value,
  unit,
  color,
}: {
  label: string
  value: string | number
  unit?: string
  color: string
}) {
  return (
    <div className="flex flex-col items-center gap-1">
      <p className={cn("text-2xl font-bold font-inter", color)}>
        {value}
        {unit && <span className="text-sm font-normal ml-0.5">{unit}</span>}
      </p>
      <p className="text-sm text-luxury-text-secondary">{label}</p>
    </div>
  )
}

export function DashboardStatsBar() {
  const {
    state,
    remainingSeconds,
    sessionId,
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

  const totalSeconds = activeTimer?.session
    ? activeTimer.session.duration_minutes * 60
    : workDurationSeconds
  const displaySeconds = state === "IDLE" ? workDurationSeconds : remainingSeconds
  const elapsed = totalSeconds - displaySeconds
  const percentage = state === "IDLE" ? 0 : (elapsed / totalSeconds) * 100
  const isActive = state !== "IDLE"
  const isTimerLoading = startSession.isPending || stopSession.isPending || completeSession.isPending

  // Analytics stats
  const { data: summary, isLoading: isStatsLoading } = useAnalyticsSummary("day")
  const focusHours = Math.round(((summary?.total_focus_minutes ?? 0) / 60) * 10) / 10

  return (
    <GlassCard className="p-4" hoverable={false}>
      {/* Timer row */}
      <div className="flex items-center gap-4">
        <p className={cn(
          "text-base font-medium min-w-[5rem]",
          state === "WORK" ? "text-luxury-indigo" :
          state === "SHORT_BREAK" || state === "LONG_BREAK" ? "text-luxury-gold" :
          "text-luxury-text-secondary"
        )}>
          {stateLabels[state]}
        </p>

        <p className="text-2xl font-bold font-inter text-luxury-text-primary tabular-nums">
          {formatTime(displaySeconds)}
        </p>

        {/* Progress bar */}
        <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-500",
              state === "WORK" ? "bg-luxury-indigo" : "bg-luxury-gold"
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {!isActive ? (
          <Button variant="primary" size="sm" onClick={handleStart} loading={isTimerLoading}>
            Start Focus
          </Button>
        ) : (
          <Button variant="danger" size="sm" onClick={handleStop} loading={isTimerLoading}>
            Stop
          </Button>
        )}
      </div>

      {/* Divider */}
      <div className="border-t border-luxury-border my-3" />

      {/* Stats grid */}
      {isStatsLoading ? (
        <p className="text-sm text-luxury-text-secondary text-center">Loading stats...</p>
      ) : (
        <div className="grid grid-cols-4 gap-4">
          <StatItem
            label="Pomodoros"
            value={summary?.total_pomodoros ?? 0}
            color="text-luxury-indigo"
          />
          <StatItem
            label="Focus Time"
            value={focusHours}
            unit="h"
            color="text-luxury-cyan"
          />
          <StatItem
            label="Tasks Done"
            value={summary?.tasks_completed ?? 0}
            color="text-luxury-gold"
          />
          <StatItem
            label="Completion"
            value={summary?.task_completion_rate ?? 0}
            unit="%"
            color="text-luxury-orange"
          />
        </div>
      )}
    </GlassCard>
  )
}
