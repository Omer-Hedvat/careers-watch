'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Check } from 'lucide-react'

type Props = {
  profile: boolean
  cv: boolean
  apiKey: boolean
  hasJobs: boolean
}

type ChecklistItem = {
  label: string
  done: boolean
  action: React.ReactNode
}

export default function GettingStartedChecklist({ profile, cv, apiKey, hasJobs }: Props) {
  const [dismissed, setDismissed] = useState(false)

  const allDone = profile && cv && apiKey && hasJobs

  if (allDone || dismissed) return null

  const items: ChecklistItem[] = [
    {
      label: 'Add your profile',
      done: profile,
      action: (
        <Link href="/settings#profile" className="text-xs text-accent hover:text-accent-hover underline underline-offset-2 transition-colors">
          Go to settings
        </Link>
      ),
    },
    {
      label: 'Upload your CV',
      done: cv,
      action: (
        <Link href="/settings#cv" className="text-xs text-accent hover:text-accent-hover underline underline-offset-2 transition-colors">
          Go to settings
        </Link>
      ),
    },
    {
      label: 'Set your API key',
      done: apiKey,
      action: (
        <Link href="/settings#apikey" className="text-xs text-accent hover:text-accent-hover underline underline-offset-2 transition-colors">
          Go to settings
        </Link>
      ),
    },
    {
      label: 'Run your first scan',
      done: hasJobs,
      action: (
        <span className="text-xs text-muted">
          Click &quot;Score now&quot; above
        </span>
      ),
    },
  ]

  return (
    <div className="bg-surface rounded-xl p-5 border border-border">
      <div className="flex items-center justify-between mb-4">
        <h2 className="cw-label text-accent">Getting started</h2>
        <button
          onClick={() => setDismissed(true)}
          className="text-xs text-subtle hover:text-muted transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded"
        >
          Dismiss for now
        </button>
      </div>
      <ul className="space-y-3">
        {items.map((item) => (
          <li key={item.label} className="flex items-center gap-3">
            {item.done ? (
              <span className="w-5 h-5 rounded-full bg-score-high flex items-center justify-center flex-shrink-0">
                <Check className="w-3 h-3 text-white" strokeWidth={3} aria-hidden="true" />
              </span>
            ) : (
              <span className="w-5 h-5 rounded-full border border-border-subtle flex-shrink-0" />
            )}
            <span className={`text-sm flex-1 ${item.done ? 'text-subtle line-through' : 'text-foreground/90'}`}>
              {item.label}
            </span>
            {!item.done && item.action}
          </li>
        ))}
      </ul>
    </div>
  )
}
