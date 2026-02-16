/**
 * PageHeader Component
 * 
 * High-focus blur header with glassmorphism
 * Sticky header that intensifies blur on scroll
 */

import * as React from "react"
import { motion } from "motion/react"
import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"
import type { PageHeaderProps } from "./PageHeader.types"

export const PageHeader = React.forwardRef<HTMLElement, PageHeaderProps>(
    ({ className, title, subtitle, actions, ...props }, ref) => {
        const [scrolled, setScrolled] = React.useState(false)

        React.useEffect(() => {
            const handleScroll = () => {
                setScrolled(window.scrollY > 10)
            }

            window.addEventListener('scroll', handleScroll)
            return () => window.removeEventListener('scroll', handleScroll)
        }, [])

        return (
            <motion.header
                ref={ref}
                className={cn(
                    glassmorphismClasses,
                    "sticky top-0 z-50 w-full px-6 py-4",
                    scrolled && "backdrop-blur-xl shadow-lg",
                    className
                )}
                initial={{ y: -100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                {...(props as Record<string, unknown>)}
            >
                <div className="flex items-center justify-between max-w-7xl mx-auto">
                    <div className="flex-1">
                        <h1 className="text-2xl font-display font-bold text-luxury-text-primary">
                            {title}
                        </h1>
                        {subtitle && (
                            <p className="mt-1 text-sm text-luxury-text-secondary">
                                {subtitle}
                            </p>
                        )}
                    </div>
                    {actions && (
                        <div className="flex items-center gap-2">
                            {actions}
                        </div>
                    )}
                </div>
            </motion.header>
        )
    }
)

PageHeader.displayName = "PageHeader"

export default PageHeader
export type { PageHeaderProps } from "./PageHeader.types"
