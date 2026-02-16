/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Luxury Design System Colors
        luxury: {
          // Background
          'obsidian': '#0a0a0f',
          'charcoal': '#151520',
          'card': 'rgba(15, 23, 42, 0.4)',

          // Accents
          'gold': '#d4af37',
          'indigo': '#6366f1',
          'cyan': '#06b6d4',
          'orange': '#f97316',
          'slate': '#64748b',

          // Text
          'text-primary': '#f8fafc',
          'text-secondary': '#94a3b8',

          // Border
          'border': 'rgba(255, 255, 255, 0.1)',
        },

        // Semantic Colors
        success: "#047857",
        warning: "#B45309",
        error: "#B91C1C",
        info: "#0EA5E9",
      },
      fontFamily: {
        'playfair': ["Playfair Display", "serif"],
        'inter': ["Inter", "sans-serif"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["Fira Code", "ui-monospace", "monospace"],
      },
      borderRadius: {
        lg: "12px",
        md: "8px",
        sm: "4px",
      },
      boxShadow: {
        "glow-gold": "0 0 15px rgba(212, 175, 55, 0.5), 0 0 30px rgba(212, 175, 55, 0.3)",
        "glow-indigo": "0 0 15px rgba(99, 102, 241, 0.5), 0 0 30px rgba(99, 102, 241, 0.3)",
        "glow-orange": "0 0 15px rgba(255, 144, 0, 0.5), 0 0 30px rgba(255, 144, 0, 0.3)",
        "glow-cyan": "0 0 15px rgba(67, 194, 210, 0.5), 0 0 30px rgba(67, 194, 210, 0.3)",
        "glow-luxury-indigo": "0 0 20px rgba(99, 102, 241, 0.4), 0 0 40px rgba(99, 102, 241, 0.2)",
      },
      animation: {
        "fade-in": "fade-in 0.6s ease-out forwards",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "breathing-glow": "breathing-glow 3s ease-in-out infinite",
        "scale-in": "scale-in 0.3s ease-out forwards",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 5px rgba(99, 102, 241, 0.5)" },
          "50%": { boxShadow: "0 0 20px rgba(99, 102, 241, 0.8)" },
        },
        "breathing-glow": {
          "0%, 100%": {
            boxShadow: "0 0 10px rgba(212, 175, 55, 0.3)",
            transform: "scale(1)",
          },
          "50%": {
            boxShadow: "0 0 30px rgba(212, 175, 55, 0.6)",
            transform: "scale(1.02)",
          },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.9)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
      },
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
      },
    },
  },
  plugins: [],
}
