/**
 * Confetti Animation Utilities
 * 
 * Celebration effects using canvas-confetti with luxury colors
 */

import confetti from 'canvas-confetti'

/**
 * Trigger subtle confetti animation for task completion
 */
export function celebrateTaskComplete() {
    confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.6 },
        colors: ['#d4af37', '#6366f1', '#06b6d4'], // Gold, Indigo, Cyan
    })
}

/**
 * Trigger full celebration for session complete
 */
export function celebrateSessionComplete() {
    const duration = 2000
    const end = Date.now() + duration

    const frame = () => {
        confetti({
            particleCount: 3,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: ['#d4af37', '#6366f1'],
        })

        confetti({
            particleCount: 3,
            angle: 120,
            spread: 55,
            origin: { x: 1 },
            colors: ['#d4af37', '#6366f1'],
        })

        if (Date.now() < end) {
            requestAnimationFrame(frame)
        }
    }

    frame()
}

/**
 * Trigger celebration for daily plan completion
 */
export function celebrateDailyPlanComplete() {
    confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#d4af37', '#6366f1', '#06b6d4', '#f97316'],
    })
}
