import { useEffect } from "react"
import { cn } from "@/lib/utils"
import { GlassCard } from "../../base/GlassCard"
import { Button } from "../../base/Button"
import { ProgressRing } from "../ProgressRing"
import { useTimerStore } from "@/stores/timerStore"
import { useActiveTimer, useStartSession, useStopSession, useCompleteSession } from "@/hooks/usePomodoro"
import { usePomodoroWebSocket } from "@/hooks/usePomodoroWebSocket"
import type { PomodoroWidgetProps } from "./PomodoroWidget.types"

const WORK_DURATION_SECONDS = 25 * 60

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

export function PomodoroWidget({ className }: PomodoroWidgetProps) {
  const {
    state,
    remainingSeconds,
    sessionId,
    pomodoroCount,
    setState,
    setRemainingSeconds,
    setSession,
  } = useTimerStore()

  const { data: activeTimer, refetch } = useActiveTimer({
    refetchInterval: state !== "IDLE" ? 1000 : undefined,
  })
  const startSession = useStartSession()
  const stopSession = useStopSession()
  const completeSession = useCompleteSession()
  const { isConnected, isConnecting, connect, disconnect } = usePomodoroWebSocket()

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
    startSession.mutate(undefined, {
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

  const displaySeconds = state === "IDLE" ? WORK_DURATION_SECONDS : remainingSeconds
  const elapsed = WORK_DURATION_SECONDS - displaySeconds
  const percentage = state === "IDLE" ? 0 : (elapsed / WORK_DURATION_SECONDS) * 100
  const isActive = state !== "IDLE"
  const isLoading = startSession.isPending || stopSession.isPending || completeSession.isPending

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
