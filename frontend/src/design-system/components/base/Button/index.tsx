/**
 * Button Component
 * 
 * Luxury button with premium animations and multiple variants
 * Supports primary (gradient), secondary (gold), ghost, and danger variants
 */

import * as React from "react"
import { motion } from "motion/react"
import { cva } from "class-variance-authority"
import { cn } from "@/lib/utils"
import type { ButtonProps } from "./Button.types"

const buttonVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-gold focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50",
    {
        variants: {
            variant: {
                primary:
                    "bg-gradient-to-r from-luxury-indigo to-luxury-gold text-white shadow-lg hover:shadow-xl",
                secondary:
                    "bg-luxury-gold text-luxury-obsidian shadow-md hover:shadow-lg",
                ghost:
                    "border border-luxury-border bg-transparent text-luxury-text-primary hover:bg-luxury-card",
                danger:
                    "bg-red-600 text-white shadow-md hover:shadow-lg hover:bg-red-700",
            },
            size: {
                sm: "h-8 px-4 text-xs",
                md: "h-10 px-6 text-sm",
                lg: "h-12 px-8 text-base",
            },
        },
        defaultVariants: {
            variant: "primary",
            size: "md",
        },
    }
)

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, loading, icon, disabled, children, ...props }, ref) => {
        return (
            <motion.button
                ref={ref}
                className={cn(buttonVariants({ variant, size, className }))}
                whileHover={!disabled && !loading ? { scale: 1.02 } : undefined}
                whileTap={!disabled && !loading ? { scale: 0.98 } : undefined}
                transition={{
                    duration: 0.3,
                    ease: "easeOut"
                }}
                disabled={disabled || loading}
                {...(props as Record<string, unknown>)}
            >
                {loading ? (
                    <>
                        <svg
                            className="animate-spin h-4 w-4"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                            />
                            <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                        </svg>
                        Loading...
                    </>
                ) : (
                    <>
                        {icon && <span className="flex-shrink-0">{icon}</span>}
                        {children}
                    </>
                )}
            </motion.button>
        )
    }
)

Button.displayName = "Button"

export default Button
export { buttonVariants }
export type { ButtonProps } from "./Button.types"
