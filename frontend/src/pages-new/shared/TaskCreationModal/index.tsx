/**
 * TaskCreationModal Component
 *
 * Glassmorphism modal overlay for creating new tasks.
 * Features quadrant selector, pomodoro estimate, due date, and keyboard shortcuts.
 */

import { useState, useEffect, useCallback } from "react"
import { motion, AnimatePresence } from "motion/react"
import { GlassCard, Button, Input } from "@/design-system/components"
import { glassmorphismClasses } from "@/design-system"
import { useCreateTask } from "@/hooks/useTasks"
import { celebrateTaskComplete } from "@/design-system/animations/confetti"
import { cn } from "@/lib/utils"

interface TaskCreationModalProps {
  isOpen: boolean
  onClose: () => void
}

interface QuadrantOption {
  quadrant: 1 | 2 | 3 | 4
  label: string
  description: string
  color: string
  glowClass: string
  borderClass: string
}

const quadrantOptions: QuadrantOption[] = [
  {
    quadrant: 1,
    label: "Q1 - Do First",
    description: "Urgent & Important",
    color: "text-luxury-indigo",
    glowClass: "shadow-[0_0_20px_rgba(99,102,241,0.4)]",
    borderClass: "border-luxury-indigo",
  },
  {
    quadrant: 2,
    label: "Q2 - Schedule",
    description: "Important, Not Urgent",
    color: "text-luxury-cyan",
    glowClass: "shadow-[0_0_20px_rgba(6,182,212,0.4)]",
    borderClass: "border-luxury-cyan",
  },
  {
    quadrant: 3,
    label: "Q3 - Delegate",
    description: "Urgent, Not Important",
    color: "text-luxury-orange",
    glowClass: "shadow-[0_0_20px_rgba(249,115,22,0.4)]",
    borderClass: "border-luxury-orange",
  },
  {
    quadrant: 4,
    label: "Q4 - Eliminate",
    description: "Neither",
    color: "text-luxury-slate",
    glowClass: "shadow-[0_0_20px_rgba(100,116,139,0.4)]",
    borderClass: "border-luxury-slate",
  },
]

export function TaskCreationModal({ isOpen, onClose }: TaskCreationModalProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [quadrant, setQuadrant] = useState<1 | 2 | 3 | 4>(1)
  const [pomodoroEstimate, setPomodoroEstimate] = useState(1)
  const [dueDate, setDueDate] = useState("")

  const createTask = useCreateTask()

  const resetForm = useCallback(() => {
    setTitle("")
    setDescription("")
    setQuadrant(1)
    setPomodoroEstimate(1)
    setDueDate("")
  }, [])

  const handleSubmit = useCallback(() => {
    if (!title.trim()) return

    createTask.mutate(
      {
        title: title.trim(),
        description: description.trim() || undefined,
        quadrant,
        due_date: dueDate || undefined,
      },
      {
        onSuccess: () => {
          celebrateTaskComplete()
          resetForm()
          onClose()
        },
      }
    )
  }, [title, description, quadrant, dueDate, createTask, resetForm, onClose])

  // Keyboard shortcuts
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault()
        onClose()
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault()
        handleSubmit()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, onClose, handleSubmit])

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          {/* Modal */}
          <motion.div
            className="relative w-full max-w-[600px] mx-4"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            <GlassCard hoverable={false} className="p-8">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="font-playfair text-2xl font-semibold text-luxury-text-primary">
                  Create New Task
                </h2>
                <button
                  onClick={onClose}
                  className="text-luxury-text-secondary hover:text-luxury-text-primary transition-colors p-1"
                  aria-label="Close modal"
                >
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M15 5L5 15M5 5l10 10"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                </button>
              </div>

              {/* Title */}
              <div className="mb-4">
                <label className="block text-sm font-inter font-medium text-luxury-text-secondary mb-1.5">
                  Title
                </label>
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="What needs to be done?"
                  autoFocus
                />
              </div>

              {/* Description */}
              <div className="mb-4">
                <label className="block text-sm font-inter font-medium text-luxury-text-secondary mb-1.5">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Add details (optional)"
                  rows={3}
                  className={cn(
                    glassmorphismClasses,
                    "w-full px-4 py-2 text-luxury-text-primary placeholder:text-luxury-text-secondary",
                    "transition-all duration-300 resize-none",
                    "focus:outline-none focus:ring-2 focus:ring-luxury-indigo focus:border-luxury-indigo"
                  )}
                />
              </div>

              {/* Quadrant Selector - 2x2 Grid */}
              <div className="mb-4">
                <label className="block text-sm font-inter font-medium text-luxury-text-secondary mb-1.5">
                  Priority Quadrant
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {quadrantOptions.map((option) => (
                    <GlassCard
                      key={option.quadrant}
                      hoverable
                      className={cn(
                        "p-3 cursor-pointer transition-all duration-300",
                        quadrant === option.quadrant
                          ? cn(
                              "border-2",
                              option.borderClass,
                              option.glowClass
                            )
                          : "border border-luxury-border hover:border-luxury-text-secondary/30"
                      )}
                      onClick={() => setQuadrant(option.quadrant)}
                    >
                      <p
                        className={cn(
                          "text-sm font-semibold font-inter",
                          quadrant === option.quadrant
                            ? option.color
                            : "text-luxury-text-primary"
                        )}
                      >
                        {option.label}
                      </p>
                      <p className="text-xs text-luxury-text-secondary mt-0.5">
                        {option.description}
                      </p>
                    </GlassCard>
                  ))}
                </div>
              </div>

              {/* Pomodoro Estimate & Due Date Row */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                {/* Pomodoro Estimate */}
                <div>
                  <label className="block text-sm font-inter font-medium text-luxury-text-secondary mb-1.5">
                    Pomodoro Estimate
                  </label>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() =>
                        setPomodoroEstimate((prev) => Math.max(1, prev - 1))
                      }
                      className={cn(
                        glassmorphismClasses,
                        "w-10 h-10 flex items-center justify-center text-luxury-text-primary",
                        "hover:bg-luxury-border transition-colors"
                      )}
                      type="button"
                    >
                      -
                    </button>
                    <span className="w-10 text-center font-inter font-semibold text-luxury-text-primary text-lg">
                      {pomodoroEstimate}
                    </span>
                    <button
                      onClick={() =>
                        setPomodoroEstimate((prev) => Math.min(12, prev + 1))
                      }
                      className={cn(
                        glassmorphismClasses,
                        "w-10 h-10 flex items-center justify-center text-luxury-text-primary",
                        "hover:bg-luxury-border transition-colors"
                      )}
                      type="button"
                    >
                      +
                    </button>
                  </div>
                </div>

                {/* Due Date */}
                <div>
                  <label className="block text-sm font-inter font-medium text-luxury-text-secondary mb-1.5">
                    Due Date
                  </label>
                  <Input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                  />
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                <p className="text-xs text-luxury-text-secondary font-inter">
                  Esc to close | Cmd+Enter to submit
                </p>
                <div className="flex gap-3">
                  <Button variant="ghost" onClick={onClose}>
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleSubmit}
                    loading={createTask.isPending}
                    disabled={!title.trim()}
                  >
                    Create Task
                  </Button>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default TaskCreationModal
