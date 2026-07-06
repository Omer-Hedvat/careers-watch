'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Check, X, Minus, ChevronDown, Copy } from 'lucide-react'
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
  if (s === 'critical') return 'border-danger/50 bg-danger/[0.06]'
  if (s === 'moderate') return 'border-warning/50 bg-warning/[0.06]'
  return 'border-border bg-surface'
}

function severityBadge(s: GapSeverity) {
  if (s === 'critical') return 'bg-danger/15 text-danger'
  if (s === 'moderate') return 'bg-warning/15 text-warning'
  return 'bg-surface-raised text-muted'
}

function coverageColor(c: CvCoverage) {
  if (c === 'none') return 'text-danger'
  if (c === 'partial') return 'text-warning'
  return 'text-muted'
}

function matchStrengthBadge(m: MatchStrength) {
  if (m === 'strong') return 'bg-score-high/15 text-score-high'
  if (m === 'partial') return 'bg-warning/15 text-warning'
  if (m === 'weak') return 'bg-danger/15 text-danger'
  return 'bg-surface-raised text-muted'
}

function alignmentBadge(a: ProfileAlignment) {
  if (a === 'strong') return 'bg-score-high/15 text-score-high'
  if (a === 'partial') return 'bg-warning/15 text-warning'
  if (a === 'mismatch') return 'bg-danger/15 text-danger'
  return 'bg-surface-raised text-muted'
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
  const color = score >= 8 ? 'text-score-high' : score >= 6 ? 'text-warning' : 'text-danger'
  return (
    <div className="flex items-center gap-3">
      <span className={`text-5xl font-mono font-semibold tabular-nums ${color}`}>{score}</span>
      <span className="text-subtle font-mono text-lg">/10</span>
    </div>
  )
}

function ProfileCVSkeleton() {
  return (
    <div className="bg-surface rounded-xl p-6 space-y-4 animate-pulse motion-reduce:animate-none">
      <div className="flex items-center gap-3">
        <div className="h-12 w-16 bg-surface-raised rounded" />
        <div className="h-5 w-10 bg-surface-raised rounded" />
      </div>
      <div className="space-y-2">
        <div className="h-3 bg-surface-raised rounded w-full" />
        <div className="h-3 bg-surface-raised rounded w-5/6" />
        <div className="h-3 bg-surface-raised rounded w-2/3" />
      </div>
    </div>
  )
}

