import { GlassCard } from "@/design-system/components"

interface SettingRowProps {
  children: React.ReactNode
}

export function SettingRow({ children }: SettingRowProps) {
  return (
    <GlassCard className="p-4">
      {children}
    </GlassCard>
  )
}
