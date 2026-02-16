/**
 * GlassCard Component
 * 
 * Glassmorphism container with premium hover effects
 * Foundation component for all luxury UI cards
 */

import * as React from "react"
import { motion } from "motion/react"
import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"
import type { GlassCardProps } from "./GlassCard.types"

export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
    ({ className, hoverable = true, children, ...props }, ref) => {
        return (
            <motion.div
                ref={ref}
                className={cn(
                    glassmorphismClasses,
                    "p-6",
                    className
                )}
                whileHover={hoverable ? {
                    y: -4,
                    boxShadow: "0 20px 40px rgba(0, 0, 0, 0.3), 0 0 30px rgba(212, 175, 55, 0.1)"
                } : undefined}
                transition={{
                    duration: 0.3,
                    ease: "easeOut"
                }}
                {...(props as Record<string, unknown>)}
            >
                {children}
            </motion.div>
        )
    }
)

GlassCard.displayName = "GlassCard"

export default GlassCard
export type { GlassCardProps } from "./GlassCard.types"