function PositionRowSkeleton() {
  return (
    <div className="border border-subtle rounded-xl p-4 flex items-center gap-3 animate-pulse motion-reduce:animate-none">
      <div className="w-8 h-8 rounded-full bg-surface-raised flex-shrink-0" />
      <div className="flex-1 min-w-0 space-y-2">
        <div className="h-4 bg-surface-raised rounded w-2/3" />
        <div className="h-3 bg-surface-raised rounded w-1/3" />
      </div>
      <div className="h-5 w-20 bg-surface-raised rounded flex-shrink-0" />
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
    <div className="border border-subtle rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(v => !v)}
        aria-expanded={expanded}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-surface-raised/60 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-inset"
      >
        <span className="bg-surface-raised text-foreground font-mono text-sm font-semibold w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 tabular-nums">
          {pos.score}
        </span>
        <div className="flex-1 min-w-0">
          <span className="font-medium text-foreground">{pos.company}</span>
          <span className="text-muted"> - {pos.title}</span>
          {pos.location && <span className="text-subtle text-sm ml-2">{pos.location}</span>}
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
        <ChevronDown
          className={`w-4 h-4 text-subtle ml-2 flex-shrink-0 transition-transform duration-300 motion-reduce:transition-none ${expanded ? 'rotate-180' : ''}`}
          aria-hidden="true"
        />
      </button>

      <div
        className={`grid transition-[grid-template-rows] duration-300 ease-in-out motion-reduce:transition-none ${expanded ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'}`}
        aria-hidden={!expanded}
      >
        <div className="overflow-hidden min-h-0">
          <div className="border-t border-border p-4 space-y-4 bg-background/40">
          {hasError ? (
            <p className="text-sm text-danger">Analysis failed: {pos.error}</p>
          ) : (
            <>
              {/* CV strengths */}
              {(pos.cv_gap?.strengths?.length ?? 0) > 0 && (
                <div>
                  <p className="cw-label text-subtle mb-2">CV covers these requirements</p>
                  <ul className="space-y-1">
                    {pos.cv_gap!.strengths.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <Check className="w-4 h-4 text-score-high flex-shrink-0 mt-0.5" aria-hidden="true" />
                        <span className="text-foreground/85">{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* CV gaps */}
              {(pos.cv_gap?.gaps?.length ?? 0) > 0 && (
                <div>
                  <p className="cw-label text-subtle mb-2">CV gaps</p>
                  <ul className="space-y-2">
                    {pos.cv_gap!.gaps.map((g, i) => (
                      <li key={i} className="text-sm">
                        <div className="flex items-start gap-2">
                          {g.cv_coverage === 'none' ? (
                            <X className={`w-4 h-4 flex-shrink-0 mt-0.5 ${coverageColor(g.cv_coverage)}`} aria-hidden="true" />
                          ) : (
                            <Minus className={`w-4 h-4 flex-shrink-0 mt-0.5 ${coverageColor(g.cv_coverage)}`} aria-hidden="true" />
                          )}
                          <div>
                            <span className="text-foreground">{g.requirement}</span>
                            <span className={`ml-2 text-xs px-1.5 py-0.5 rounded ${coverageColor(g.cv_coverage)} bg-surface-raised`}>
                              {g.cv_coverage}
                            </span>
                            {g.note && <p className="text-muted mt-0.5">{g.note}</p>}
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
                  <p className="cw-label text-subtle mb-2">Profile divergences</p>
                  <ul className="space-y-3">
                    {pos.profile_gap!.divergences.map((d, i) => (
                      <li key={i} className="text-sm space-y-0.5">
                        <div className="flex items-start gap-2">
                          <span className={`flex-shrink-0 text-xs px-1.5 py-0.5 rounded mt-0.5 ${
                            d.impact === 'high' ? 'bg-danger/15 text-danger' :
                            d.impact === 'medium' ? 'bg-warning/15 text-warning' :
                            'bg-surface-raised text-muted'
                          }`}>{d.impact}</span>
                          <div>
                            <p className="text-muted">Profile: {d.profile_says}</p>
                            <p className="text-foreground/85">JD: {d.jd_says}</p>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <button
                onClick={copy}
                tabIndex={expanded ? undefined : -1}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-surface-raised hover:bg-border-subtle text-sm rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
              >
                {copied ? (
                  <Check className="w-4 h-4 text-score-high" aria-hidden="true" />
                ) : (
                  <Copy className="w-4 h-4" aria-hidden="true" />
                )}
                {copied ? 'Copied!' : 'Copy gap summary'}
              </button>
            </>
          )}
          </div>
        </div>
      </div>
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
        <h1 className="font-display text-4xl tracking-tight mb-8">Gap Analysis</h1>

        {/* Section 1: Profile vs CV */}
        <section className="mb-10">
          <h2 className="font-display text-2xl mb-4 text-foreground">Profile vs CV</h2>
          {loadingProfileCV ? (
            <div className="space-y-2">
              <p className="text-sm text-muted">Analyzing alignment...</p>
              <ProfileCVSkeleton />
            </div>
          ) : errorProfileCV ? (
            <p className="text-sm text-danger">Error: {errorProfileCV}</p>
          ) : profileCV?.empty ? (
            <div className="bg-surface border border-dashed border-border-subtle rounded-xl p-6 text-center">
              <p className="text-muted text-sm">{profileCV.reason}</p>
              <Link href="/settings" className="mt-2 inline-block text-sm text-accent hover:text-accent-hover underline transition-colors">
                Go to Settings
              </Link>
            </div>
          ) : profileCV ? (
            <div className="space-y-4">
              {/* Score + positioning note */}
              <div className="bg-surface border border-border rounded-xl p-6 space-y-3">
                <AlignmentScore score={profileCV.alignment_score} />
                {profileCV.positioning_notes && (
                  <p className="font-display italic text-[0.95rem] text-foreground/85 leading-relaxed">{profileCV.positioning_notes}</p>
                )}
              </div>

              {/* Strengths */}
              {profileCV.strengths?.length > 0 && (
                <div className="bg-surface border border-border rounded-xl p-5">
                  <p className="cw-label text-subtle mb-3">Strengths</p>
                  <ul className="space-y-2">
                    {profileCV.strengths.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <Check className="w-4 h-4 text-score-high flex-shrink-0 mt-0.5" aria-hidden="true" />
                        <span className="text-foreground/90">{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Gaps */}
              {profileCV.gaps?.length > 0 && (
                <div className="space-y-3">
                  <p className="cw-label text-subtle">Gaps</p>
                  {profileCV.gaps.map((g, i) => (
                    <div key={i} className={`rounded-xl p-5 border ${severityColor(g.severity)}`}>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="font-medium text-foreground">{g.area}</span>
                        <span className={`px-2 py-0.5 rounded text-xs ${severityBadge(g.severity)}`}>{g.severity}</span>
                      </div>
                      <div className="space-y-1.5 text-sm">
                        <p><span className="text-muted">Profile targets:</span> <span className="text-foreground/90">{g.profile_says}</span></p>
                        <p><span className="text-muted">CV shows:</span> <span className="text-foreground/90">{g.cv_shows}</span></p>
                        {g.suggestion && (
                          <p className="mt-2 pt-2 border-t border-border">
                            <span className="text-muted">Suggestion:</span>{' '}
                            <span className="text-foreground/90">{g.suggestion}</span>
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
          <h2 className="font-display text-2xl mb-4 text-foreground">Position gaps (score &ge; 6)</h2>
          {loadingPositions ? (
            <div className="space-y-3">
              <p className="text-sm text-muted">Analyzing positions... this may take a minute.</p>
              {[0, 1, 2].map(i => <PositionRowSkeleton key={i} />)}
            </div>
          ) : errorPositions ? (
            <p className="text-sm text-danger">Error: {errorPositions}</p>
          ) : !positions || positions.length === 0 ? (
            <div className="bg-surface border border-dashed border-border-subtle rounded-xl p-6 text-center">
              <p className="text-muted text-sm">No positions scored 6 or above yet.</p>
              <Link href="/digest" className="mt-2 inline-block text-sm text-accent hover:text-accent-hover underline transition-colors">
                Run scoring first
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              <input
                value={filter}
                onChange={e => setFilter(e.target.value)}
                placeholder="Filter by company or title..."
                className="w-full bg-surface-raised text-foreground px-3 py-2 rounded-lg border border-subtle text-sm focus:outline-none focus:border-accent transition-colors"
              />
              {filteredPositions.length === 0 ? (
                <p className="text-sm text-subtle py-4 text-center">No matches for &ldquo;{filter}&rdquo;</p>
              ) : (
                filteredPositions.map(pos => <PositionRow key={pos.job_id} pos={pos} />)
              )}
            </div>
          )}
        </section>
    </div>
  )
}
