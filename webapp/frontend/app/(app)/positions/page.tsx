'use client'

import { useEffect, useState, useMemo } from 'react'
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
              <span className="text-gray-400 font-normal text-base ml-2">
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
            className="px-3 py-1.5 bg-gray-800 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-green-500 w-52"
          />
        </div>

        {loading && <p className="text-gray-400">Loading...</p>}

        {!loading && filtered.length === 0 && (
          <p className="text-gray-400 text-center py-12">No positions found.</p>
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
                className={`flex items-start gap-3 bg-gray-900 rounded-xl px-5 py-3 transition-colors ${isClosed ? 'opacity-40 pointer-events-none' : 'hover:bg-gray-800'} ${!p.apply_url ? 'pointer-events-none opacity-50' : ''}`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`font-semibold text-sm ${isClosed ? 'text-gray-400 line-through' : 'text-white'}`}>{p.company}</span>
                    <span className="text-gray-500 text-sm">—</span>
                    <span className={`text-sm ${isClosed ? 'text-gray-500 line-through' : 'text-gray-200'}`}>{p.title}</span>
                    {isClosed && <span className="text-xs text-red-500 no-underline" style={{textDecoration: 'none'}}>Closed</span>}
                  </div>
                  {p.location && (
                    <div className="text-xs text-gray-500 mt-0.5">{p.location}</div>
                  )}
                </div>
                {!isClosed && <span className="text-xs text-green-500 shrink-0 mt-0.5">Apply →</span>}
                {p.score != null && (
                  <span className={`text-xs shrink-0 mt-0.5 font-medium ${p.score >= 9 ? 'text-green-400' : p.score >= 7 ? 'text-yellow-400' : 'text-gray-500'}`}>
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
              className="px-3 py-1.5 bg-gray-800 rounded-lg text-sm disabled:opacity-40 hover:bg-gray-700 disabled:hover:bg-gray-800"
            >
              ← Prev
            </button>
            <span className="text-sm text-gray-400">
              Page {page_ + 1} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page_ === totalPages - 1}
              className="px-3 py-1.5 bg-gray-800 rounded-lg text-sm disabled:opacity-40 hover:bg-gray-700 disabled:hover:bg-gray-800"
            >
              Next →
            </button>
          </div>
        )}
    </div>
  )
}
