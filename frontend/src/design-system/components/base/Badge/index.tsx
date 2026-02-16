/**
 * Badge Component
 * 
 * Quadrant indicator badges with color variants for Eisenhower Matrix
 */

import * as React from "react"
import { cva } from "class-variance-authority"
import { cn } from "@/lib/utils"
import type { BadgeProps } from "./Badge.types"

const badgeVariants = cva(
    "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold transition-all duration-300",
    {
        variants: {
            variant: {
                q1: "bg-luxury-indigo/20 text-luxury-indigo border border-luxury-indigo/30 shadow-[0_0_10px_rgba(99,102,241,0.3)]",
                q2: "bg-luxury-cyan/20 text-luxury-cyan border border-luxury-cyan/30 shadow-[0_0_10px_rgba(6,182,212,0.3)]",
                q3: "bg-luxury-orange/20 text-luxury-orange border border-luxury-orange/30 shadow-[0_0_10px_rgba(249,115,22,0.3)]",
                q4: "bg-luxury-slate/20 text-luxury-slate border border-luxury-slate/30 shadow-[0_0_10px_rgba(100,116,139,0.3)]",
                gold: "bg-luxury-gold/20 text-luxury-gold border border-luxury-gold/30 shadow-[0_0_10px_rgba(212,175,55,0.3)]",
                default: "bg-luxury-text-secondary/20 text-luxury-text-secondary border border-luxury-text-secondary/30",
            },
        },
        defaultVariants: {
            variant: "default",
        },
    }
)

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
    ({ className, variant, icon, children, ...props }, ref) => {
        return (
            <span
                ref={ref}
                className={cn(badgeVariants({ variant, className }))}
                {...props}
            >
                {icon && <span className="flex-shrink-0">{icon}</span>}
                {children}
            </span>
        )
    }
)

Badge.displayName = "Badge"

export default Badge
export { badgeVariants }
export type { BadgeProps } from "./Badge.types"
