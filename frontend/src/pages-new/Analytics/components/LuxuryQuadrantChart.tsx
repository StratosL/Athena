import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts"
import { cn } from "@/lib/utils"
import { GlassCard } from "@/design-system/components"
import { LUXURY_QUADRANT_COLORS, LUXURY_CHART_THEME, LUXURY_TOOLTIP_STYLE } from "@/lib/chartThemeLuxury"
import type { TaskQuadrantStats } from "@/lib/api"

interface LuxuryQuadrantChartProps {
  data: TaskQuadrantStats[]
  className?: string
}

const QUADRANT_LABELS: Record<number, string> = {
  1: "Q1: Do First",
  2: "Q2: Schedule",
  3: "Q3: Delegate",
  4: "Q4: Eliminate",
}

export function LuxuryQuadrantChart({ data, className }: LuxuryQuadrantChartProps) {
  const chartData = data.map((stat) => ({
    name: QUADRANT_LABELS[stat.quadrant],
    quadrant: stat.quadrant,
    total: stat.total,
    completed: stat.completed,
    completionRate: stat.completion_rate,
  }))

  return (
    <GlassCard className={cn("p-6", className)} hoverable={false}>
      <h3 className="font-playfair font-semibold text-luxury-text-primary mb-1">
        Tasks by Quadrant
      </h3>
      <p className="text-sm text-luxury-text-secondary mb-4">Distribution across Eisenhower Matrix</p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid
            strokeDasharray="3 3"
            stroke={LUXURY_CHART_THEME.gridStroke}
            horizontal={false}
          />
          <XAxis
            type="number"
            stroke={LUXURY_CHART_THEME.textMuted}
            tick={{ fill: LUXURY_CHART_THEME.textSecondary, fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: LUXURY_CHART_THEME.gridStroke }}
          />
          <YAxis
            type="category"
            dataKey="name"
            stroke={LUXURY_CHART_THEME.textMuted}
            tick={{ fill: LUXURY_CHART_THEME.textSecondary, fontSize: 12 }}
            tickLine={false}
            axisLine={false}
            width={100}
          />
          <Tooltip
            contentStyle={LUXURY_TOOLTIP_STYLE}
            labelStyle={{ color: LUXURY_CHART_THEME.text }}
            formatter={(value: number | undefined, name: string | undefined) => {
              const v = value ?? 0
              if (name === "total") return [`${v} tasks`, "Total"]
              if (name === "completed") return [`${v} done`, "Completed"]
              return [v, name ?? ""]
            }}
          />
          <Bar dataKey="total" radius={[0, 4, 4, 0]} barSize={24}>
            {chartData.map((entry) => (
              <Cell
                key={`cell-${entry.quadrant}`}
                fill={LUXURY_QUADRANT_COLORS[entry.quadrant]}
                opacity={0.8}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-2 gap-2">
        {chartData.map((stat) => (
          <div key={stat.quadrant} className="flex items-center gap-2 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: LUXURY_QUADRANT_COLORS[stat.quadrant] }}
            />
            <span className="text-luxury-text-secondary">
              {stat.completed}/{stat.total} ({stat.completionRate}%)
            </span>
          </div>
        ))}
      </div>
    </GlassCard>
  )
}
