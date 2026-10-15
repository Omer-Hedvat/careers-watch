'use client'

// Skip / Unskip button shared by Positions and the Digest. Presentational only
// (JobCard also renders on the public landing page); the save lives in lib/skip.ts.

export function SkipButton({ skipped, onClick, className = '' }: { skipped?: boolean; onClick: () => void; className?: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={skipped ? 'Show this job again' : 'Not interested - hide this job and never score it'}
      className={`px-3.5 py-1.5 text-muted hover:text-foreground text-sm rounded-lg transition-colors underline underline-offset-2 decoration-border-subtle focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${className}`}
    >
      {skipped ? 'Unskip' : 'Skip'}
    </button>
  )
}
