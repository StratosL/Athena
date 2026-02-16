/**
 * Deep Cozy Luxury Color Palette
 * 
 * Design System: Atmospheric Minimalist with Premium Glassmorphism
 * Source: DESIGN_SYSTEM.md
 */

export const colors = {
  // Background Colors
  background: {
    obsidian: '#0a0a0f',      // Primary background
    charcoal: '#151520',       // Gradient end
    card: 'rgba(15, 23, 42, 0.4)', // Glassmorphism card background
  },
  
  // Accent Colors
  accent: {
    gold: '#d4af37',           // Champagne Gold - active states, celebrations
    indigo: '#6366f1',         // Electric Indigo - work mode, Q1, primary
    cyan: '#06b6d4',           // Cyan - Q2, scheduled tasks
    orange: '#f97316',         // Orange - Q3, delegated tasks
    slate: '#64748b',          // Slate - Q4, low priority
  },
  
  // Text Colors
  text: {
    primary: '#f8fafc',        // White - primary text
    secondary: '#94a3b8',      // Muted - secondary text
  },
  
  // Border & Effects
  border: 'rgba(255, 255, 255, 0.1)', // 1px gradient borders
  
  // Glow Effects (for box-shadow)
  glow: {
    gold: 'radial-gradient(circle, rgba(212, 175, 55, 0.15) 0%, transparent 70%)',
    indigo: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)',
    cyan: 'radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%)',
    orange: 'radial-gradient(circle, rgba(249, 115, 22, 0.15) 0%, transparent 70%)',
  },
} as const

export type ColorPalette = typeof colors
