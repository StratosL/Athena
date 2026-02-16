/**
 * Page Transition Configurations
 * 
 * Framer Motion transition configs for page animations
 */

export const pageTransitions = {
    // Fade in/out transition
    fade: {
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        exit: { opacity: 0 },
        transition: { duration: 0.3 },
    },

    // Slide up transition
    slideUp: {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        exit: { opacity: 0, y: -20 },
        transition: { type: 'spring', stiffness: 100, damping: 15 },
    },

    // Scale transition
    scale: {
        initial: { opacity: 0, scale: 0.95 },
        animate: { opacity: 1, scale: 1 },
        exit: { opacity: 0, scale: 0.95 },
        transition: { duration: 0.2 },
    },
} as const

export type PageTransition = keyof typeof pageTransitions
