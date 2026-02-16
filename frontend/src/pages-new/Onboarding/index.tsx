/**
 * Onboarding Screen
 *
 * Multi-step wizard introducing new users to Artemis.
 * Step 1: Welcome with branding
 * Step 2: Feature highlights (Eisenhower, 1-3-5, Pomodoro)
 * Step 3: Get started CTA with confetti
 *
 * Saves completion flag to localStorage. Route: /onboarding
 */

import { useState, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "motion/react"
import { GlassCard, Button } from "@/design-system/components"
import { celebrateTaskComplete } from "@/design-system/animations/confetti"

const ONBOARDING_KEY = "onboarding-complete"
const TOTAL_STEPS = 3

interface FeatureHighlight {
  title: string
  description: string
  color: string
  glowClass: string
  iconPath: string
}

const features: FeatureHighlight[] = [
  {
    title: "Eisenhower Matrix",
    description:
      "Prioritize your tasks by urgency and importance. Focus on what truly matters and stop wasting time on distractions.",
    color: "text-luxury-indigo",
    glowClass: "shadow-[0_0_20px_rgba(99,102,241,0.3)]",
    iconPath:
      "M3 3h7v7H3V3zm11 0h7v7h-7V3zM3 14h7v7H3v-7zm11 0h7v7h-7v-7z",
  },
  {
    title: "1-3-5 Rule",
    description:
      "Plan each day with intention: 1 major task, 3 medium tasks, and 5 small tasks. Never feel overwhelmed again.",
    color: "text-luxury-gold",
    glowClass: "shadow-[0_0_20px_rgba(212,175,55,0.3)]",
    iconPath:
      "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
  },
  {
    title: "Pomodoro Timer",
    description:
      "Work in focused 25-minute sessions with built-in breaks. Track your sessions and build unstoppable momentum.",
    color: "text-luxury-cyan",
    glowClass: "shadow-[0_0_20px_rgba(6,182,212,0.3)]",
    iconPath:
      "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
  },
]

export function Onboarding() {
  const [currentStep, setCurrentStep] = useState(0)
  const navigate = useNavigate()

  const handleNext = useCallback(() => {
    if (currentStep < TOTAL_STEPS - 1) {
      setCurrentStep((prev) => prev + 1)
    }
  }, [currentStep])

  const handleBack = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1)
    }
  }, [currentStep])

  const handleComplete = useCallback(() => {
    celebrateTaskComplete()
    localStorage.setItem(ONBOARDING_KEY, "true")

    // Small delay so user can see the confetti
    setTimeout(() => {
      navigate("/")
    }, 800)
  }, [navigate])

  return (
    <div className="min-h-screen bg-luxury-obsidian flex flex-col items-center justify-center p-6">
      {/* Ambient background */}
      <div className="fixed inset-0 bg-gradient-radial from-luxury-indigo/5 via-transparent to-transparent pointer-events-none" />

      {/* Step Content */}
      <div className="relative z-10 w-full max-w-2xl">
        <AnimatePresence mode="wait">
          {/* Step 1: Welcome */}
          {currentStep === 0 && (
            <motion.div
              key="step-1"
              className="flex flex-col items-center text-center"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
            >
              {/* Logo / Icon */}
              <motion.div
                className="w-20 h-20 rounded-full bg-gradient-to-br from-luxury-indigo to-luxury-gold flex items-center justify-center mb-8 shadow-[0_0_40px_rgba(212,175,55,0.3)]"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{
                  delay: 0.2,
                  type: "spring",
                  stiffness: 200,
                  damping: 15,
                }}
              >
                <svg
                  width="36"
                  height="36"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                    stroke="white"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </motion.div>

              <motion.h1
                className="font-playfair text-5xl font-bold text-luxury-text-primary mb-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                Artemis
              </motion.h1>

              <motion.p
                className="text-xl text-luxury-text-secondary font-inter mb-3 max-w-md"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                Your personal productivity command center
              </motion.p>

              <motion.p
                className="text-sm text-luxury-text-secondary/70 font-inter mb-10 max-w-sm"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                Three proven methodologies, one elegant interface. Prioritize,
                plan, and focus with precision.
              </motion.p>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
              >
                <Button variant="primary" size="lg" onClick={handleNext}>
                  Get Started
                </Button>
              </motion.div>
            </motion.div>
          )}

          {/* Step 2: Feature Highlights */}
          {currentStep === 1 && (
            <motion.div
              key="step-2"
              className="flex flex-col items-center"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
            >
              <h2 className="font-playfair text-3xl font-semibold text-luxury-text-primary mb-2 text-center">
                Three Powerful Methods
              </h2>
              <p className="text-luxury-text-secondary font-inter mb-8 text-center">
                Combined into one seamless workflow
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mb-8">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 + index * 0.15 }}
                  >
                    <GlassCard
                      hoverable
                      className={`p-5 text-center h-full ${feature.glowClass}`}
                    >
                      <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-luxury-card border border-luxury-border flex items-center justify-center">
                        <svg
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            d={feature.iconPath}
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className={feature.color}
                          />
                        </svg>
                      </div>
                      <h3
                        className={`font-playfair text-lg font-semibold mb-2 ${feature.color}`}
                      >
                        {feature.title}
                      </h3>
                      <p className="text-xs text-luxury-text-secondary font-inter leading-relaxed">
                        {feature.description}
                      </p>
                    </GlassCard>
                  </motion.div>
                ))}
              </div>

              <div className="flex gap-3">
                <Button variant="ghost" onClick={handleBack}>
                  Back
                </Button>
                <Button variant="primary" onClick={handleNext}>
                  Next
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Get Started */}
          {currentStep === 2 && (
            <motion.div
              key="step-3"
              className="flex flex-col items-center text-center"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
            >
              <motion.div
                className="w-16 h-16 rounded-full bg-luxury-gold/20 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(212,175,55,0.3)]"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{
                  delay: 0.2,
                  type: "spring",
                  stiffness: 200,
                  damping: 12,
                }}
              >
                <svg
                  width="28"
                  height="28"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                    stroke="#d4af37"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </motion.div>

              <motion.h2
                className="font-playfair text-3xl font-semibold text-luxury-text-primary mb-3"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                You are Ready
              </motion.h2>

              <motion.p
                className="text-luxury-text-secondary font-inter mb-8 max-w-sm"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                Start by creating your first task or setting up your daily plan.
                Artemis will guide you every step of the way.
              </motion.p>

              <motion.div
                className="flex gap-3"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <Button variant="ghost" onClick={handleBack}>
                  Back
                </Button>
                <Button variant="primary" size="lg" onClick={handleComplete}>
                  Launch Artemis
                </Button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Progress Dots */}
      <div className="relative z-10 flex gap-2 mt-12">
        {Array.from({ length: TOTAL_STEPS }).map((_, index) => (
          <motion.button
            key={index}
            className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
              index === currentStep
                ? "bg-luxury-gold shadow-[0_0_10px_rgba(212,175,55,0.5)]"
                : "bg-luxury-border"
            }`}
            onClick={() => setCurrentStep(index)}
            whileHover={{ scale: 1.3 }}
            aria-label={`Go to step ${index + 1}`}
          />
        ))}
      </div>
    </div>
  )
}

export default Onboarding
