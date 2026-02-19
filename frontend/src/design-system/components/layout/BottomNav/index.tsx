import { useState } from "react"
import { Link } from "react-router-dom"
import { AnimatePresence, motion } from "motion/react"
import { MoreHorizontal } from "lucide-react"
import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"
import type { BottomNavProps } from "./BottomNav.types"

export function BottomNav({ items, overflowItems, className }: BottomNavProps) {
  const [isMoreOpen, setIsMoreOpen] = useState(false)

  const isOverflowActive = overflowItems?.some((item) => item.active) ?? false

  return (
    <>
      {/* Bottom Sheet */}
      <AnimatePresence>
        {isMoreOpen && overflowItems && (
          <>
            <motion.div
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMoreOpen(false)}
            />
            <motion.div
              className={cn(
                "fixed bottom-16 left-0 right-0 z-50 lg:hidden",
                "rounded-t-2xl pb-safe",
                glassmorphismClasses,
                "bg-luxury-obsidian/95 backdrop-blur-xl border-b-0"
              )}
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
            >
              {/* Drag handle */}
              <div className="flex justify-center pt-3 pb-2">
                <div className="w-10 h-1 rounded-full bg-luxury-text-secondary/30" />
              </div>

              {/* Overflow nav items */}
              <div className="px-4 pb-4 space-y-1">
                {overflowItems.map((item, index) => (
                  <Link
                    key={index}
                    to={item.href}
                    onClick={() => setIsMoreOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-4 py-3 rounded-xl transition-all",
                      item.active
                        ? "text-luxury-gold bg-luxury-gold/10"
                        : "text-luxury-text-secondary hover:text-luxury-text-primary hover:bg-luxury-card"
                    )}
                  >
                    <span className="w-5 h-5 flex items-center justify-center">
                      {item.icon}
                    </span>
                    <span className="text-sm font-medium">{item.label}</span>
                  </Link>
                ))}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Bottom Nav Bar */}
      <nav
        className={cn(
          "fixed bottom-0 left-0 right-0 z-50 lg:hidden",
          "backdrop-blur-xl bg-luxury-obsidian/90 border-t border-luxury-border",
          "px-2 py-2 safe-bottom",
          className
        )}
      >
        <div className="flex items-center">
          {items.map((item, index) => (
            <Link
              key={index}
              to={item.href}
              className={cn(
                "flex flex-col items-center gap-1 min-w-[64px] flex-1 px-2 py-1.5 rounded-lg transition-all",
                item.active
                  ? "text-luxury-gold"
                  : "text-luxury-text-secondary hover:text-luxury-text-primary"
              )}
            >
              <span className="w-5 h-5 flex items-center justify-center">
                {item.icon}
              </span>
              <span className="text-[10px] font-medium">{item.label}</span>
            </Link>
          ))}

          {/* More button */}
          {overflowItems && overflowItems.length > 0 && (
            <button
              onClick={() => setIsMoreOpen((prev) => !prev)}
              className={cn(
                "flex flex-col items-center gap-1 min-w-[64px] flex-1 px-2 py-1.5 rounded-lg transition-all",
                isOverflowActive || isMoreOpen
                  ? "text-luxury-gold"
                  : "text-luxury-text-secondary hover:text-luxury-text-primary"
              )}
            >
              <span className="w-5 h-5 flex items-center justify-center">
                <MoreHorizontal className="w-5 h-5" />
              </span>
              <span className="text-[10px] font-medium">More</span>
            </button>
          )}
        </div>
      </nav>
    </>
  )
}

export default BottomNav
export type { BottomNavProps } from "./BottomNav.types"
