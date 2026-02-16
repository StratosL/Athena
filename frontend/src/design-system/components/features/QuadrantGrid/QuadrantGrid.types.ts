import type { Task } from "@/lib/api"

export interface QuadrantGridProps {
  tasks: Task[]
  compact?: boolean
  onComplete?: (id: string) => void
  onDelete?: (id: string) => void
  onClick?: (task: Task) => void
  className?: string
}
