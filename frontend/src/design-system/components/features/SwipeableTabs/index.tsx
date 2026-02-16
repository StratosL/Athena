import { useState } from "react"
import { motion, AnimatePresence } from "motion/react"
import { cn } from "@/lib/utils"
import type { SwipeableTabsProps } from "./SwipeableTabs.types"

export function SwipeableTabs({ tabs, className }: SwipeableTabsProps) {
  const [activeIndex, setActiveIndex] = useState(0)
  const [direction, setDirection] = useState(0)

  const handleTabChange = (index: number) => {
    setDirection(index > activeIndex ? 1 : -1)
    setActiveIndex(index)
  }

  return (
    <div className={cn("w-full", className)}>
      {/* Tab Headers */}
      <div className="flex gap-1 mb-4 backdrop-blur-md bg-luxury-card border border-luxury-border rounded-lg p-1 overflow-x-auto">
        {tabs.map((tab, index) => (
          <button
            key={index}
            onClick={() => handleTabChange(index)}
            className={cn(
              "flex-1 min-w-0 px-3 py-1.5 rounded-md text-sm font-medium transition-all whitespace-nowrap",
              activeIndex === index
                ? "bg-luxury-gold text-luxury-obsidian"
                : "text-luxury-text-secondary hover:text-luxury-text-primary hover:bg-white/5"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="overflow-hidden">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={activeIndex}
            initial={{ x: direction * 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: direction * -100, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            {tabs[activeIndex]?.content}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}

export default SwipeableTabs
export type { SwipeableTabsProps, SwipeableTab } from "./SwipeableTabs.types"
