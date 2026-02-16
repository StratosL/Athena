import type { DailyPlan } from "@/lib/api"

export interface PlanWidgetProps {
  plan?: DailyPlan | null
  isLoading?: boolean
  onCompleteTask?: (taskId: string) => void
  className?: string
}
