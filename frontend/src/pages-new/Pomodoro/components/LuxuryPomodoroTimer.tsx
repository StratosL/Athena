import { useEffect, useMemo } from "react"
import { cn } from "@/lib/utils"
import { ProgressRing } from "@/design-system/components"
import { celebrateSessionComplete } from "@/design-system/animations/confetti"
import { useTimerStore } from "@/stores/timerStore"
import { useActiveTimer, useStartSession, useStopSession, useCompleteSession } from "@/hooks/usePomodoro"
import { usePomodoroWebSocket } from "@/hooks/usePomodoroWebSocket"

interface LuxuryPomodoroTimerProps {
  taskId?: string
  taskTitle?: string
  className?: string
}

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
  IDLE: "Ready to Focus",
  WORK: "Deep Focus",
  SHORT_BREAK: "Short Break",
  LONG_BREAK: "Long Break",
} as const

export function LuxuryPomodoroTimer({ taskId, taskTitle, className }: LuxuryPomodoroTimerProps) {
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

  const { isConnected, isConnecting, error, connect, disconnect } =
    usePomodoroWebSocket()

  // Only poll HTTP when WebSocket is not connected (fallback)
  const { data: activeTimer, refetch } = useActiveTimer({
    refetchInterval: state !== "IDLE" && !isConnected ? 1000 : undefined,
  })

  // Sync with server state on initial load and refetch
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
      } else {
        if (sessionId) {
          setSession(null, null)
          setState("IDLE")
          setRemainingSeconds(0)
        }
      }
    }
  }, [
    activeTimer,
    sessionId,
    isConnected,
    isConnecting,
    connect,
    setSession,
    setState,
    setRemainingSeconds,
  ])

  // Auto-complete when timer reaches zero
  useEffect(() => {
    if (state === "WORK" && remainingSeconds === 0 && sessionId) {
      completeSession.mutate(undefined, {
        onSuccess: () => {
          celebrateSessionComplete()
          refetch()
        },
      })
    }
  }, [state, remainingSeconds, sessionId, completeSession, refetch])

  const handleStart = () => {
    startSession.mutate({ taskId, durationMinutes: workDuration }, {
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

  const handleReconnect = () => {
    if (sessionId) {
      connect(sessionId)
    }
  }

  const isLoading = startSession.isPending || stopSession.isPending || completeSession.isPending
  const isActive = state !== "IDLE"
  // Use the active session's duration for progress, fall back to settings for IDLE display
  const totalSeconds = activeTimer?.session
    ? activeTimer.session.duration_minutes * 60
    : workDurationSeconds
  const displaySeconds = state === "IDLE" ? workDurationSeconds : remainingSeconds
  const elapsed = totalSeconds - displaySeconds
  const percentage = state === "IDLE" ? 0 : (elapsed / totalSeconds) * 100

  const glowClass =
    state === "WORK"
      ? "shadow-glow-luxury-indigo"
      : state === "SHORT_BREAK" || state === "LONG_BREAK"
        ? "shadow-glow-gold"
        : ""

  return (
    <div className={cn("flex flex-col items-center", className)}>
      {/* Title */}
      <h2 className="text-2xl font-playfair font-bold text-luxury-text-primary mb-2">
        {taskTitle || "Pomodoro Timer"}
      </h2>

      {/* Connection Status */}
      {isActive && (
        <div className="flex items-center gap-2 mb-6">
          <div className={cn(
            "w-2 h-2 rounded-full",
            isConnected ? "bg-green-400" : isConnecting ? "bg-yellow-400 animate-pulse" : "bg-red-400"
          )} />
          <span className="text-xs text-luxury-text-secondary">
            {isConnected ? "Connected" : isConnecting ? "Connecting..." : "Disconnected"}
          </span>
          {!isConnected && !isConnecting && error && (
            <button
              onClick={handleReconnect}
              className="text-xs text-luxury-indigo hover:underline"
            >
              Retry
            </button>
          )}
        </div>
      )}

      {/* Timer Ring */}
      <div className={cn(
        "rounded-full transition-shadow duration-500",
        isActive && glowClass
      )}>
        <ProgressRing percentage={percentage} size={360} strokeWidth={12} active={isActive}>
          <div className="text-center">
            <p className="text-6xl font-bold font-inter text-luxury-text-primary tracking-tight">
              {formatTime(displaySeconds)}
            </p>
            <p className={cn(
              "text-sm mt-2 font-medium",
              state === "WORK" ? "text-luxury-indigo" :
              state === "SHORT_BREAK" || state === "LONG_BREAK" ? "text-luxury-gold" :
              "text-luxury-text-secondary"
            )}>
              {stateLabels[state]}
            </p>
          </div>
        </ProgressRing>
      </div>

      {/* Session Progress Dots */}
      {pomodoroCount > 0 && (
        <div className="flex gap-2 mt-6">
          {Array.from({ length: Math.min(pomodoroCount, 8) }).map((_, i) => (
            <div key={i} className="w-3 h-3 rounded-full bg-luxury-gold shadow-glow-gold" />
          ))}
          {pomodoroCount > 8 && (
            <span className="text-xs text-luxury-text-secondary ml-1">+{pomodoroCount - 8}</span>
          )}
        </div>
      )}

      {/* Controls */}
      <div className="flex gap-4 mt-8">
        {!isActive ? (
          <button
            onClick={handleStart}
            disabled={isLoading}
            className={cn(
              "px-8 py-3 rounded-xl font-semibold text-lg transition-all duration-300",
              "bg-gradient-to-r from-luxury-indigo to-luxury-gold text-white",
              "shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]",
              isLoading && "opacity-50 cursor-not-allowed"
            )}
          >
            {isLoading ? "Starting..." : "Start Focus"}
          </button>
        ) : (
          <button
            onClick={handleStop}
            disabled={isLoading}
            className={cn(
              "px-8 py-3 rounded-xl font-semibold text-lg transition-all duration-300",
              "bg-red-600 text-white shadow-lg hover:bg-red-700",
              "hover:scale-[1.02] active:scale-[0.98]",
              isLoading && "opacity-50 cursor-not-allowed"
            )}
          >
            {isLoading ? "Stopping..." : "Stop"}
          </button>
        )}
      </div>
    </div>
  )
}
