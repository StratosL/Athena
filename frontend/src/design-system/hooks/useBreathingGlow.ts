/**
 * Breathing Glow Animation Hook
 * 
 * Returns className for 3-second breathing glow cycle
 */

export function useBreathingGlow(color: 'gold' | 'indigo' | 'cyan' | 'orange' = 'gold') {
    const glowMap = {
        gold: 'animate-breathing-glow shadow-glow-gold',
        indigo: 'animate-breathing-glow shadow-glow-luxury-indigo',
        cyan: 'animate-breathing-glow shadow-glow-cyan',
        orange: 'animate-breathing-glow shadow-glow-orange',
    }

    return glowMap[color]
}
