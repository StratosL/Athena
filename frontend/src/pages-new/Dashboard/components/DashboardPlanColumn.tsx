import { PlanWidget } from "@/design-system/components"
import { useTodayPlan } from "@/hooks/useDailyPlan"
import { useCompleteTask } from "@/hooks/useTasks"

export function DashboardPlanColumn() {
  const { data: plan, isLoading } = useTodayPlan()
  const completeTask = useCompleteTask()

  return (
    <PlanWidget
      plan={plan}
      isLoading={isLoading}
      onCompleteTask={(id) => completeTask.mutate(id)}
    />
  )
}
