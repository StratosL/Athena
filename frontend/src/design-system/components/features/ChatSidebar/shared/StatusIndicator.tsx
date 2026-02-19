import { motion } from "motion/react"

export function StatusIndicator({ status }: { status: string }) {
  if (status === "recording") {
    return (
      <div className="flex justify-start">
        <div className="backdrop-blur-md bg-luxury-card border border-luxury-border rounded-2xl px-4 py-3 flex items-center gap-2">
          <motion.div
            className="w-2.5 h-2.5 rounded-full bg-red-500"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
          <span className="text-luxury-text-secondary text-xs">Recording...</span>
        </div>
      </div>
    )
  }

  if (status === "transcribing") {
    return (
      <div className="flex justify-start">
        <div className="backdrop-blur-md bg-luxury-card border border-luxury-border rounded-2xl px-4 py-3 flex items-center gap-2">
          <motion.div
            className="w-2.5 h-2.5 rounded-full bg-luxury-indigo"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
          <span className="text-luxury-text-secondary text-xs">Transcribing...</span>
        </div>
      </div>
    )
  }

  if (status === "thinking") {
    return (
      <div className="flex justify-start">
        <div className="backdrop-blur-md bg-luxury-card border border-luxury-border rounded-2xl px-4 py-3 flex items-center gap-2">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="w-2 h-2 rounded-full bg-luxury-indigo"
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
              />
            ))}
          </div>
          <span className="text-luxury-text-secondary text-xs">Athena is thinking...</span>
        </div>
      </div>
    )
  }

  if (status === "speaking") {
    return (
      <div className="flex justify-start">
        <div className="backdrop-blur-md bg-luxury-card border border-luxury-border rounded-2xl px-4 py-3 flex items-center gap-2">
          <div className="flex items-end gap-0.5 h-4">
            {[0, 1, 2, 3].map((i) => (
              <motion.div
                key={i}
                className="w-1 bg-luxury-indigo rounded-full"
                animate={{ scaleY: [0.3, 1, 0.3] }}
                transition={{
                  duration: 0.8,
                  repeat: Infinity,
                  delay: i * 0.15,
                }}
                style={{ height: 16, originY: 1 }}
              />
            ))}
          </div>
          <span className="text-luxury-text-secondary text-xs">Speaking...</span>
        </div>
      </div>
    )
  }

  return null
}
