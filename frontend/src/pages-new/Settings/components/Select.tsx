import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"

interface SelectOption {
  value: string
  label: string
}

interface SelectProps {
  value: string
  onChange: (value: string) => void
  options: SelectOption[]
  label?: string
  description?: string
  disabled?: boolean
}

export function Select({
  value,
  onChange,
  options,
  label,
  description,
  disabled,
}: SelectProps) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-luxury-text-primary">
          {label}
        </label>
      )}
      {description && (
        <p className="text-sm text-luxury-text-secondary">{description}</p>
      )}

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={cn(
          glassmorphismClasses,
          "w-full px-4 py-2 text-luxury-text-primary",
          "transition-all duration-300",
          "focus:outline-none focus:ring-2 focus:ring-luxury-indigo focus:border-luxury-indigo",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "cursor-pointer"
        )}
      >
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
            className="bg-luxury-obsidian text-luxury-text-primary"
          >
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}
