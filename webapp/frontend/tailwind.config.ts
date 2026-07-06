import type { Config } from "tailwindcss";

// Tokens live in app/globals.css as raw RGB triples; <alpha-value> keeps
// Tailwind opacity modifiers (bg-accent/10 etc.) working in both themes.
const token = (name: string) => `rgb(var(--color-${name}) / <alpha-value>)`;

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    // lib/scoreBands.ts carries bg-score-* class strings - without this glob
    // Tailwind never generates them and score badges render unstyled.
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: token("bg"),
        foreground: token("text"),
        surface: {
          DEFAULT: token("surface"),
          raised: token("surface-raised"),
        },
        border: {
          DEFAULT: token("border"),
          subtle: token("border-subtle"),
        },
        muted: token("text-muted"),
        subtle: token("text-subtle"),
        accent: {
          DEFAULT: token("accent"),
          hover: token("accent-hover"),
          foreground: token("accent-foreground"),
        },
        score: {
          high: token("score-high"),
          mid: token("score-mid"),
          low: token("score-low"),
        },
        warning: token("warning"),
        danger: token("danger"),
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "Georgia", "serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
