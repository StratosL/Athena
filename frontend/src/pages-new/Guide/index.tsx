/**
 * Guide Page
 *
 * User-facing guide explaining the three productivity techniques
 * built into Artemis (Eisenhower Matrix, 1-3-5 Rule, Pomodoro).
 * Encourages using one, two, or all three combined.
 *
 * Route: /guide
 */

import { motion } from "motion/react"
import { GlassCard, Button, Badge } from "@/design-system/components"
import { AppShell } from "@/pages-new/layout"
import { useNavigate } from "react-router-dom"

interface Technique {
  title: string
  tagline: string
  badge: { label: string; variant: "q1" | "q2" | "q3" | "q4" | "gold" | "default" }
  color: string
  glowClass: string
  iconPath: string
  what: string
  howItWorks: string[]
  benefits: string[]
  bestFor: string
  appRoute: string
  appRouteLabel: string
}

const techniques: Technique[] = [
  {
    title: "Eisenhower Matrix",
    tagline: "Know what matters",
    badge: { label: "Prioritize", variant: "q1" },
    color: "text-luxury-indigo",
    glowClass: "shadow-[0_0_20px_rgba(99,102,241,0.15)]",
    iconPath: "M3 3h7v7H3V3zm11 0h7v7h-7V3zM3 14h7v7H3v-7zm11 0h7v7h-7v-7z",
    what: "The Eisenhower Matrix helps you make strategic decisions about what to work on by sorting tasks into four quadrants based on urgency and importance. Instead of reacting to whatever feels pressing, you deliberately choose high-impact work.",
    howItWorks: [
      "Q1 — Urgent & Important: Do these first. Deadlines, crises, critical bugs.",
      "Q2 — Important, Not Urgent: Schedule these. Strategy, learning, long-term goals.",
      "Q3 — Urgent, Not Important: Delegate or batch. Meetings, minor requests.",
      "Q4 — Neither: Eliminate. Time-wasters, busywork, endless scrolling.",
    ],
    benefits: [
      "Shifts your focus from reactive to strategic work",
      "Identifies tasks you can delegate or drop entirely",
      "Improves long-term goal achievement",
    ],
    bestFor: "Deciding what to work on and what to ignore",
    appRoute: "/tasks",
    appRouteLabel: "Open Tasks",
  },
  {
    title: "1-3-5 Rule",
    tagline: "Plan with intention",
    badge: { label: "Plan", variant: "gold" },
    color: "text-luxury-gold",
    glowClass: "shadow-[0_0_20px_rgba(212,175,55,0.15)]",
    iconPath: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
    what: "The 1-3-5 Rule gives you a daily framework that prevents overwhelm while keeping you consistently productive. Each day you commit to a realistic set of tasks — no more, no less.",
    howItWorks: [
      "1 Major Task — Your most impactful work for the day (2-4 hours).",
      "3 Medium Tasks — Solid work items that take about an hour each.",
      "5 Small Tasks — Quick wins you can knock out in 15-30 minutes.",
    ],
    benefits: [
      "Prevents the paralysis of an endless to-do list",
      "Guarantees daily progress on your biggest priorities",
      "Gives you a satisfying sense of completion every evening",
    ],
    bestFor: "Morning planning and maintaining daily momentum",
    appRoute: "/daily-plan",
    appRouteLabel: "Open Daily Plan",
  },
  {
    title: "Pomodoro Technique",
    tagline: "Focus deeply",
    badge: { label: "Focus", variant: "q2" },
    color: "text-luxury-cyan",
    glowClass: "shadow-[0_0_20px_rgba(6,182,212,0.15)]",
    iconPath: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
    what: "The Pomodoro Technique breaks your work into focused 25-minute intervals separated by short breaks. The time constraint creates healthy urgency, fights procrastination, and keeps your mind fresh throughout the day.",
    howItWorks: [
      "Work for 25 minutes with complete focus on a single task.",
      "Take a 5-minute break to rest and recharge.",
      "After 4 pomodoros, take a longer 15-30 minute break.",
      "Repeat. Track your sessions to see your output grow.",
    ],
    benefits: [
      "Increases output by 25-35% compared to unstructured work",
      "Reduces mental fatigue through regular breaks",
      "Builds a visible record of your focused effort",
    ],
    bestFor: "Any task that needs sustained concentration",
    appRoute: "/pomodoro",
    appRouteLabel: "Open Pomodoro",
  },
]

