import { Check, Plus, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { GlassCard } from "@/design-system/components"
import type { TaskInfo, SlotType } from "@/lib/api"

interface LuxuryTaskSlotProps {
  task?: TaskInfo
  slotType: SlotType
  slotIndex?: number
  onRemove?: (taskId: string) => void
  onComplete?: (taskId: string) => void
  onClick?: () => void
  className?: string
}

const slotStyles = {
  major: {
    height: "min-h-[80px]",
    glow: "shadow-[0_0_15px_rgba(99,102,241,0.15)]",
    borderColor: "border-luxury-indigo/30",
    dotColor: "text-luxury-indigo",
    label: "Major Task",
  },
  medium: {
    height: "min-h-[64px]",
    glow: "shadow-[0_0_15px_rgba(6,182,212,0.15)]",
    borderColor: "border-luxury-cyan/30",
    dotColor: "text-luxury-cyan",
    label: "Medium Task",
  },
  small: {
    height: "min-h-[56px]",
    glow: "shadow-[0_0_15px_rgba(249,115,22,0.15)]",
    borderColor: "border-luxury-orange/30",
    dotColor: "text-luxury-orange",
    label: "Small Task",
  },
} as const

export function LuxuryTaskSlot({
  task,
  slotType,
  slotIndex,
  onRemove,
  onComplete,
  onClick,
  className,
}: LuxuryTaskSlotProps) {
  const style = slotStyles[slotType]
  const isCompleted = task?.status === "completed"

  if (!task) {
    return (
      <button
        type="button"
        onClick={onClick}
        className={cn(
          "w-full rounded-xl border-2 border-dashed flex items-center justify-center gap-2 transition-all duration-300",
          "hover:bg-white/5 cursor-pointer border-luxury-border/30",
          style.height,
          className
        )}
      >
        <Plus className={cn("w-4 h-4", style.dotColor)} />
        <span className={cn("text-sm font-medium", style.dotColor)}>
          {style.label}
          {slotIndex !== undefined && ` ${slotIndex + 1}`}
        </span>
      </button>
    )
  }

  return (
    <GlassCard
      className={cn(
        "flex items-center justify-between px-4",
        style.height,
        style.glow,
        isCompleted && "opacity-50",
        className
      )}
      hoverable={false}
    >
      <div className="flex-1 min-w-0">
        <p className={cn(
          "font-medium text-luxury-text-primary truncate",
          isCompleted && "line-through text-luxury-text-secondary"
        )}>
          {task.title}
        </p>
        <p className="text-xs text-luxury-text-secondary">
          Q{task.quadrant} · {task.pomodoro_count} pomodoros
        </p>
      </div>
      <div className="flex gap-1 ml-2 flex-shrink-0">
        {!isCompleted && onComplete && (
          <button
            onClick={(e) => { e.stopPropagation(); onComplete(task.id) }}
            className="w-7 h-7 rounded-md flex items-center justify-center text-green-400 hover:bg-green-400/10 transition-colors"
          >
            <Check className="w-4 h-4" />
          </button>
        )}
        {onRemove && (
          <button
            onClick={(e) => { e.stopPropagation(); onRemove(task.id) }}
            className="w-7 h-7 rounded-md flex items-center justify-center text-red-400 hover:bg-red-400/10 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </GlassCard>
  )
}
