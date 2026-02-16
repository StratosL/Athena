/**
 * ProgressRing Component
 * 
 * Circular progress ring for Pomodoro timer with gradient stroke
 * Features pulsing glow during active state
 */

import * as React from "react"
import { motion } from "motion/react"
import { cn } from "@/lib/utils"
import type { ProgressRingProps } from "./ProgressRing.types"

export const ProgressRing = React.forwardRef<HTMLDivElement, ProgressRingProps>(
    ({
        className,
        percentage,
        size = 400,
        strokeWidth = 12,
        active = false,
        children,
        ...props
    }, ref) => {
        const gradientId = React.useId()
        const radius = (size - strokeWidth) / 2
        const circumference = 2 * Math.PI * radius
        const offset = circumference * (1 - percentage / 100)

        return (
            <div
                ref={ref}
                className={cn("relative inline-flex items-center justify-center", className)}
                style={{ width: size, height: size }}
                {...props}
            >
                {/* SVG Progress Ring */}
                <svg
                    width={size}
                    height={size}
                    className="transform -rotate-90"
                >
                    {/* Background Circle */}
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        stroke="rgba(255, 255, 255, 0.1)"
                        strokeWidth={strokeWidth}
                        fill="none"
                    />

                    {/* Progress Circle with Gradient */}
                    <defs>
                        <linearGradient id={`progressGradient-${gradientId}`} x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#6366f1" />
                            <stop offset="100%" stopColor="#d4af37" />
                        </linearGradient>
                    </defs>

                    <motion.circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        stroke={`url(#progressGradient-${gradientId})`}
                        strokeWidth={strokeWidth}
                        fill="none"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{
                            strokeDashoffset: offset,
                            filter: active
                                ? [
                                    "drop-shadow(0 0 10px rgba(212, 175, 55, 0.3))",
                                    "drop-shadow(0 0 30px rgba(212, 175, 55, 0.6))",
                                    "drop-shadow(0 0 10px rgba(212, 175, 55, 0.3))",
                                ]
                                : "drop-shadow(0 0 10px rgba(212, 175, 55, 0.3))"
                        }}
                        transition={{
                            strokeDashoffset: { duration: 0.5, ease: "easeOut" },
                            filter: active
                                ? { duration: 3, repeat: Infinity, ease: "easeInOut" }
                                : { duration: 0.3 }
                        }}
                    />
                </svg>

                {/* Center Content */}
                <div className="absolute inset-0 flex items-center justify-center">
                    {children}
                </div>
            </div>
        )
    }
)

ProgressRing.displayName = "ProgressRing"

export default ProgressRing
export type { ProgressRingProps } from "./ProgressRing.types"