export function Guide() {
  const navigate = useNavigate()

  return (
    <AppShell title="Guide" subtitle="Learn the methods behind Artemis">
      <div className="max-w-4xl mx-auto space-y-10">

        {/* Intro */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <GlassCard className="p-8">
            <h2 className="font-playfair text-2xl font-semibold text-luxury-text-primary mb-4">
              Three Techniques, Your Way
            </h2>
            <p className="text-luxury-text-secondary font-inter leading-relaxed mb-4">
              Artemis brings together three proven productivity methods that work
              beautifully on their own — and even better together. You don't have to
              use all of them. Pick the one that fits your style, combine two that
              complement each other, or run the full stack for a complete system.
            </p>
            <p className="text-luxury-text-secondary font-inter leading-relaxed">
              The goal isn't to add complexity to your day. It's to remove the
              guesswork so you always know <span className="text-luxury-gold font-medium">what</span> to
              work on, <span className="text-luxury-gold font-medium">how much</span> to
              take on, and <span className="text-luxury-gold font-medium">when</span> to
              focus.
            </p>
          </GlassCard>
        </motion.section>

        {/* Technique Cards */}
        {techniques.map((tech, index) => (
          <motion.section
            key={tech.title}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * (index + 1) }}
          >
            <GlassCard className={`p-8 ${tech.glowClass}`}>
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-luxury-card border border-luxury-border flex items-center justify-center flex-shrink-0">
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d={tech.iconPath}
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className={tech.color}
                      />
                    </svg>
                  </div>
                  <div>
                    <h3 className={`font-playfair text-xl font-semibold ${tech.color}`}>
                      {tech.title}
                    </h3>
                    <p className="text-sm text-luxury-text-secondary font-inter">
                      {tech.tagline}
                    </p>
                  </div>
                </div>
                <Badge variant={tech.badge.variant}>{tech.badge.label}</Badge>
              </div>

              {/* What it does */}
              <p className="text-luxury-text-secondary font-inter leading-relaxed mb-6">
                {tech.what}
              </p>

              {/* How it works */}
              <div className="mb-6">
                <h4 className="font-playfair text-sm font-semibold text-luxury-text-primary uppercase tracking-wider mb-3">
                  How It Works
                </h4>
                <ul className="space-y-2">
                  {tech.howItWorks.map((step, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-luxury-text-secondary font-inter">
                      <span className={`mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${tech.color.replace("text-", "bg-")}`} />
                      {step}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Benefits */}
              <div className="mb-6">
                <h4 className="font-playfair text-sm font-semibold text-luxury-text-primary uppercase tracking-wider mb-3">
                  Why It Works
                </h4>
                <ul className="space-y-2">
                  {tech.benefits.map((benefit, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-luxury-text-secondary font-inter">
                      <span className="mt-1 text-luxury-gold">&#10003;</span>
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Best for + CTA */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-luxury-border">
                <p className="text-xs text-luxury-text-secondary font-inter">
                  <span className="text-luxury-text-primary font-medium">Best for:</span>{" "}
                  {tech.bestFor}
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(tech.appRoute)}
                >
                  {tech.appRouteLabel}
                </Button>
              </div>
            </GlassCard>
          </motion.section>
        ))}

        {/* Combining Techniques */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <GlassCard className="p-8 shadow-[0_0_30px_rgba(212,175,55,0.1)]">
            <h2 className="font-playfair text-2xl font-semibold text-luxury-gold mb-6">
              Better Together
            </h2>

            <div className="space-y-6">
              <div>
                <h4 className="font-playfair text-base font-semibold text-luxury-text-primary mb-2">
                  Use one technique
                </h4>
                <p className="text-sm text-luxury-text-secondary font-inter leading-relaxed">
                  Even a single method will make a difference. If you're overwhelmed by
                  your task list, start with the <span className="text-luxury-indigo font-medium">Eisenhower Matrix</span> to
                  cut through the noise. If you struggle to start working, the <span className="text-luxury-cyan font-medium">Pomodoro
                  Timer</span> gives you a clear on-ramp. If planning your day feels chaotic,
                  the <span className="text-luxury-gold font-medium">1-3-5 Rule</span> brings instant clarity.
                </p>
              </div>

              <div>
                <h4 className="font-playfair text-base font-semibold text-luxury-text-primary mb-2">
                  Combine two techniques
                </h4>
                <p className="text-sm text-luxury-text-secondary font-inter leading-relaxed">
                  Pair the <span className="text-luxury-indigo font-medium">Matrix</span> with
                  the <span className="text-luxury-gold font-medium">1-3-5 Rule</span> to
                  prioritize your backlog and then pull the right tasks into each day.
                  Or pair the <span className="text-luxury-gold font-medium">1-3-5 Rule</span> with
                  the <span className="text-luxury-cyan font-medium">Pomodoro Timer</span> to
                  plan your day and execute with focused intensity.
                </p>
              </div>

              <div>
                <h4 className="font-playfair text-base font-semibold text-luxury-text-primary mb-2">
                  Run the full stack
                </h4>
                <p className="text-sm text-luxury-text-secondary font-inter leading-relaxed">
                  When you use all three together, you get a complete productivity
                  system: the Matrix decides <em>what matters</em>, the 1-3-5 Rule
                  decides <em>what's on your plate today</em>, and Pomodoro decides <em>how
                  you'll execute</em>. Prioritize, plan, focus — that's the Artemis cycle.
                </p>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-luxury-border text-center">
              <p className="text-luxury-text-secondary font-inter text-sm mb-5">
                There's no wrong way to start. Pick what feels right and build from there.
              </p>
              <Button variant="primary" size="lg" onClick={() => navigate("/")}>
                Go to Dashboard
              </Button>
            </div>
          </GlassCard>
        </motion.section>
      </div>
    </AppShell>
  )
}

export default Guide
