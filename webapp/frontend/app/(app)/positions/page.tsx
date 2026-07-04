'use client'

import { useEffect, useState, useMemo } from 'react'
import { ArrowUpRight, ChevronLeft, ChevronRight } from 'lucide-react'
import { supabase } from '@/lib/supabaseClient'
import { useCountUp } from '@/hooks/useCountUp'

const PAGE_SIZE = 50

type Position = {
  company: string
  title: string
  location: string
  apply_url: string
  score: number | null
  status: string | null
}

function PositionRowSkeleton() {
  return (
    <div className="bg-surface rounded-xl px-5 py-3 animate-pulse motion-reduce:animate-none">
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0 space-y-2">
          <div className="h-4 bg-surface-raised rounded w-2/3" />
          <div className="h-3 bg-surface-raised rounded w-1/3" />
        </div>
        <div className="h-3 bg-surface-raised rounded w-12 shrink-0 mt-0.5" />
      </div>
    </div>
  )
}

export default function PositionsPage() {
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const animatedTotal = useCountUp(loading ? 0 : positions.length)

  useEffect(() => {
    async function load() {
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token ?? ''
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs/positions`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) setPositions(await res.json())
      setLoading(false)
    }
    load()
  }, [])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return positions
    return positions.filter(
      p => p.company.toLowerCase().includes(q) || p.title.toLowerCase().includes(q)
    )
  }, [positions, search])

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const page_ = Math.min(page, Math.max(0, totalPages - 1))
  const visible = filtered.slice(page_ * PAGE_SIZE, (page_ + 1) * PAGE_SIZE)

  function handleSearch(val: string) {
    setSearch(val)
    setPage(0)
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">
            Open positions
            {!loading && (
              <span className="text-muted font-normal text-base ml-2">
                ({search.trim()
                  ? `${filtered.length.toLocaleString()} of ${animatedTotal.toLocaleString()}`
                  : animatedTotal.toLocaleString()
                })
              </span>
            )}
          </h1>
          <input
            value={search}
            onChange={e => handleSearch(e.target.value)}
            placeholder="Search company or title..."
            className="px-3 py-1.5 bg-surface-raised rounded-lg border border-subtle text-sm focus:outline-none focus:border-accent transition-colors w-52"
          />
        </div>

        {loading && (
          <div className="space-y-1.5">
            {[0, 1, 2, 3, 4, 5].map(i => <PositionRowSkeleton key={i} />)}
          </div>
        )}

        {!loading && filtered.length === 0 && (
          <p className="text-muted text-center py-12">No positions found.</p>
        )}

        <div className="space-y-1.5">
          {visible.map((p, i) => {
            const isClosed = p.status === 'closed'
            return (
              <a
                key={`${p.company}-${p.title}-${i}`}
                href={isClosed ? undefined : (p.apply_url || '#')}
                target="_blank"
                rel="noopener noreferrer"
                className={`flex items-start gap-3 bg-surface rounded-xl px-5 py-3 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${isClosed ? 'opacity-40 pointer-events-none' : 'hover:bg-surface-raised'} ${!p.apply_url ? 'pointer-events-none opacity-50' : ''}`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`font-semibold text-sm ${isClosed ? 'text-muted line-through' : 'text-foreground'}`}>{p.company}</span>
                    <span className="text-subtle text-sm">—</span>
                    <span className={`text-sm ${isClosed ? 'text-subtle line-through' : 'text-gray-200'}`}>{p.title}</span>
                    {isClosed && <span className="text-xs text-danger no-underline" style={{textDecoration: 'none'}}>Closed</span>}
                  </div>
                  {p.location && (
                    <div className="text-xs text-subtle mt-0.5">{p.location}</div>
                  )}
                </div>
                {!isClosed && (
                  <span className="text-xs text-accent shrink-0 mt-0.5 inline-flex items-center gap-0.5">
                    Apply
                    <ArrowUpRight className="w-3.5 h-3.5" aria-hidden="true" />
                  </span>
                )}
                {p.score != null && (
                  <span className={`text-xs shrink-0 mt-0.5 font-medium ${p.score >= 9 ? 'text-green-400' : p.score >= 7 ? 'text-yellow-400' : 'text-subtle'}`}>
                    {p.score}/10
                  </span>
                )}
              </a>
            )
          })}
        </div>

        {totalPages > 1 && (
          <div className="flex items-center justify-between pt-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page_ === 0}
              className="inline-flex items-center gap-1 px-3 py-1.5 bg-surface-raised rounded-lg text-sm transition-colors disabled:opacity-40 hover:bg-border-subtle disabled:hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              <ChevronLeft className="w-4 h-4" aria-hidden="true" />
              Prev
            </button>
            <span className="text-sm text-muted">
              Page {page_ + 1} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page_ === totalPages - 1}
              className="inline-flex items-center gap-1 px-3 py-1.5 bg-surface-raised rounded-lg text-sm transition-colors disabled:opacity-40 hover:bg-border-subtle disabled:hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              Next
              <ChevronRight className="w-4 h-4" aria-hidden="true" />
            </button>
          </div>
        )}
    </div>
  )
}
