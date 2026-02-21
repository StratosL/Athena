import { cn } from "@/lib/utils"
import { GlassCard } from "@/design-system/components"
import type { PomodoroSession } from "@/lib/api"

interface LuxurySessionListProps {
  sessions: PomodoroSession[]
  className?: string
}

export function LuxurySessionList({ sessions, className }: LuxurySessionListProps) {
  return (
    <GlassCard className={cn("p-5", className)} hoverable={false}>
      <h3 className="text-lg font-playfair font-semibold text-luxury-text-primary mb-3">
        Recent Sessions
      </h3>

      {sessions.length === 0 ? (
        <p className="text-base text-luxury-text-secondary">
          No sessions yet. Start your first pomodoro!
        </p>
      ) : (
        <div className="space-y-2">
          {sessions.map((session) => (
            <div
              key={session.id}
              className="flex items-center justify-between p-3 rounded-lg border border-luxury-border"
            >
              <div>
                <p className="text-base text-luxury-text-primary">
                  {session.completed ? (
                    <span className="text-green-400 mr-1">●</span>
                  ) : (
                    <span className="text-red-400 mr-1">●</span>
                  )}
                  {session.duration_minutes} min
                </p>
                <p className="text-sm text-luxury-text-secondary">
                  {new Date(session.started_at).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </GlassCard>
  )
}
