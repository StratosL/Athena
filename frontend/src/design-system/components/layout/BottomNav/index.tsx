import { Link } from "react-router-dom"
import { cn } from "@/lib/utils"
import type { BottomNavProps } from "./BottomNav.types"

export function BottomNav({ items, className }: BottomNavProps) {
  return (
    <nav
      className={cn(
        "fixed bottom-0 left-0 right-0 z-50 lg:hidden",
        "backdrop-blur-xl bg-luxury-obsidian/90 border-t border-luxury-border",
        "px-2 py-2 safe-bottom",
        className
      )}
    >
      <div className="flex items-center overflow-x-auto scrollbar-hide">
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
      </div>
    </nav>
  )
}

export default BottomNav
export type { BottomNavProps } from "./BottomNav.types"
