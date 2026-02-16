/**
 * Glassmorphism Utility Hook
 * 
 * Returns Tailwind classes for premium glassmorphism effect
 */

export function useGlassmorphism() {
    return 'backdrop-blur-md bg-luxury-card border border-luxury-border rounded-xl'
}

// Alternative: Export as constant for non-hook usage
export const glassmorphismClasses = 'backdrop-blur-md bg-luxury-card border border-luxury-border rounded-xl'
