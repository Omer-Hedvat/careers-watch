'use client'

import { useState } from 'react'
import Link from 'next/link'

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
        <Link href="/settings#profile" className="text-xs text-green-500 hover:text-green-400 underline underline-offset-2">
          Go to settings
        </Link>
      ),
    },
    {
      label: 'Upload your CV',
      done: cv,
      action: (
        <Link href="/settings#cv" className="text-xs text-green-500 hover:text-green-400 underline underline-offset-2">
          Go to settings
        </Link>
      ),
    },
    {
      label: 'Set your API key',
      done: apiKey,
      action: (
        <Link href="/settings#apikey" className="text-xs text-green-500 hover:text-green-400 underline underline-offset-2">
          Go to settings
        </Link>
      ),
    },
    {
      label: 'Run your first scan',
      done: hasJobs,
      action: (
        <span className="text-xs text-gray-400">
          Click &quot;Score now&quot; above
        </span>
      ),
    },
  ]

  return (
    <div className="bg-gray-900 rounded-xl p-5 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-white">Getting started</h2>
        <button
          onClick={() => setDismissed(true)}
          className="text-xs text-gray-500 hover:text-gray-300"
        >
          Dismiss for now
        </button>
      </div>
      <ul className="space-y-3">
        {items.map((item) => (
          <li key={item.label} className="flex items-center gap-3">
            {item.done ? (
              <span className="w-5 h-5 rounded-full bg-green-700 flex items-center justify-center flex-shrink-0">
                <svg className="w-3 h-3 text-green-300" viewBox="0 0 12 12" fill="none">
                  <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
            ) : (
              <span className="w-5 h-5 rounded-full border border-gray-600 flex-shrink-0" />
            )}
            <span className={`text-sm flex-1 ${item.done ? 'text-gray-500 line-through' : 'text-gray-200'}`}>
              {item.label}
            </span>
            {!item.done && item.action}
          </li>
        ))}
      </ul>
    </div>
  )
}
