import { Calendar } from "lucide-react"
import { cn } from "@/lib/utils"
import { GlassCard } from "@/design-system/components"
import { LuxuryTaskSlot } from "./LuxuryTaskSlot"
import { LuxuryPlanProgress } from "./LuxuryPlanProgress"
import type { DailyPlan, SlotType } from "@/lib/api"

interface LuxuryPlanViewProps {
  plan: DailyPlan
  onRemoveTask?: (taskId: string) => void
  onCompleteTask?: (taskId: string) => void
  onSlotClick?: (slot: SlotType, index?: number) => void
  className?: string
}

export function LuxuryPlanView({
  plan,
  onRemoveTask,
  onCompleteTask,
  onSlotClick,
  className,
}: LuxuryPlanViewProps) {
  const displayDate = new Date(plan.date).toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  })

  const mediumSlots = Array.from({ length: 3 }, (_, i) => plan.medium_tasks[i])
  const smallSlots = Array.from({ length: 5 }, (_, i) => plan.small_tasks[i])

  return (
    <GlassCard className={cn("p-6", className)} hoverable={false}>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-luxury-indigo/20 flex items-center justify-center">
          <Calendar className="w-5 h-5 text-luxury-indigo" />
        </div>
        <div>
          <h2 className="text-xl font-playfair font-semibold text-luxury-text-primary">
            Today's Plan
          </h2>
          <p className="text-sm text-luxury-text-secondary">{displayDate}</p>
        </div>
      </div>

      <LuxuryPlanProgress
        completedTasks={plan.completed_tasks}
        totalTasks={plan.total_tasks}
        completionRate={plan.completion_rate}
        className="mb-6"
      />

      <div className="space-y-6">
        {/* Major */}
        <div>
          <h3 className="text-sm font-semibold text-luxury-indigo mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-luxury-indigo" />
            Major Task (1)
          </h3>
          <LuxuryTaskSlot
            task={plan.major_task}
            slotType="major"
            onRemove={onRemoveTask}
            onComplete={onCompleteTask}
            onClick={() => onSlotClick?.("major")}
          />
        </div>

        {/* Medium */}
        <div>
          <h3 className="text-sm font-semibold text-luxury-cyan mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-luxury-cyan" />
            Medium Tasks (3)
          </h3>
          <div className="space-y-2">
            {mediumSlots.map((task, index) => (
              <LuxuryTaskSlot
                key={task?.id || `medium-${index}`}
                task={task}
                slotType="medium"
                slotIndex={index}
                onRemove={onRemoveTask}
                onComplete={onCompleteTask}
                onClick={() => onSlotClick?.("medium", index)}
              />
            ))}
          </div>
        </div>

        {/* Small */}
        <div>
          <h3 className="text-sm font-semibold text-luxury-orange mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-luxury-orange" />
            Small Tasks (5)
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {smallSlots.map((task, index) => (
              <LuxuryTaskSlot
                key={task?.id || `small-${index}`}
                task={task}
                slotType="small"
                slotIndex={index}
                onRemove={onRemoveTask}
                onComplete={onCompleteTask}
                onClick={() => onSlotClick?.("small", index)}
              />
            ))}
          </div>
        </div>
      </div>
    </GlassCard>
  )
}
