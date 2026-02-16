/**
 * Chart theme constants for Recharts - Luxury Design System.
 * Uses Deep Cozy Luxury palette on obsidian/charcoal backgrounds.
 */

export const LUXURY_CHART_COLORS = {
  indigo: '#6366f1',
  cyan: '#06b6d4',
  orange: '#f97316',
  gold: '#d4af37',
  slate: '#64748b',
  success: '#22c55e',
  error: '#ef4444',
} as const

export const LUXURY_QUADRANT_COLORS: Record<number, string> = {
  1: LUXURY_CHART_COLORS.indigo,
  2: LUXURY_CHART_COLORS.cyan,
  3: LUXURY_CHART_COLORS.orange,
  4: LUXURY_CHART_COLORS.slate,
}

export const LUXURY_CHART_THEME = {
  background: '#0a0a0f',
  surface: 'rgba(15, 23, 42, 0.4)',
  text: '#f8fafc',
  textSecondary: '#94a3b8',
  textMuted: '#64748b',
  border: 'rgba(255, 255, 255, 0.1)',
  gridStroke: 'rgba(255, 255, 255, 0.06)',
} as const

export const LUXURY_TOOLTIP_STYLE = {
  backgroundColor: 'rgba(15, 23, 42, 0.9)',
  backdropFilter: 'blur(12px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '12px',
  color: LUXURY_CHART_THEME.text,
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
} as const
