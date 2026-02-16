import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { cn } from "@/lib/utils"
import { GlassCard } from "@/design-system/components"
import { LUXURY_CHART_COLORS, LUXURY_CHART_THEME, LUXURY_TOOLTIP_STYLE } from "@/lib/chartThemeLuxury"
import type { PomodoroTrendPoint } from "@/lib/api"

interface LuxuryPomodoroChartProps {
  data: PomodoroTrendPoint[]
  className?: string
}

export function LuxuryPomodoroChart({ data, className }: LuxuryPomodoroChartProps) {
  const formattedData = data.map((point) => ({
    ...point,
    displayDate: new Date(point.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }))

  return (
    <GlassCard className={cn("p-6", className)} hoverable={false}>
      <h3 className="font-playfair font-semibold text-luxury-text-primary mb-1">
        Pomodoro Trends
      </h3>
      <p className="text-sm text-luxury-text-secondary mb-4">Daily focus sessions completed</p>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={formattedData}>
          <defs>
            <linearGradient id="pomodoroGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={LUXURY_CHART_COLORS.indigo} stopOpacity={0.3} />
              <stop offset="95%" stopColor={LUXURY_CHART_COLORS.indigo} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke={LUXURY_CHART_THEME.gridStroke}
            vertical={false}
          />
          <XAxis
            dataKey="displayDate"
            stroke={LUXURY_CHART_THEME.textMuted}
            tick={{ fill: LUXURY_CHART_THEME.textSecondary, fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: LUXURY_CHART_THEME.gridStroke }}
          />
          <YAxis
            stroke={LUXURY_CHART_THEME.textMuted}
            tick={{ fill: LUXURY_CHART_THEME.textSecondary, fontSize: 12 }}
            tickLine={false}
            axisLine={false}
            allowDecimals={false}
          />
          <Tooltip
            contentStyle={LUXURY_TOOLTIP_STYLE}
            labelStyle={{ color: LUXURY_CHART_THEME.text }}
            formatter={(value: number | undefined) => [`${value ?? 0} pomodoros`, "Completed"]}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke={LUXURY_CHART_COLORS.indigo}
            strokeWidth={3}
            fill="url(#pomodoroGradient)"
            dot={{ fill: LUXURY_CHART_COLORS.indigo, strokeWidth: 0, r: 4 }}
            activeDot={{
              r: 6,
              fill: LUXURY_CHART_COLORS.gold,
              stroke: LUXURY_CHART_COLORS.indigo,
              strokeWidth: 2,
            }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </GlassCard>
  )
}
