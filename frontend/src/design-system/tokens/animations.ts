/**
 * Animation Constants
 * 
 * Durations, easing functions, and animation configurations
 */

export const animations = {
    // Durations (in milliseconds)
    duration: {
        micro: 150,
        fast: 200,
        normal: 300,
        slow: 600,
        breathing: 3000,  // 3-second breathing cycle
    },

    // Easing functions
    easing: {
        easeOut: 'cubic-bezier(0.16, 1, 0.3, 1)',
        easeIn: 'cubic-bezier(0.7, 0, 0.84, 0)',
        easeInOut: 'cubic-bezier(0.65, 0, 0.35, 1)',
        spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
    },

    // Framer Motion spring configs
    spring: {
        gentle: { type: 'spring', stiffness: 100, damping: 15 },
        bouncy: { type: 'spring', stiffness: 300, damping: 20 },
        stiff: { type: 'spring', stiffness: 400, damping: 30 },
    },
} as const

export type Animations = typeof animations
