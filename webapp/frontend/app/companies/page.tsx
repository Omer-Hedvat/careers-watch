'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { supabase } from '@/lib/supabaseClient'

type Company = {
  name: string
  category: string
  ats: string
  careers_url: string
  last_verified_at: string | null
  consecutive_failures: number
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const d = Math.floor(diff / 86_400_000)
  if (d < 1) return 'today'
  if (d === 1) return '1d ago'
  return `${d}d ago`
}

function FailureBadge({ count }: { count: number }) {
  if (count === 0) return null
  const color = count >= 3 ? 'bg-red-700 text-red-100' : 'bg-amber-700 text-amber-100'
  return (
    <span className={`${color} text-xs font-semibold px-2 py-0.5 rounded`}>
      {count} {count === 1 ? 'failure' : 'failures'}
    </span>
  )
}

function CategoryBadge({ category }: { category: string }) {
  const colors: Record<string, string> = {
    cyber: 'bg-blue-900 text-blue-200',
    fraud: 'bg-purple-900 text-purple-200',
    fintech: 'bg-teal-900 text-teal-200',
    security: 'bg-blue-900 text-blue-200',
    general: 'bg-gray-800 text-gray-300',
  }
  const cls = colors[category] ?? 'bg-gray-800 text-gray-300'
  return <span className={`${cls} text-xs px-2 py-0.5 rounded`}>{category || '—'}</span>
}

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    async function load() {
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token ?? ''
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs/companies`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) setCompanies(await res.json())
      setLoading(false)
    }
    load()
  }, [])

  const filtered = search.trim()
    ? companies.filter(c => c.name.toLowerCase().includes(search.toLowerCase()))
    : companies

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <div className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <span className="font-bold text-lg">CareerWatch</span>
        <div className="flex items-center gap-4">
          <Link href="/digest" className="text-sm text-gray-400 hover:text-white">Digest</Link>
          <Link href="/companies" className="text-sm text-white font-medium">Companies</Link>
          <Link href="/settings" className="p-2 text-gray-400 hover:text-white rounded-lg">⚙</Link>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">
            Tracked companies
            {!loading && <span className="text-gray-400 font-normal text-base ml-2">({companies.length})</span>}
          </h1>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search..."
            className="px-3 py-1.5 bg-gray-800 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-green-500 w-40"
          />
        </div>

        {loading && <p className="text-gray-400">Loading...</p>}

        {!loading && filtered.length === 0 && (
          <p className="text-gray-400 text-center py-12">No companies found.</p>
        )}

        <div className="space-y-2">
          {filtered.map(c => (
            <a
              key={c.name}
              href={c.careers_url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              className={`block bg-gray-900 rounded-xl px-5 py-4 hover:bg-gray-800 transition-colors ${!c.careers_url ? 'pointer-events-none' : ''}`}
            >
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-semibold text-white">{c.name}</span>
                <CategoryBadge category={c.category} />
                {c.ats && <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">{c.ats}</span>}
                <FailureBadge count={c.consecutive_failures} />
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {c.last_verified_at ? `Verified ${timeAgo(c.last_verified_at)}` : 'Never verified'}
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
