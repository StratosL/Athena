/**
 * DailyReflection Screen
 *
 * End-of-day reflection page with star rating, stats summary,
 * journal textarea, and carry-forward incomplete tasks.
 * Saves reflection data to localStorage keyed by date.
 *
 * Route: /reflection
 */

import { useState, useEffect, useCallback, useMemo } from "react"
import { motion } from "motion/react"
import { GlassCard, Button, Badge } from "@/design-system/components"
import { glassmorphismClasses } from "@/design-system"
import { useAnalyticsSummary } from "@/hooks/useAnalytics"
import { useTodayPlan } from "@/hooks/useDailyPlan"
import { AppShell } from "../layout"
import { cn } from "@/lib/utils"
import type { TaskInfo } from "@/lib/api"

// ---- StarRating Component (inline) ----

interface StarRatingProps {
  value: number
  onChange: (rating: number) => void
}

function StarRating({ value, onChange }: StarRatingProps) {
  const [hoveredStar, setHoveredStar] = useState<number | null>(null)

  return (
    <div className="flex gap-1.5">
      {[1, 2, 3, 4, 5].map((star) => {
        const isActive = star <= (hoveredStar ?? value)
        return (
          <motion.button
            key={star}
            className="p-0.5 focus:outline-none"
            onClick={() => onChange(star)}
            onMouseEnter={() => setHoveredStar(star)}
            onMouseLeave={() => setHoveredStar(null)}
            whileHover={{ scale: 1.15 }}
            whileTap={{ scale: 0.9 }}
            aria-label={`Rate ${star} star${star !== 1 ? "s" : ""}`}
          >
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill={isActive ? "#d4af37" : "none"}
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                stroke={isActive ? "#d4af37" : "rgba(255,255,255,0.2)"}
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            {isActive && (
              <div className="absolute inset-0 rounded-full pointer-events-none shadow-[0_0_12px_rgba(212,175,55,0.4)]" />
            )}
          </motion.button>
        )
      })}
    </div>
  )
}

// ---- Reflection Data Shape ----

interface ReflectionData {
  date: string
  rating: number
  journal: string
  savedAt: string
}

function getStorageKey(date: string): string {
  return `artemis-reflection-${date}`
}

function getTodayDateString(): string {
  return new Date().toISOString().split("T")[0]
}

