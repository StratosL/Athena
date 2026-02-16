/**
 * BreakModeScreen Component
 *
 * Full-screen overlay with warm gold glow for break periods.
 * Features a breathing circle animation, wellness suggestions,
 * motivational messages, and break countdown timer.
 */

import { useState, useEffect, useMemo } from "react"
import { motion, AnimatePresence } from "motion/react"
import { GlassCard, Button } from "@/design-system/components"
import { useTimerStore } from "@/stores/timerStore"

interface BreakModeScreenProps {
  isOpen: boolean
  onSkip: () => void
}

interface WellnessActivity {
  title: string
  description: string
  icon: string
}

const wellnessActivities: WellnessActivity[] = [
  {
    title: "Stretch",
    description: "Stand up and stretch your arms above your head. Roll your shoulders back.",
    icon: "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
  },
  {
    title: "Hydrate",
    description: "Drink a full glass of water. Your brain works better when hydrated.",
    icon: "M12 2.69l5.66 5.66a8 8 0 11-11.31 0z",
  },
  {
    title: "Rest Your Eyes",
    description: "Look at something 20 feet away for 20 seconds. Blink slowly a few times.",
    icon: "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z",
  },
  {
    title: "Take a Walk",
    description: "Walk around the room or step outside. Even 2 minutes of movement helps.",
    icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
  },
  {
    title: "Deep Breathe",
    description: "Inhale for 4 seconds, hold for 4, exhale for 4. Repeat three times.",
    icon: "M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  },
]

const motivationalMessages: string[] = [
  "You are making progress. Every session counts.",
  "Rest is not laziness. It is preparation for excellence.",
  "The mind needs space to process what it has learned.",
  "Small breaks fuel big breakthroughs.",
  "You have earned this moment of peace.",
  "Consistency is the bridge between goals and accomplishment.",
  "Your focus is a superpower. Recharge it wisely.",
  "Great work is built one session at a time.",
  "Pause, breathe, and return stronger.",
  "The best ideas come in moments of rest.",
]

function formatBreakTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, "0")}`
}

export function BreakModeScreen({ isOpen, onSkip }: BreakModeScreenProps) {
  const remainingSeconds = useTimerStore((s) => s.remainingSeconds)

  // Pick a random activity and message on mount (stable for session)
  const [randomIndices] = useState(() => ({
    activity: Math.floor(Math.random() * wellnessActivities.length),
    message: Math.floor(Math.random() * motivationalMessages.length),
  }))

  const activity = useMemo(
    () => wellnessActivities[randomIndices.activity],
    [randomIndices.activity]
  )
  const message = useMemo(
    () => motivationalMessages[randomIndices.message],
    [randomIndices.message]
  )

  // Cycle breathing phase text
  const [breathPhase, setBreathPhase] = useState<"Breathe in" | "Hold" | "Breathe out">("Breathe in")

  useEffect(() => {
    if (!isOpen) return

    // 4s inhale, 4s hold, 4s exhale cycle
    const phases: Array<"Breathe in" | "Hold" | "Breathe out"> = [
      "Breathe in",
      "Hold",
      "Breathe out",
    ]
    let index = 0

    const interval = setInterval(() => {
      index = (index + 1) % phases.length
      setBreathPhase(phases[index])
    }, 4000)

    return () => clearInterval(interval)
  }, [isOpen])

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Background with warm gold glow */}
          <div className="absolute inset-0 bg-luxury-obsidian" />
          <div className="absolute inset-0 bg-gradient-radial from-luxury-gold/10 via-transparent to-transparent" />

          {/* Ambient glow orbs */}
          <motion.div
            className="absolute w-96 h-96 rounded-full bg-luxury-gold/5 blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />

          {/* Content */}
          <div className="relative z-10 flex flex-col items-center max-w-lg mx-4">
            {/* Breathing Circle */}
            <div className="relative mb-8">
              <motion.div
                className="w-40 h-40 rounded-full border-2 border-luxury-gold/40 flex items-center justify-center"
                animate={{
                  scale: [1, 1.3, 1.3, 1],
                  borderColor: [
                    "rgba(212, 175, 55, 0.4)",
                    "rgba(212, 175, 55, 0.8)",
                    "rgba(212, 175, 55, 0.8)",
                    "rgba(212, 175, 55, 0.4)",
                  ],
                  boxShadow: [
                    "0 0 20px rgba(212, 175, 55, 0.1)",
                    "0 0 60px rgba(212, 175, 55, 0.3)",
                    "0 0 60px rgba(212, 175, 55, 0.3)",
                    "0 0 20px rgba(212, 175, 55, 0.1)",
                  ],
                }}
                transition={{
                  duration: 12,
                  repeat: Infinity,
                  ease: "easeInOut",
                  times: [0, 0.33, 0.66, 1],
                }}
              >
                <motion.div
                  className="w-24 h-24 rounded-full bg-luxury-gold/10 backdrop-blur-sm flex items-center justify-center"
                  animate={{
                    scale: [1, 1.2, 1.2, 1],
                    backgroundColor: [
                      "rgba(212, 175, 55, 0.1)",
                      "rgba(212, 175, 55, 0.2)",
                      "rgba(212, 175, 55, 0.2)",
                      "rgba(212, 175, 55, 0.1)",
                    ],
                  }}
                  transition={{
                    duration: 12,
                    repeat: Infinity,
                    ease: "easeInOut",
                    times: [0, 0.33, 0.66, 1],
                  }}
                >
                  <span className="text-luxury-gold font-inter text-sm font-medium">
                    {breathPhase}
                  </span>
                </motion.div>
              </motion.div>
            </div>

            {/* Break Timer */}
            <motion.div
              className="mb-6 text-center"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <p className="text-luxury-text-secondary font-inter text-sm uppercase tracking-wider mb-1">
                Break Time Remaining
              </p>
              <p className="text-4xl font-playfair font-semibold text-luxury-text-primary">
                {formatBreakTime(remainingSeconds)}
              </p>
            </motion.div>

            {/* Wellness Activity Card */}
            <motion.div
              className="w-full mb-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <GlassCard hoverable={false} className="p-6 text-center">
                <div className="w-10 h-10 mx-auto mb-3 rounded-full bg-luxury-gold/20 flex items-center justify-center">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d={activity.icon}
                      stroke="#d4af37"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
                <h3 className="font-playfair text-lg font-semibold text-luxury-text-primary mb-1">
                  {activity.title}
                </h3>
                <p className="text-sm text-luxury-text-secondary font-inter">
                  {activity.description}
                </p>
              </GlassCard>
            </motion.div>

            {/* Motivational Message */}
            <motion.p
              className="text-luxury-text-secondary font-inter text-sm italic text-center mb-8 max-w-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              "{message}"
            </motion.p>

            {/* Skip Button */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              <Button variant="ghost" size="md" onClick={onSkip}>
                Skip Break
              </Button>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default BreakModeScreen
