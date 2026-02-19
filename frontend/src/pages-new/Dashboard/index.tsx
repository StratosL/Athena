import { useState } from "react"
import { Plus, X } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { AppShell } from "../layout"
import {
  DashboardPlanColumn,
  DashboardMatrixColumn,
  DashboardStatsBar,
} from "./components"

export function Dashboard() {
  const [fabOpen, setFabOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <AppShell
      title="Artemis"
      subtitle="Achieve sustainable, high-quality productivity"
    >
      {/* 2-Column Hub — Plan left, Matrix right; single-column on mobile */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <DashboardPlanColumn />
        <DashboardMatrixColumn />
      </div>

      {/* Bottom: Daily Stats Bar */}
      <DashboardStatsBar />

      {/* Footer */}
      <footer className="mt-12 text-center text-luxury-text-secondary text-sm">
        <p>Artemis v 0.6.0</p>
      </footer>

      {/* Mobile FAB for quick actions */}
      <div className="fixed bottom-20 right-4 z-50 lg:hidden">
        {fabOpen && (
          <div className="mb-3 flex flex-col gap-2 items-end">
            <button
              onClick={() => { setFabOpen(false); navigate("/tasks") }}
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-luxury-card backdrop-blur-md border border-luxury-border text-luxury-text-primary text-sm shadow-lg"
            >
              Add Task
            </button>
            <button
              onClick={() => { setFabOpen(false); navigate("/pomodoro") }}
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-luxury-card backdrop-blur-md border border-luxury-border text-luxury-text-primary text-sm shadow-lg"
            >
              Start Pomodoro
            </button>
            <button
              onClick={() => { setFabOpen(false); navigate("/daily-plan") }}
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-luxury-card backdrop-blur-md border border-luxury-border text-luxury-text-primary text-sm shadow-lg"
            >
              Plan Day
            </button>
          </div>
        )}
        <button
          onClick={() => setFabOpen((v) => !v)}
          className="w-14 h-14 rounded-full bg-luxury-gold text-luxury-obsidian flex items-center justify-center shadow-lg shadow-luxury-gold/30 transition-transform active:scale-95"
        >
          {fabOpen ? <X className="w-6 h-6" /> : <Plus className="w-6 h-6" />}
        </button>
      </div>
    </AppShell>
  )
}