function loadReflection(date: string): ReflectionData | null {
  try {
    const raw = localStorage.getItem(getStorageKey(date))
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function saveReflection(data: ReflectionData): void {
  localStorage.setItem(getStorageKey(data.date), JSON.stringify(data))
}

// ---- Quadrant badge variant mapping ----

function quadrantVariant(quadrant: number): "q1" | "q2" | "q3" | "q4" {
  const map: Record<number, "q1" | "q2" | "q3" | "q4"> = {
    1: "q1",
    2: "q2",
    3: "q3",
    4: "q4",
  }
  return map[quadrant] ?? "q4"
}

// ---- Main Component ----

export function DailyReflection() {
  const today = useMemo(() => getTodayDateString(), [])

  const [rating, setRating] = useState(0)
  const [journal, setJournal] = useState("")
  const [isSaved, setIsSaved] = useState(false)

  const { data: summary, isLoading: summaryLoading } = useAnalyticsSummary("day")
  const { data: todayPlan, isLoading: planLoading } = useTodayPlan()

  // Load existing reflection on mount
  useEffect(() => {
    const existing = loadReflection(today)
    if (existing) {
      setRating(existing.rating)
      setJournal(existing.journal)
    }
  }, [today])

  const handleSave = useCallback(() => {
    saveReflection({
      date: today,
      rating,
      journal,
      savedAt: new Date().toISOString(),
    })
    setIsSaved(true)

    // Reset saved indicator after a moment
    setTimeout(() => setIsSaved(false), 2000)
  }, [today, rating, journal])

  // Incomplete tasks from today's plan
  const incompleteTasks: TaskInfo[] = useMemo(() => {
    if (!todayPlan) return []
    const allTasks: TaskInfo[] = [
      ...(todayPlan.major_task ? [todayPlan.major_task] : []),
      ...todayPlan.medium_tasks,
      ...todayPlan.small_tasks,
    ]
    return allTasks.filter((t) => t.status !== "completed")
  }, [todayPlan])

  return (
    <AppShell
      title="Daily Reflection"
      subtitle={`Reflect on your day - ${new Date().toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
      })}`}
    >
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Star Rating Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <GlassCard hoverable={false} className="p-6">
            <h3 className="font-playfair text-xl font-semibold text-luxury-text-primary mb-2">
              How was your day?
            </h3>
            <p className="text-sm text-luxury-text-secondary font-inter mb-4">
              Rate your overall productivity and satisfaction
            </p>
            <StarRating value={rating} onChange={setRating} />
            {rating > 0 && (
              <motion.p
                className="mt-2 text-sm text-luxury-gold font-inter"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                {rating <= 2
                  ? "Tomorrow is a fresh start. Rest well."
                  : rating <= 3
                    ? "A solid day. Room to grow."
                    : rating <= 4
                      ? "Great work today! Keep the momentum."
                      : "Outstanding! You crushed it today."}
              </motion.p>
            )}
          </GlassCard>
        </motion.div>

        {/* Stats Summary Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <GlassCard hoverable={false} className="p-6">
            <h3 className="font-playfair text-xl font-semibold text-luxury-text-primary mb-4">
              Today's Metrics
            </h3>
            {summaryLoading ? (
              <p className="text-sm text-luxury-text-secondary font-inter">
                Loading statistics...
              </p>
            ) : summary ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <GlassCard hoverable={false} className="p-3 text-center">
                  <p className="text-xs text-luxury-text-secondary font-inter uppercase tracking-wider mb-1">
                    Pomodoros
                  </p>
                  <p className="text-2xl font-semibold text-luxury-indigo font-inter">
                    {summary.total_pomodoros}
                  </p>
                </GlassCard>

                <GlassCard hoverable={false} className="p-3 text-center">
                  <p className="text-xs text-luxury-text-secondary font-inter uppercase tracking-wider mb-1">
                    Focus Time
                  </p>
                  <p className="text-2xl font-semibold text-luxury-cyan font-inter">
                    {summary.total_focus_minutes}m
                  </p>
                </GlassCard>

                <GlassCard hoverable={false} className="p-3 text-center">
                  <p className="text-xs text-luxury-text-secondary font-inter uppercase tracking-wider mb-1">
                    Tasks Done
                  </p>
                  <p className="text-2xl font-semibold text-luxury-gold font-inter">
                    {summary.tasks_completed}
                  </p>
                </GlassCard>

                <GlassCard hoverable={false} className="p-3 text-center">
                  <p className="text-xs text-luxury-text-secondary font-inter uppercase tracking-wider mb-1">
                    Completion
                  </p>
                  <p className="text-2xl font-semibold text-luxury-orange font-inter">
                    {Math.round(summary.task_completion_rate)}%
                  </p>
                </GlassCard>
              </div>
            ) : (
              <p className="text-sm text-luxury-text-secondary font-inter">
                No data available for today
              </p>
            )}
          </GlassCard>
        </motion.div>

        {/* Journal Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <GlassCard hoverable={false} className="p-6">
            <h3 className="font-playfair text-xl font-semibold text-luxury-text-primary mb-2">
              Journal
            </h3>
            <p className="text-sm text-luxury-text-secondary font-inter mb-4">
              What went well? What would you do differently? Any insights?
            </p>
            <textarea
              value={journal}
              onChange={(e) => setJournal(e.target.value)}
              placeholder="Write your thoughts for the day..."
              rows={5}
              className={cn(
                glassmorphismClasses,
                "w-full px-4 py-3 text-luxury-text-primary placeholder:text-luxury-text-secondary",
                "transition-all duration-300 resize-none font-inter text-sm",
                "focus:outline-none focus:ring-2 focus:ring-luxury-gold focus:border-luxury-gold"
              )}
            />
          </GlassCard>
        </motion.div>

        {/* Carry Forward Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <GlassCard hoverable={false} className="p-6">
            <h3 className="font-playfair text-xl font-semibold text-luxury-text-primary mb-2">
              Carry Forward
            </h3>
            <p className="text-sm text-luxury-text-secondary font-inter mb-4">
              These tasks from today's plan were not completed
            </p>
            {planLoading ? (
              <p className="text-sm text-luxury-text-secondary font-inter">
                Loading plan...
              </p>
            ) : incompleteTasks.length > 0 ? (
              <div className="space-y-2">
                {incompleteTasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-luxury-obsidian/50 border border-luxury-border"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-luxury-orange" />
                      <span className="text-sm text-luxury-text-primary font-inter">
                        {task.title}
                      </span>
                    </div>
                    <Badge variant={quadrantVariant(task.quadrant)}>
                      Q{task.quadrant}
                    </Badge>
                  </div>
                ))}
                <p className="text-xs text-luxury-text-secondary font-inter mt-2">
                  {incompleteTasks.length} task{incompleteTasks.length !== 1 ? "s" : ""} to carry
                  forward to tomorrow
                </p>
              </div>
            ) : (
              <div className="text-center py-4">
                <p className="text-sm text-luxury-gold font-inter">
                  All tasks completed! Nothing to carry forward.
                </p>
              </div>
            )}
          </GlassCard>
        </motion.div>

        {/* Save Button */}
        <motion.div
          className="flex justify-center pb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Button
            variant="primary"
            size="lg"
            onClick={handleSave}
            disabled={rating === 0}
          >
            {isSaved ? "Saved!" : "Save Reflection"}
          </Button>
        </motion.div>
      </div>
    </AppShell>
  )
}

export default DailyReflection
