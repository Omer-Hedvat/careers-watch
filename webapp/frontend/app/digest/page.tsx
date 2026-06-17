'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { supabase } from '@/lib/supabaseClient'

type Job = {
  id: string
  company: string
  title: string
  location: string
  score: number
  reasoning: string
  flags: string[]
  scored_at: string
  applied: boolean
  apply_url: string
  profile_version?: number
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const h = Math.floor(diff / 3_600_000)
  const d = Math.floor(diff / 86_400_000)
  if (h < 1) return 'just now'
  if (h < 24) return `${h}h ago`
  return `${d}d ago`
}

function ScoreBadge({ score }: { score: number }) {
  const bg = score >= 9 ? 'bg-green-600' : score >= 7 ? 'bg-blue-600' : 'bg-gray-600'
  return <span className={`${bg} text-white text-sm font-bold w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0`}>{score}</span>
}

function JobCard({ job, onToggleApplied, currentProfileVersion }: { job: Job; onToggleApplied: (j: Job) => void; currentProfileVersion: number }) {
  const staleProfile = job.profile_version !== undefined && job.profile_version < currentProfileVersion
  return (
    <div className={`bg-gray-900 rounded-xl p-5 flex gap-4 ${job.applied ? 'opacity-50' : ''}`}>
      <ScoreBadge score={job.score} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-semibold text-white">{job.company} — {job.title}</span>
          {staleProfile && <span className="px-2 py-0.5 bg-gray-800 text-gray-500 text-xs rounded border border-gray-700">scored with old profile</span>}
        </div>
        <div className="text-sm text-gray-400 mt-0.5">{job.location} · scored {timeAgo(job.scored_at)}</div>
        {job.reasoning && <p className="text-sm text-gray-300 mt-2 line-clamp-2">"{job.reasoning}"</p>}
        {job.flags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {job.flags.map(f => <span key={f} className="px-2 py-0.5 bg-gray-800 text-gray-400 text-xs rounded">{f}</span>)}
          </div>
        )}
        <div className="flex gap-2 mt-3">
          <a href={job.apply_url} target="_blank" rel="noopener noreferrer"
            className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg font-medium">
            Apply →
          </a>
          <button onClick={() => onToggleApplied(job)}
            className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-sm rounded-lg">
            {job.applied ? 'Undo applied' : 'Mark applied'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function DigestPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [scoring, setScoring] = useState(false)
  const [scoreMsg, setScoreMsg] = useState('')
  const [runsUsed, setRunsUsed] = useState(0)
  const [currentProfileVersion, setCurrentProfileVersion] = useState(1)
  const [minScore, setMinScore] = useState(5)
  const [titleFilter, setTitleFilter] = useState('')
  const [companyFilter, setCompanyFilter] = useState('')
  const [locationFilter, setLocationFilter] = useState('')
  const [showApplied, setShowApplied] = useState(false)

  async function getToken() {
    const { data: { session } } = await supabase.auth.getSession()
    return session?.access_token ?? ''
  }

  async function loadJobs() {
    const token = await getToken()
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) setJobs(await res.json())
    setLoading(false)
  }

  async function loadUser() {
    const token = await getToken()
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      const d = await res.json()
      setRunsUsed(d.scoring_runs_this_week ?? 0)
      setCurrentProfileVersion(d.profile_version ?? 1)
    }
  }

  useEffect(() => { loadJobs(); loadUser() }, [])

  async function triggerScoring() {
    setScoring(true)
    setScoreMsg('')
    const token = await getToken()
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/score/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    if (res.ok) setScoreMsg(`Scored ${data.scored} new jobs`)
    else setScoreMsg(data.detail ?? 'Scoring failed')
    await loadJobs()
    await loadUser()
    setScoring(false)
  }

  async function toggleApplied(job: Job) {
    const token = await getToken()
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs/${job.id}/applied`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    setJobs(prev => prev.map(j => j.id === job.id ? { ...j, applied: !j.applied } : j))
  }

  function matchesMultiFilter(value: string, filter: string): boolean {
    if (!filter.trim()) return true
    const terms = filter.split(';').map(t => t.trim()).filter(Boolean)
    return terms.some(t => value.toLowerCase().includes(t.toLowerCase()))
  }

  const filtered = jobs
    .filter(j => j.score >= minScore)
    .filter(j => matchesMultiFilter(j.title, titleFilter))
    .filter(j => matchesMultiFilter(j.company, companyFilter))
    .filter(j => matchesMultiFilter(j.location, locationFilter))

  const active = filtered.filter(j => !j.applied)
  const applied = filtered.filter(j => j.applied)

  const lastScored = jobs.length > 0 ? timeAgo(jobs.reduce((a, b) => a.scored_at > b.scored_at ? a : b).scored_at) : null

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <div className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div>
          <span className="font-bold text-lg">CareerWatch</span>
          {lastScored && <span className="text-sm text-gray-400 ml-4">Last scored: {lastScored}</span>}
        </div>
        <div className="flex items-center gap-3">
          {scoreMsg && <span className="text-sm text-gray-400">{scoreMsg}</span>}
          <button
            onClick={triggerScoring}
            disabled={scoring || runsUsed >= 2}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:text-gray-400 rounded-lg text-sm font-medium"
          >
            {scoring ? 'Scoring...' : runsUsed >= 2 ? '2 of 2 runs used' : 'Score now'}
          </button>
          <Link href="/settings" className="p-2 text-gray-400 hover:text-white rounded-lg">⚙</Link>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        {/* Filters */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-400">Min score:</label>
            <input type="range" min={0} max={10} value={minScore} onChange={e => setMinScore(+e.target.value)} className="w-24" />
            <span className="text-sm w-4">{minScore}</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            <input value={titleFilter} onChange={e => setTitleFilter(e.target.value)}
              placeholder="e.g. Data Scientist; Machine Learning; Applied Scientist"
              className="flex-1 min-w-[200px] px-3 py-1.5 bg-gray-800 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-green-500" />
            <input value={companyFilter} onChange={e => setCompanyFilter(e.target.value)}
              placeholder="e.g. Wiz; CrowdStrike; Palo Alto"
              className="flex-1 min-w-[160px] px-3 py-1.5 bg-gray-800 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-green-500" />
            <input value={locationFilter} onChange={e => setLocationFilter(e.target.value)}
              placeholder="e.g. Tel Aviv; Herzliya; Remote"
              className="flex-1 min-w-[160px] px-3 py-1.5 bg-gray-800 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-green-500" />
          </div>
        </div>

        {/* Job list */}
        {loading && <p className="text-gray-400">Loading...</p>}
        {!loading && active.length === 0 && applied.length === 0 && (
          <p className="text-gray-400 text-center py-12">No jobs scored yet. Click "Score now" to run your first scoring.</p>
        )}
        {!loading && active.length === 0 && applied.length > 0 && (
          <p className="text-gray-400 text-center py-6">No jobs match your current filters.</p>
        )}
        {active.map(job => <JobCard key={job.id} job={job} onToggleApplied={toggleApplied} currentProfileVersion={currentProfileVersion} />)}

        {/* Applied section */}
        {applied.length > 0 && (
          <div>
            <button onClick={() => setShowApplied(v => !v)} className="text-sm text-gray-400 hover:text-white py-2">
              {showApplied ? `Hide ${applied.length} applied` : `Show ${applied.length} applied`}
            </button>
            {showApplied && applied.map(job => <JobCard key={job.id} job={job} onToggleApplied={toggleApplied} currentProfileVersion={currentProfileVersion} />)}
          </div>
        )}
      </div>
    </div>
  )
}
