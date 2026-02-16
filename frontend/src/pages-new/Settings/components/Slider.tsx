import { cn } from "@/lib/utils"

interface SliderProps {
  value: number
  onChange: (value: number) => void
  min: number
  max: number
  step?: number
  label?: string
  description?: string
  unit?: string
  disabled?: boolean
}

export function Slider({
  value,
  onChange,
  min,
  max,
  step = 1,
  label,
  description,
  unit,
  disabled,
}: SliderProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div>
          {label && (
            <label className="block text-sm font-medium text-luxury-text-primary">
              {label}
            </label>
          )}
          {description && (
            <p className="text-sm text-luxury-text-secondary mt-1">{description}</p>
          )}
        </div>
        <span className="text-sm font-medium text-luxury-gold">
          {value}{unit}
        </span>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        disabled={disabled}
        className={cn(
          "w-full h-2 rounded-lg appearance-none cursor-pointer",
          "bg-luxury-border",
          "focus:outline-none focus:ring-2 focus:ring-luxury-gold",
          "[&::-webkit-slider-thumb]:appearance-none",
          "[&::-webkit-slider-thumb]:w-4",
          "[&::-webkit-slider-thumb]:h-4",
          "[&::-webkit-slider-thumb]:rounded-full",
          "[&::-webkit-slider-thumb]:bg-luxury-gold",
          "[&::-webkit-slider-thumb]:shadow-glow-gold",
          "[&::-webkit-slider-thumb]:cursor-pointer",
          "[&::-moz-range-thumb]:w-4",
          "[&::-moz-range-thumb]:h-4",
          "[&::-moz-range-thumb]:rounded-full",
          "[&::-moz-range-thumb]:bg-luxury-gold",
          "[&::-moz-range-thumb]:border-0",
          "[&::-moz-range-thumb]:cursor-pointer",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      />
    </div>
  )
}
