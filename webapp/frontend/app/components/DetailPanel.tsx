'use client'

import { useEffect, type ReactNode } from 'react'
import { X } from 'lucide-react'

// Shared slide-over shell: fixed overlay, right-anchored panel, entrance
// animation, Esc-to-close, backdrop click, and body-scroll lock. Callers
// supply the header, an optional action row, and the body via children.
// Used by the digest job detail and the positions catalog detail.
export function DetailPanel({
  ariaLabel, header, actions, children, onClose,
}: {
  ariaLabel: string
  header: ReactNode
  actions?: ReactNode
  children: ReactNode
  onClose: () => void
}) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', onKey)
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = prev
    }
  }, [onClose])

  return (
    <div className="fixed inset-0 z-50" role="dialog" aria-modal="true" aria-label={ariaLabel}>
      <style>{`
        @keyframes cwPanelIn { from { transform: translateX(24px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes cwFadeIn { from { opacity: 0; } to { opacity: 1; } }
        @media (prefers-reduced-motion: no-preference) {
          .cw-panel-in { animation: cwPanelIn 0.25s ease-out; }
          .cw-fade-in { animation: cwFadeIn 0.25s ease-out; }
        }
      `}</style>
      <div className="cw-fade-in absolute inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />
      <div className="cw-panel-in absolute right-0 top-0 h-full w-full max-w-xl bg-surface border-l border-border shadow-2xl overflow-y-auto">
        <div className="sticky top-0 flex items-start justify-between gap-4 px-6 py-4 bg-surface/95 backdrop-blur-sm border-b border-border">
          <div className="flex items-center gap-3 min-w-0">{header}</div>
          <button onClick={onClose} aria-label="Close details"
            className="flex-shrink-0 w-8 h-8 rounded-lg border border-border text-muted hover:text-foreground hover:border-border-subtle flex items-center justify-center transition-colors">
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        <div className="px-6 py-5 space-y-6">
          {actions && <div className="flex gap-2">{actions}</div>}
          {children}
        </div>
      </div>
    </div>
  )
}
