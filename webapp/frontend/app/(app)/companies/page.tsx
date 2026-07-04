'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabaseClient'
import { useCountUp } from '@/hooks/useCountUp'

type Company = {
  name: string
  category: string
  ats: string
  careers_url: string
  last_verified_at: string | null
  consecutive_failures: number
  open_positions: number
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

function CompanyRowSkeleton() {
  return (
    <div className="bg-surface rounded-xl px-5 py-4 animate-pulse motion-reduce:animate-none">
      <div className="flex items-center gap-2">
        <div className="h-4 bg-surface-raised rounded w-32" />
        <div className="h-4 bg-surface-raised rounded w-14" />
        <div className="h-4 bg-surface-raised rounded w-16" />
      </div>
      <div className="h-3 bg-surface-raised rounded w-24 mt-2" />
    </div>
  )
}

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const animatedCount = useCountUp(loading ? 0 : companies.length)

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
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">
            Tracked companies
            {!loading && <span className="text-muted font-normal text-base ml-2">({animatedCount})</span>}
          </h1>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search..."
            className="px-3 py-1.5 bg-surface-raised rounded-lg border border-subtle text-sm focus:outline-none focus:border-accent transition-colors w-40"
          />
        </div>

        {loading && (
          <div className="space-y-2">
            {[0, 1, 2, 3, 4].map(i => <CompanyRowSkeleton key={i} />)}
          </div>
        )}

        {!loading && filtered.length === 0 && (
          <p className="text-muted text-center py-12">No companies found.</p>
        )}

        <div className="space-y-2">
          {filtered.map(c => (
            <a
              key={c.name}
              href={c.careers_url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              className={`block bg-surface rounded-xl px-5 py-4 hover:bg-surface-raised transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${!c.careers_url ? 'pointer-events-none' : ''}`}
            >
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-semibold text-foreground">{c.name}</span>
                <CategoryBadge category={c.category} />
                {c.ats && c.ats !== 'unknown' && <span className="text-xs text-subtle bg-surface-raised px-2 py-0.5 rounded">{c.ats}</span>}
                {c.open_positions > 0 && (
                  <span className="text-xs text-green-400 bg-green-900/40 px-2 py-0.5 rounded">
                    {c.open_positions} open
                  </span>
                )}
                <FailureBadge count={c.consecutive_failures} />
              </div>
              <div className="text-xs text-subtle mt-1">
                {c.last_verified_at ? `Verified ${timeAgo(c.last_verified_at)}` : 'Never verified'}
              </div>
            </a>
          ))}
        </div>
    </div>
  )
}
