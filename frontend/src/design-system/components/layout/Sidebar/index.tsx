/**
 * Sidebar Component
 * 
 * Navigation sidebar with glassmorphism and collapse functionality
 * Persists collapse state in localStorage
 */

import * as React from "react"
import { motion, AnimatePresence } from "motion/react"
import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"
import type { SidebarProps } from "./Sidebar.types"

const STORAGE_KEY = "sidebar-collapsed"

export const Sidebar = React.forwardRef<HTMLElement, SidebarProps>(
    ({ className, items, bottomItems, collapsed: controlledCollapsed, onCollapsedChange, ...props }, ref) => {
        const [internalCollapsed, setInternalCollapsed] = React.useState(() => {
            if (typeof window !== 'undefined') {
                const stored = localStorage.getItem(STORAGE_KEY)
                return stored ? JSON.parse(stored) : false
            }
            return false
        })

        const collapsed = controlledCollapsed !== undefined ? controlledCollapsed : internalCollapsed

        const handleToggle = () => {
            const newValue = !collapsed
            setInternalCollapsed(newValue)
            onCollapsedChange?.(newValue)

            if (typeof window !== 'undefined') {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(newValue))
            }
        }

        return (
            <motion.nav
                ref={ref}
                className={cn(
                    glassmorphismClasses,
                    "h-screen sticky top-0 flex flex-col p-4 transition-all duration-300",
                    collapsed ? "w-20" : "w-64",
                    className
                )}
                {...(props as Record<string, unknown>)}
            >
                {/* Toggle Button */}
                <button
                    onClick={handleToggle}
                    className="mb-6 p-2 rounded-lg hover:bg-luxury-card transition-colors text-luxury-text-primary"
                    aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                    <svg
                        className={cn(
                            "w-6 h-6 transition-transform duration-300",
                            collapsed && "rotate-180"
                        )}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
                        />
                    </svg>
                </button>

                {/* Navigation Items */}
                <div className="flex-1 space-y-2">
                    {items.map((item, index) => (
                        <a
                            key={index}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-300",
                                "hover:bg-luxury-card",
                                item.active && "bg-luxury-gold/20 text-luxury-gold shadow-[0_0_15px_rgba(212,175,55,0.3)]",
                                !item.active && "text-luxury-text-primary"
                            )}
                        >
                            <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center">
                                {item.icon}
                            </span>
                            <AnimatePresence>
                                {!collapsed && (
                                    <motion.span
                                        initial={{ opacity: 0, width: 0 }}
                                        animate={{ opacity: 1, width: "auto" }}
                                        exit={{ opacity: 0, width: 0 }}
                                        transition={{ duration: 0.3 }}
                                        className="font-medium whitespace-nowrap overflow-hidden"
                                    >
                                        {item.label}
                                    </motion.span>
                                )}
                            </AnimatePresence>
                        </a>
                    ))}
                </div>

                {/* Bottom Items (Guide, Settings) */}
                {bottomItems && bottomItems.length > 0 && (
                    <div className="space-y-2 pt-4 border-t border-luxury-border">
                        {bottomItems.map((item, index) => (
                            <a
                                key={index}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-300",
                                    "hover:bg-luxury-card",
                                    item.active && "bg-luxury-gold/20 text-luxury-gold shadow-[0_0_15px_rgba(212,175,55,0.3)]",
                                    !item.active && "text-luxury-text-primary"
                                )}
                            >
                                <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center">
                                    {item.icon}
                                </span>
                                <AnimatePresence>
                                    {!collapsed && (
                                        <motion.span
                                            initial={{ opacity: 0, width: 0 }}
                                            animate={{ opacity: 1, width: "auto" }}
                                            exit={{ opacity: 0, width: 0 }}
                                            transition={{ duration: 0.3 }}
                                            className="font-medium whitespace-nowrap overflow-hidden"
                                        >
                                            {item.label}
                                        </motion.span>
                                    )}
                                </AnimatePresence>
                            </a>
                        ))}
                    </div>
                )}
            </motion.nav>
        )
    }
)

Sidebar.displayName = "Sidebar"

export default Sidebar
export type { SidebarProps, SidebarNavItem } from "./Sidebar.types"
