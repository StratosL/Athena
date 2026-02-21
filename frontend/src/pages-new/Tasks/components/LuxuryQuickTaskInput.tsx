import { useState, type KeyboardEvent } from "react"
import { Plus } from "lucide-react"
import { Button, Input } from "@/design-system/components"
import { cn } from "@/lib/utils"
import { glassmorphismClasses } from "@/design-system"

interface LuxuryQuickTaskInputProps {
  onSubmit: (title: string, quadrant: 1 | 2 | 3 | 4) => void
  defaultQuadrant?: 1 | 2 | 3 | 4
  placeholder?: string
  className?: string
}

export function LuxuryQuickTaskInput({
  onSubmit,
  defaultQuadrant = 1,
  placeholder = "Add a task...",
  className,
}: LuxuryQuickTaskInputProps) {
  const [title, setTitle] = useState("")
  const [quadrant, setQuadrant] = useState<1 | 2 | 3 | 4>(defaultQuadrant)

  const handleSubmit = () => {
    if (title.trim()) {
      onSubmit(title.trim(), quadrant)
      setTitle("")
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className={cn("flex flex-col sm:flex-row gap-2", className)}>
      <Input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="flex-1"
      />
      <div className="flex gap-2">
        <select
          value={quadrant}
          onChange={(e) => setQuadrant(Number(e.target.value) as 1 | 2 | 3 | 4)}
          className={cn(
            glassmorphismClasses,
            "px-3 py-2 text-luxury-text-primary text-sm flex-1 sm:flex-initial",
            "focus:outline-none focus:ring-2 focus:ring-luxury-indigo"
          )}
        >
          <option value={1}>Q1: Do First</option>
          <option value={2}>Q2: Schedule</option>
          <option value={3}>Q3: Delegate</option>
          <option value={4}>Q4: Eliminate</option>
        </select>
        <Button variant="primary" size="md" onClick={handleSubmit} disabled={!title.trim()}>
          <Plus className="w-4 h-4 mr-1" />
          Add
        </Button>
      </div>
    </div>
  )
}
