'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { supabase } from '@/lib/supabaseClient'

// --- Types ---

type GapSeverity = 'critical' | 'moderate' | 'minor'
type CvCoverage = 'none' | 'partial' | 'implicit'
type MatchStrength = 'strong' | 'partial' | 'weak' | 'unknown'
type ProfileAlignment = 'strong' | 'partial' | 'mismatch' | 'unknown'

type ProfileGap = {
  area: string
  profile_says: string
  cv_shows: string
  severity: GapSeverity
  suggestion: string
}

type ProfileCVResult = {
  alignment_score: number
  positioning_notes: string
  strengths: string[]
  gaps: ProfileGap[]
  empty?: boolean
  reason?: string
}

type CvGap = {
  requirement: string
  cv_coverage: CvCoverage
  note: string
}

type ProfileDivergence = {
  profile_says: string
  jd_says: string
  impact: 'high' | 'medium' | 'low'
}

type PositionResult = {
  job_id: string
  company: string
  title: string
  location: string
  score: number
  error?: string
  cv_gap?: {
    match_strength: MatchStrength
    strengths: string[]
    gaps: CvGap[]
  }
  profile_gap?: {
    alignment: ProfileAlignment
    divergences: ProfileDivergence[]
  }
}

// --- Helpers ---

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token ?? ''
}

async function apiFetch(path: string) {
  const token = await getToken()
  const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!r.ok) throw new Error(`${r.status}`)
  return r.json()
}

function severityColor(s: GapSeverity) {
  if (s === 'critical') return 'border-red-500 bg-red-900/10'
  if (s === 'moderate') return 'border-amber-500 bg-amber-900/10'
  return 'border-gray-700 bg-gray-800/30'
}

function severityBadge(s: GapSeverity) {
  if (s === 'critical') return 'bg-red-900/60 text-red-300'
  if (s === 'moderate') return 'bg-amber-900/60 text-amber-300'
  return 'bg-gray-800 text-gray-400'
}

function coverageColor(c: CvCoverage) {
  if (c === 'none') return 'text-red-400'
  if (c === 'partial') return 'text-amber-400'
  return 'text-gray-400'
}

function matchStrengthBadge(m: MatchStrength) {
  if (m === 'strong') return 'bg-green-900/50 text-green-300'
  if (m === 'partial') return 'bg-amber-900/50 text-amber-300'
  if (m === 'weak') return 'bg-red-900/50 text-red-300'
  return 'bg-gray-800 text-gray-400'
}

function alignmentBadge(a: ProfileAlignment) {
  if (a === 'strong') return 'bg-green-900/50 text-green-300'
  if (a === 'partial') return 'bg-amber-900/50 text-amber-300'
  if (a === 'mismatch') return 'bg-red-900/50 text-red-300'
  return 'bg-gray-800 text-gray-400'
}

function buildCopyText(pos: PositionResult): string {
  const lines: string[] = []
  lines.push(`Gap summary: ${pos.company} - ${pos.title} (score ${pos.score})`)
  lines.push('')
  if (pos.cv_gap?.gaps?.length) {
    lines.push('CV gaps (requirements not clearly covered):')
    for (const g of pos.cv_gap.gaps) {
      lines.push(`- ${g.requirement} [${g.cv_coverage}]${g.note ? ': ' + g.note : ''}`)
    }
    lines.push('')
  }
  if (pos.cv_gap?.strengths?.length) {
    lines.push('CV strengths (requirements clearly covered):')
    for (const s of pos.cv_gap.strengths) lines.push(`+ ${s}`)
    lines.push('')
  }
  if (pos.profile_gap?.divergences?.length) {
    lines.push('Profile divergences:')
    for (const d of pos.profile_gap.divergences) {
      lines.push(`- Profile says: ${d.profile_says}`)
      lines.push(`  JD says: ${d.jd_says} [${d.impact} impact]`)
    }
  }
  return lines.join('\n')
}

// --- Components ---

function AlignmentScore({ score }: { score: number }) {
  const color = score >= 8 ? 'text-green-400' : score >= 6 ? 'text-amber-400' : 'text-red-400'
  return (
    <div className="flex items-center gap-3">
      <span className={`text-5xl font-bold ${color}`}>{score}</span>
      <span className="text-gray-500 text-lg">/10</span>
    </div>
  )
}

