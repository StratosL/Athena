/**
 * Typography System
 * 
 * Header Font: Playfair Display (sophisticated serif)
 * Body Font: Inter (clean sans-serif)
 * 
 * Source: DESIGN_SYSTEM.md
 */

export const typography = {
    fonts: {
        header: "'Playfair Display', serif",
        body: "'Inter', sans-serif",
    },

    sizes: {
        logo: '72px',
        pageTitle: '48px',
        sectionHeader: '28px',
        body: '16px',
        small: '14px',
        tiny: '12px',
    },

    weights: {
        regular: 400,
        medium: 500,
        bold: 700,
    },

    lineHeights: {
        tight: 1.2,
        normal: 1.5,
        relaxed: 1.75,
    },
} as const

export type Typography = typeof typography
