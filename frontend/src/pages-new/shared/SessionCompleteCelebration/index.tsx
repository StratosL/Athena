/**
 * SessionCompleteCelebration Component
 *
 * Full-screen glassmorphism overlay shown when a Pomodoro session completes.
 * Shows session stats, achievement streak, and auto-dismisses after 10 seconds.
 * Gold confetti fires on mount.
 */

import { useEffect, useState, useRef, useCallback } from "react"
import { motion, AnimatePresence } from "motion/react"
import { GlassCard, Button, Badge } from "@/design-system/components"
import { celebrateSessionComplete } from "@/design-system/animations/confetti"
import { useTimerStore } from "@/stores/timerStore"
import { cn } from "@/lib/utils"

interface SessionCompleteCelebrationProps {
  isOpen: boolean
  onClose: () => void
  sessionDuration: number
  taskTitle?: string
}

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (minutes === 0) return `${remainingSeconds}s`
  return `${minutes}m ${remainingSeconds}s`
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}

const AUTO_DISMISS_DURATION = 10000

export function SessionCompleteCelebration({
  isOpen,
  onClose,
  sessionDuration,
  taskTitle,
}: SessionCompleteCelebrationProps) {
  const [progress, setProgress] = useState(0)
  const [completedAt] = useState(() => new Date())
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const startTimeRef = useRef<number>(0)
  const pomodoroCount = useTimerStore((s) => s.pomodoroCount)

  const handleClose = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    onClose()
  }, [onClose])

  // Fire confetti on mount
  useEffect(() => {
    if (isOpen) {
      celebrateSessionComplete()
    }
  }, [isOpen])

  // Auto-dismiss timer with progress
  useEffect(() => {
    if (!isOpen) {
      setProgress(0)
      return
    }

    startTimeRef.current = Date.now()

    timerRef.current = setInterval(() => {
      const elapsed = Date.now() - startTimeRef.current
      const newProgress = Math.min((elapsed / AUTO_DISMISS_DURATION) * 100, 100)
      setProgress(newProgress)

      if (elapsed >= AUTO_DISMISS_DURATION) {
        handleClose()
      }
    }, 50)

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [isOpen, handleClose])

  const streakLabel =
    pomodoroCount <= 1
      ? "First Session"
      : pomodoroCount <= 3
        ? "Getting Started"
        : pomodoroCount <= 6
          ? "On a Roll"
          : pomodoroCount <= 10
            ? "Focus Master"
            : "Unstoppable"

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/60 backdrop-blur-md" />

          {/* Content */}
          <motion.div
            className="relative w-full max-w-md mx-4"
            initial={{ opacity: 0, scale: 0.9, y: 30 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 30 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
          >
            <GlassCard hoverable={false} className="p-8 text-center">
              {/* Trophy Icon */}
              <motion.div
                className="mb-4"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{
                  delay: 0.2,
                  type: "spring",
                  stiffness: 200,
                  damping: 12,
                }}
              >
                <div className="w-16 h-16 mx-auto rounded-full bg-luxury-gold/20 flex items-center justify-center shadow-[0_0_30px_rgba(212,175,55,0.3)]">
                  <svg
                    width="32"
                    height="32"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                      fill="#d4af37"
                      stroke="#d4af37"
                      strokeWidth="1"
                    />
                  </svg>
                </div>
              </motion.div>

              {/* Title */}
              <h2 className="font-playfair text-3xl font-semibold text-luxury-text-primary mb-2">
                Session Complete
              </h2>
              <p className="text-luxury-text-secondary font-inter mb-6">
                Great work! You stayed focused and earned this break.
              </p>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-3 mb-6">
                {/* Duration */}
                <GlassCard hoverable={false} className="p-4">
                  <p className="text-xs text-luxury-text-secondary font-inter uppercase tracking-wider mb-1">
                    Duration
                  </p>
                  <p className="text-xl font-semibold text-luxury-text-primary font-inter">
                    {formatDuration(sessionDuration)}
                  </p>
                </GlassCard>

                {/* Time Completed */}
                <GlassCard hoverable={false} className="p-4">
                  <p className="text-xs text-luxury-text-secondary font-inter uppercase tracking-wider mb-1">
                    Completed At
                  </p>
                  <p className="text-xl font-semibold text-luxury-text-primary font-inter">
                    {formatTime(completedAt)}
                  </p>
                </GlassCard>

                {/* Linked Task */}
                {taskTitle && (
                  <GlassCard hoverable={false} className="p-4 col-span-2">
                    <p className="text-xs text-luxury-text-secondary font-inter uppercase tracking-wider mb-1">
                      Linked Task
                    </p>
                    <p className="text-sm font-medium text-luxury-text-primary font-inter truncate">
                      {taskTitle}
                    </p>
                  </GlassCard>
                )}

                {/* Pomodoro Count */}
                <GlassCard
                  hoverable={false}
                  className={cn("p-4", taskTitle ? "" : "col-span-2")}
                >
                  <p className="text-xs text-luxury-text-secondary font-inter uppercase tracking-wider mb-1">
                    Pomodoros Today
                  </p>
                  <p className="text-xl font-semibold text-luxury-gold font-inter">
                    {pomodoroCount}
                  </p>
                </GlassCard>
              </div>

              {/* Achievement */}
              <div className="mb-6">
                <p className="text-xs text-luxury-text-secondary font-inter uppercase tracking-wider mb-2">
                  Achievement
                </p>
                <Badge variant="gold">
                  {streakLabel} - {pomodoroCount} session
                  {pomodoroCount !== 1 ? "s" : ""}
                </Badge>
              </div>

              {/* Continue Button */}
              <Button variant="primary" size="lg" onClick={handleClose} className="w-full mb-4">
                Continue
              </Button>

              {/* Auto-dismiss progress bar */}
              <div className="w-full h-1 rounded-full bg-luxury-border overflow-hidden">
                <motion.div
                  className="h-full bg-luxury-gold rounded-full"
                  style={{ width: `${progress}%` }}
                  transition={{ duration: 0.05 }}
                />
              </div>
              <p className="text-xs text-luxury-text-secondary mt-1 font-inter">
                Auto-dismissing in{" "}
                {Math.ceil((AUTO_DISMISS_DURATION - (progress / 100) * AUTO_DISMISS_DURATION) / 1000)}s
              </p>
            </GlassCard>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default SessionCompleteCelebration
