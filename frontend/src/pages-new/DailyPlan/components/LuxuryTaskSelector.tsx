import { useState, useMemo } from "react"
import { Search, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { GlassCard, Input, Badge } from "@/design-system/components"
import type { Task, SlotType } from "@/lib/api"

interface LuxuryTaskSelectorProps {
  isOpen: boolean
  onClose: () => void
  tasks: Task[]
  assignedTaskIds: string[]
  onSelect: (taskId: string) => void
  targetSlot: SlotType
}

const slotLabels: Record<SlotType, string> = {
  major: "Major Task",
  medium: "Medium Task",
  small: "Small Task",
}

const quadrantBadgeVariant = {
  1: "q1" as const,
  2: "q2" as const,
  3: "q3" as const,
  4: "q4" as const,
}

export function LuxuryTaskSelector({
  isOpen,
  onClose,
  tasks,
  assignedTaskIds,
  onSelect,
  targetSlot,
}: LuxuryTaskSelectorProps) {
  const [searchQuery, setSearchQuery] = useState("")

  const availableTasks = useMemo(() => {
    return tasks.filter((task) => {
      if (task.status === "completed") return false
      if (assignedTaskIds.includes(task.id)) return false
      if (searchQuery) {
        return task.title.toLowerCase().includes(searchQuery.toLowerCase())
      }
      return true
    })
  }, [tasks, assignedTaskIds, searchQuery])

  const handleSelect = (taskId: string) => {
    onSelect(taskId)
    setSearchQuery("")
    onClose()
  }

  const handleClose = () => {
    setSearchQuery("")
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <GlassCard className="relative w-full max-w-[500px] p-6 max-h-[80vh] flex flex-col" hoverable={false}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-playfair font-semibold text-luxury-text-primary">
            Select {slotLabels[targetSlot]}
          </h2>
          <button
            onClick={handleClose}
            className="w-8 h-8 rounded-md flex items-center justify-center text-luxury-text-secondary hover:text-luxury-text-primary hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-luxury-text-secondary" />
          <Input
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Task List */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {availableTasks.length === 0 ? (
            <p className="text-center py-8 text-luxury-text-secondary">
              {searchQuery
                ? "No tasks match your search"
                : "No available tasks. Create some tasks first!"}
            </p>
          ) : (
            availableTasks.map((task) => (
              <button
                key={task.id}
                type="button"
                onClick={() => handleSelect(task.id)}
                className={cn(
                  "w-full text-left p-3 rounded-lg border border-luxury-border",
                  "bg-luxury-card hover:bg-white/5 transition-colors",
                  "focus:outline-none focus:ring-2 focus:ring-luxury-indigo/50"
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-luxury-text-primary truncate">
                      {task.title}
                    </p>
                    {task.description && (
                      <p className="text-sm text-luxury-text-secondary truncate mt-0.5">
                        {task.description}
                      </p>
                    )}
                  </div>
                  <Badge variant={quadrantBadgeVariant[task.quadrant]}>
                    Q{task.quadrant}
                  </Badge>
                </div>
                <div className="flex items-center gap-2 mt-2 text-xs text-luxury-text-secondary">
                  {task.pomodoro_count > 0 && (
                    <span>{task.pomodoro_count} pomodoros</span>
                  )}
                </div>
              </button>
            ))
          )}
        </div>
      </GlassCard>
    </div>
  )
}
