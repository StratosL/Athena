import { cn } from "@/lib/utils"
import { GlassCard } from "@/design-system/components"

interface LuxuryMetricCardProps {
  label: string
  value: string | number
  subtext?: string
  trend?: { direction: "up" | "down" | "stable"; value: number }
  glowColor?: "indigo" | "cyan" | "gold" | "orange"
  className?: string
}

const glowMap = {
  indigo: "hover:shadow-[0_0_20px_rgba(99,102,241,0.2)]",
  cyan: "hover:shadow-[0_0_20px_rgba(6,182,212,0.2)]",
  gold: "hover:shadow-[0_0_20px_rgba(212,175,55,0.2)]",
  orange: "hover:shadow-[0_0_20px_rgba(249,115,22,0.2)]",
}

const trendColors = {
  up: "text-green-400",
  down: "text-red-400",
  stable: "text-luxury-text-secondary",
}

const trendIcons = {
  up: "\u2191",
  down: "\u2193",
  stable: "\u2192",
}

export function LuxuryMetricCard({
  label,
  value,
  subtext,
  trend,
  glowColor = "indigo",
  className,
}: LuxuryMetricCardProps) {
  return (
    <GlassCard className={cn("p-5 text-center", glowMap[glowColor], className)}>
      <p className="text-xs text-luxury-text-secondary mb-2 uppercase tracking-wider">{label}</p>
      <p className="text-3xl font-bold font-inter text-luxury-text-primary">{value}</p>
      {subtext && <p className="text-xs text-luxury-text-secondary mt-1">{subtext}</p>}
      {trend && (
        <p className={cn("text-xs mt-1", trendColors[trend.direction])}>
          {trendIcons[trend.direction]} {Math.abs(trend.value)}% vs last period
        </p>
      )}
    </GlassCard>
  )
}
