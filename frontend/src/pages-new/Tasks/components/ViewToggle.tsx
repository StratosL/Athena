import { LayoutGrid, List } from "lucide-react"

type ViewMode = "matrix" | "list"

interface ViewToggleProps {
  value: ViewMode
  onChange: (mode: ViewMode) => void
}

export function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <div className="flex gap-1 backdrop-blur-md bg-luxury-card border border-luxury-border rounded-lg p-1">
      <button
        onClick={() => onChange("matrix")}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all text-sm font-medium ${
          value === "matrix"
            ? "bg-luxury-gold text-luxury-obsidian"
            : "text-luxury-text-secondary hover:text-luxury-text-primary hover:bg-white/5"
        }`}
      >
        <LayoutGrid className="w-4 h-4" />
        Matrix
      </button>
      <button
        onClick={() => onChange("list")}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all text-sm font-medium ${
          value === "list"
            ? "bg-luxury-gold text-luxury-obsidian"
            : "text-luxury-text-secondary hover:text-luxury-text-primary hover:bg-white/5"
        }`}
      >
        <List className="w-4 h-4" />
        List
      </button>
    </div>
  )
}
