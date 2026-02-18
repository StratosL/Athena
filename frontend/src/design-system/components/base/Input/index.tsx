/**
 * Input Component
 * 
 * Glassmorphism input field with focus states and error handling
 */

import * as React from "react"
import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"
import type { InputProps } from "./Input.types"

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, error, errorMessage, disabled, ...props }, ref) => {
        return (
            <div className="w-full">
                <input
                    ref={ref}
                    className={cn(
                        glassmorphismClasses,
                        "w-full px-4 py-2 text-luxury-text-primary placeholder:text-luxury-text-secondary",
                        "transition-all duration-300",
                        "focus:outline-none focus:ring-2 focus:ring-luxury-accent focus:border-luxury-accent",
                        error && "ring-2 ring-red-500 border-red-500",
                        disabled && "opacity-50 cursor-not-allowed",
                        className
                    )}
                    disabled={disabled}
                    {...props}
                />
                {error && errorMessage && (
                    <p className="mt-1 text-sm text-red-500">{errorMessage}</p>
                )}
            </div>
        )
    }
)

Input.displayName = "Input"

export default Input
export type { InputProps } from "./Input.types"
