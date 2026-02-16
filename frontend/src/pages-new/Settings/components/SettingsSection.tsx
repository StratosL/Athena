interface SettingsSectionProps {
  title: string
  description?: string
  children: React.ReactNode
}

export function SettingsSection({ title, description, children }: SettingsSectionProps) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-display font-bold text-luxury-text-primary">
          {title}
        </h2>
        {description && (
          <p className="text-sm text-luxury-text-secondary mt-1">{description}</p>
        )}
      </div>
      <div className="space-y-4">
        {children}
      </div>
    </div>
  )
}
