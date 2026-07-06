'use client'

import { Moon, Sun } from 'lucide-react'

// Stateless by design: the active icon is chosen purely by CSS against
// html[data-theme] (see .cw-dark-only / .cw-light-only in globals.css), so
// the server render is identical to the client render regardless of the
// visitor's saved theme - no mounted-state dance, no hydration mismatch.
export function ThemeToggle({ className = '' }: { className?: string }) {
  return (
    <button
      type="button"
      aria-label="Toggle light or dark theme"
      onClick={() => {
        const root = document.documentElement
        const next = root.dataset.theme === 'light' ? 'dark' : 'light'
        root.dataset.theme = next
        try {
          localStorage.setItem('cw-theme', next)
        } catch {
          /* private mode - theme still applies for this page view */
        }
      }}
      className={`inline-flex items-center justify-center w-9 h-9 rounded-lg border border-border bg-surface text-muted hover:text-foreground hover:border-border-subtle transition-colors ${className}`}
    >
      <Sun aria-hidden="true" className="cw-dark-only w-4 h-4" />
      <Moon aria-hidden="true" className="cw-light-only w-4 h-4" />
    </button>
  )
}
