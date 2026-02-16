/**
 * TaskCard Component
 * 
 * Luxury task card with quadrant-specific styling and completion animation
 * Combines GlassCard with Badge for premium task display
 */

import * as React from "react"
import { motion } from "motion/react"
import { cn } from "@/lib/utils"
import { GlassCard } from "../../base/GlassCard"
import { Badge } from "../../base/Badge"
import type { TaskCardProps } from "./TaskCard.types"

const quadrantConfig = {
    1: { label: "Q1", variant: "q1" as const, glow: "shadow-[0_0_20px_rgba(99,102,241,0.2)]" },
    2: { label: "Q2", variant: "q2" as const, glow: "shadow-[0_0_20px_rgba(6,182,212,0.2)]" },
    3: { label: "Q3", variant: "q3" as const, glow: "shadow-[0_0_20px_rgba(249,115,22,0.2)]" },
    4: { label: "Q4", variant: "q4" as const, glow: "shadow-[0_0_20px_rgba(100,116,139,0.2)]" },
}

export const TaskCard = React.forwardRef<HTMLDivElement, TaskCardProps>(
    ({
        className,
        id,
        title,
        description,
        quadrant,
        pomodoroCount = 0,
        completed = false,
        onCompletedChange,
        onDelete,
        onCardClick,
        ...props
    }, ref) => {
        const [isCompleted, setIsCompleted] = React.useState(completed)
        const config = quadrantConfig[quadrant]

        React.useEffect(() => {
            setIsCompleted(completed)
        }, [completed])

        const handleCheckboxChange = (e: React.MouseEvent) => {
            e.stopPropagation()
            const newValue = !isCompleted
            setIsCompleted(newValue)
            onCompletedChange?.(newValue)
        }

        const handleDelete = (e: React.MouseEvent) => {
            e.stopPropagation()
            if (id) onDelete?.(id)
        }

        const handleClick = () => {
            if (id) onCardClick?.(id)
        }

        return (
            <GlassCard
                ref={ref}
                className={cn(
                    "relative transition-all duration-300",
                    config.glow,
                    isCompleted && "opacity-60",
                    onCardClick && "cursor-pointer",
                    className
                )}
                onClick={handleClick}
                {...props}
            >
                {/* Quadrant Badge + Actions */}
                <div className="flex items-start justify-between mb-3">
                    <Badge variant={config.variant}>
                        {config.label}
                    </Badge>

                    <div className="flex items-center gap-1">
                        {/* Delete Button */}
                        {onDelete && id && !isCompleted && (
                            <motion.button
                                onClick={handleDelete}
                                className="w-6 h-6 rounded-md flex items-center justify-center text-luxury-text-secondary hover:text-red-400 transition-colors"
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                aria-label="Delete task"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </motion.button>
                        )}

                        {/* Completion Checkbox */}
                        <motion.button
                            onClick={handleCheckboxChange}
                            className={cn(
                                "w-6 h-6 rounded-md border-2 flex items-center justify-center transition-all duration-300",
                                isCompleted
                                    ? "bg-luxury-gold border-luxury-gold"
                                    : "border-luxury-border hover:border-luxury-gold"
                            )}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            aria-label={isCompleted ? "Mark as incomplete" : "Mark as complete"}
                        >
                            {isCompleted && (
                                <motion.svg
                                    initial={{ scale: 0, rotate: -180 }}
                                    animate={{ scale: 1, rotate: 0 }}
                                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                                    className="w-4 h-4 text-luxury-obsidian"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={3}
                                        d="M5 13l4 4L19 7"
                                    />
                                </motion.svg>
                            )}
                        </motion.button>
                    </div>
                </div>

                {/* Task Title */}
                <h3 className={cn(
                    "text-lg font-display font-semibold text-luxury-text-primary mb-2",
                    isCompleted && "line-through"
                )}>
                    {title}
                </h3>

                {/* Task Description */}
                {description && (
                    <p className="text-sm text-luxury-text-secondary mb-3">
                        {description}
                    </p>
                )}

                {/* Pomodoro Count */}
                {pomodoroCount > 0 && (
                    <div className="flex items-center gap-1 text-luxury-text-secondary text-sm">
                        <span>🍅</span>
                        <span>×{pomodoroCount}</span>
                    </div>
                )}
            </GlassCard>
        )
    }
)

TaskCard.displayName = "TaskCard"

export default TaskCard
export type { TaskCardProps } from "./TaskCard.types"