function PositionRow({ pos }: { pos: PositionResult }) {
  const [expanded, setExpanded] = useState(false)
  const [copied, setCopied] = useState(false)

  const cvMatch = pos.cv_gap?.match_strength ?? 'unknown'
  const profAlign = pos.profile_gap?.alignment ?? 'unknown'
  const hasError = !!pos.error

  function copy() {
    navigator.clipboard.writeText(buildCopyText(pos))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="border border-gray-700 rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-gray-800/50 transition-colors"
      >
        <span className="bg-gray-700 text-white text-sm font-bold w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
          {pos.score}
        </span>
        <div className="flex-1 min-w-0">
          <span className="font-medium text-white">{pos.company}</span>
          <span className="text-gray-400"> - {pos.title}</span>
          {pos.location && <span className="text-gray-500 text-sm ml-2">{pos.location}</span>}
        </div>
        {!hasError && (
          <div className="flex gap-2 flex-shrink-0">
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${matchStrengthBadge(cvMatch)}`}>
              CV: {cvMatch}
            </span>
            {profAlign !== 'strong' && (
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${alignmentBadge(profAlign)}`}>
                Profile: {profAlign}
              </span>
            )}
          </div>
        )}
        <span className="text-gray-500 ml-2">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="border-t border-gray-700 p-4 space-y-4 bg-gray-900/50">
          {hasError ? (
            <p className="text-sm text-red-400">Analysis failed: {pos.error}</p>
          ) : (
            <>
              {/* CV strengths */}
              {(pos.cv_gap?.strengths?.length ?? 0) > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">CV covers these requirements</p>
                  <ul className="space-y-1">
                    {pos.cv_gap!.strengths.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <span className="text-green-400 flex-shrink-0 mt-0.5">✓</span>
                        <span className="text-gray-300">{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* CV gaps */}
              {(pos.cv_gap?.gaps?.length ?? 0) > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">CV gaps</p>
                  <ul className="space-y-2">
                    {pos.cv_gap!.gaps.map((g, i) => (
                      <li key={i} className="text-sm">
                        <div className="flex items-start gap-2">
                          <span className={`flex-shrink-0 mt-0.5 ${coverageColor(g.cv_coverage)}`}>
                            {g.cv_coverage === 'none' ? '✗' : '~'}
                          </span>
                          <div>
                            <span className="text-white">{g.requirement}</span>
                            <span className={`ml-2 text-xs px-1.5 py-0.5 rounded ${coverageColor(g.cv_coverage)} bg-gray-800`}>
                              {g.cv_coverage}
                            </span>
                            {g.note && <p className="text-gray-400 mt-0.5">{g.note}</p>}
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Profile divergences */}
              {(pos.profile_gap?.divergences?.length ?? 0) > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Profile divergences</p>
                  <ul className="space-y-3">
                    {pos.profile_gap!.divergences.map((d, i) => (
                      <li key={i} className="text-sm space-y-0.5">
                        <div className="flex items-start gap-2">
                          <span className={`flex-shrink-0 text-xs px-1.5 py-0.5 rounded mt-0.5 ${
                            d.impact === 'high' ? 'bg-red-900/50 text-red-300' :
                            d.impact === 'medium' ? 'bg-amber-900/50 text-amber-300' :
                            'bg-gray-800 text-gray-400'
                          }`}>{d.impact}</span>
                          <div>
                            <p className="text-gray-400">Profile: {d.profile_says}</p>
                            <p className="text-gray-300">JD: {d.jd_says}</p>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <button
                onClick={copy}
                className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-sm rounded-lg"
              >
                {copied ? 'Copied!' : 'Copy gap summary'}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}

// --- Page ---

export default function GapsPage() {
  const [profileCV, setProfileCV] = useState<ProfileCVResult | null>(null)
  const [positions, setPositions] = useState<PositionResult[] | null>(null)
  const [loadingProfileCV, setLoadingProfileCV] = useState(true)
  const [loadingPositions, setLoadingPositions] = useState(true)
  const [errorProfileCV, setErrorProfileCV] = useState('')
  const [errorPositions, setErrorPositions] = useState('')
  const [filter, setFilter] = useState('')

  useEffect(() => {
    apiFetch('/gaps/profile-cv')
      .then(d => setProfileCV(d))
      .catch(e => setErrorProfileCV(e.message))
      .finally(() => setLoadingProfileCV(false))

    apiFetch('/gaps/positions?min_score=6')
      .then(d => setPositions(d))
      .catch(e => setErrorPositions(e.message))
      .finally(() => setLoadingPositions(false))
  }, [])

  const filteredPositions = positions?.filter(p =>
    !filter ||
    p.company.toLowerCase().includes(filter.toLowerCase()) ||
    p.title.toLowerCase().includes(filter.toLowerCase())
  ) ?? []

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-8">Gap Analysis</h1>

        {/* Section 1: Profile vs CV */}
        <section className="mb-10">
          <h2 className="text-lg font-semibold mb-4 text-gray-200">Profile vs CV</h2>
          {loadingProfileCV ? (
            <p className="text-sm text-gray-400">Analyzing alignment...</p>
          ) : errorProfileCV ? (
            <p className="text-sm text-red-400">Error: {errorProfileCV}</p>
          ) : profileCV?.empty ? (
            <div className="bg-gray-800/50 rounded-xl p-6 text-center">
              <p className="text-gray-400 text-sm">{profileCV.reason}</p>
              <Link href="/settings" className="mt-2 inline-block text-sm text-green-400 hover:text-green-300 underline">
                Go to Settings
              </Link>
            </div>
          ) : profileCV ? (
            <div className="space-y-4">
              {/* Score + positioning note */}
              <div className="bg-gray-900 rounded-xl p-6 space-y-3">
                <AlignmentScore score={profileCV.alignment_score} />
                {profileCV.positioning_notes && (
                  <p className="text-gray-300 text-sm leading-relaxed">{profileCV.positioning_notes}</p>
                )}
              </div>

              {/* Strengths */}
              {profileCV.strengths?.length > 0 && (
                <div className="bg-gray-900 rounded-xl p-5">
                  <p className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-3">Strengths</p>
                  <ul className="space-y-2">
                    {profileCV.strengths.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <span className="text-green-400 flex-shrink-0 mt-0.5">✓</span>
                        <span className="text-gray-200">{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Gaps */}
              {profileCV.gaps?.length > 0 && (
                <div className="space-y-3">
                  <p className="text-sm font-medium text-gray-400 uppercase tracking-wide">Gaps</p>
                  {profileCV.gaps.map((g, i) => (
                    <div key={i} className={`rounded-xl p-5 border ${severityColor(g.severity)}`}>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="font-medium text-white">{g.area}</span>
                        <span className={`px-2 py-0.5 rounded text-xs ${severityBadge(g.severity)}`}>{g.severity}</span>
                      </div>
                      <div className="space-y-1.5 text-sm">
                        <p><span className="text-gray-400">Profile targets:</span> <span className="text-gray-200">{g.profile_says}</span></p>
                        <p><span className="text-gray-400">CV shows:</span> <span className="text-gray-200">{g.cv_shows}</span></p>
                        {g.suggestion && (
                          <p className="mt-2 pt-2 border-t border-gray-700/50">
                            <span className="text-gray-400">Suggestion:</span>{' '}
                            <span className="text-gray-200">{g.suggestion}</span>
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : null}
        </section>

        {/* Section 2: Position gaps */}
        <section>
          <h2 className="text-lg font-semibold mb-4 text-gray-200">Position gaps (score &ge; 6)</h2>
          {loadingPositions ? (
            <p className="text-sm text-gray-400">Analyzing positions... this may take a minute.</p>
          ) : errorPositions ? (
            <p className="text-sm text-red-400">Error: {errorPositions}</p>
          ) : !positions || positions.length === 0 ? (
            <div className="bg-gray-800/50 rounded-xl p-6 text-center">
              <p className="text-gray-400 text-sm">No positions scored 6 or above yet.</p>
              <Link href="/digest" className="mt-2 inline-block text-sm text-green-400 hover:text-green-300 underline">
                Run scoring first
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              <input
                value={filter}
                onChange={e => setFilter(e.target.value)}
                placeholder="Filter by company or title..."
                className="w-full bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-green-500"
              />
              {filteredPositions.length === 0 ? (
                <p className="text-sm text-gray-500 py-4 text-center">No matches for &ldquo;{filter}&rdquo;</p>
              ) : (
                filteredPositions.map(pos => <PositionRow key={pos.job_id} pos={pos} />)
              )}
            </div>
          )}
        </section>
    </div>
  )
}
