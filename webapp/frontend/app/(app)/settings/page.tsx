'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { AlertTriangle, Check, ChevronDown, ChevronRight } from 'lucide-react'
import { supabase } from '@/lib/supabaseClient'

type Tab = 'profile' | 'cv' | 'filters' | 'apikey' | 'account'

const PROFILE_PROMPT = `You are helping me create a job-matching profile file. I will answer your questions and you will produce a structured Markdown document called profile.md that a job-scoring AI will use to evaluate job postings for me.

Ask me the following questions one at a time (or ask them all at once and I will answer):

1. What is your current title and how many years of experience do you have?
2. What is your primary specialization - the area where you are stronger than most people at your level?
3. What job titles are you targeting, in priority order? (e.g. "Team Lead DS first, Senior DS second")
4. What domains do you want to work in? (e.g. cyber security, fraud, fintech, healthcare, general SaaS). Which are required vs. preferred?
5. Where are you located and what is your maximum commute time? Are you open to hybrid, fully remote, or relocation?
6. What are your absolute dealbreakers - roles or companies you will not consider no matter how good the title looks?
7. What specific technologies, methodologies, or company stages are a strong signal that a role is right for you?
8. What kinds of roles look good on paper but are actually wrong for you? (e.g. "MLOps-heavy roles", "pure research", "customer-facing")
9. What nuances should the scorer know that are easy to get wrong? (e.g. "I have military leadership but no formal DS manager title - treat it as a partial fit, not a miss")
10. What does a 9-10 role look like for you? What does a 5-6 look like?

After I answer, produce a profile.md with these exact sections:
- # Candidate Profile
- ## Who I am, in one paragraph
- ## What I'm looking for, in priority order
- ## Location
- ## Strong fit signals (boost the score)
- ## Weak fit / skip (drop the score)
- ## Dealbreakers (score = 0, do not surface)
- ## Notes for the matcher
- ## Scoring rubric for the matcher

Write the scoring rubric as explicit score bands: what a 9-10 looks like, what a 7-8 looks like, what a 5-6 looks like, and what 0-2 means. Be specific - reference the role types and signals I described.`

function TagInput({ tags, onChange, placeholder }: { tags: string[]; onChange: (t: string[]) => void; placeholder?: string }) {
  const [input, setInput] = useState('')
  function addTag(val: string) {
    const trimmed = val.trim().replace(/,$/, '')
    if (trimmed && !tags.includes(trimmed)) onChange([...tags, trimmed])
    setInput('')
  }
  return (
    <div className="flex flex-wrap gap-1.5 p-2 bg-surface-raised rounded-lg border border-border min-h-[42px] transition-colors focus-within:border-accent">
      {tags.length === 0 && !input && (
        <span className="text-sm text-subtle self-center px-1">None set</span>
      )}
      {tags.map(t => (
        <span key={t} className="flex items-center gap-1 px-2 py-0.5 bg-surface border border-border rounded text-sm text-foreground">
          {t}
          <button type="button" aria-label={`Remove ${t}`} onClick={() => onChange(tags.filter(x => x !== t))} className="text-muted hover:text-foreground transition-colors rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"><span aria-hidden="true">×</span></button>
        </span>
      ))}
      <input
        value={input}
        placeholder={tags.length === 0 ? undefined : placeholder}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); addTag(input) } }}
        onBlur={() => input && addTag(input)}
        className="flex-1 min-w-[120px] bg-transparent text-foreground text-sm outline-none placeholder:text-subtle"
      />
    </div>
  )
}

type FilterPanelProps = {
  locationInput: string
  onLocationChange: (v: string) => void
  skipTitles: string[]
  onSkipTitlesChange: (v: string[]) => void
  keepTitles: string[]
  onKeepTitlesChange: (v: string[]) => void
  skipCompanies: string[]
  onSkipCompaniesChange: (v: string[]) => void
  skipIndustries: string[]
  onSkipIndustriesChange: (v: string[]) => void
  preview: { passing: number; total: number; empty: boolean } | null
  previewLoading: boolean
}

function FilterPanel({ locationInput, onLocationChange, skipTitles, onSkipTitlesChange, keepTitles, onKeepTitlesChange, skipCompanies, onSkipCompaniesChange, skipIndustries, onSkipIndustriesChange, preview, previewLoading }: FilterPanelProps) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm text-muted block mb-1">
          Location filter <span title="Only score jobs whose location contains this text (e.g. 'israel')" className="text-subtle cursor-help">(?)</span>
        </label>
        <input value={locationInput} onChange={e => onLocationChange(e.target.value)} placeholder="e.g. israel (leave blank for no filter)"
          className="w-full bg-surface-raised text-foreground px-3 py-2 rounded-lg border border-border placeholder:text-subtle transition-colors focus:outline-none focus:border-accent" />
      </div>
      <div>
        <label className="text-sm text-muted block mb-1">
          Skip jobs whose title contains... <span title="Jobs with these words in the title are dropped before scoring (e.g. 'data engineer, analyst')" className="text-subtle cursor-help">(?)</span>
        </label>
        <p className="text-xs text-subtle mb-1">e.g. data engineer, analyst, bi developer</p>
        <TagInput tags={skipTitles} onChange={onSkipTitlesChange} placeholder="add term, press Enter" />
      </div>
      <div>
        <label className="text-sm text-muted block mb-1">
          Only score jobs whose title contains at least one of... <span title="Leave blank to score all titles. Add terms to score only matching titles (e.g. 'data scientist, ml engineer')" className="text-subtle cursor-help">(?)</span>
        </label>
        <p className="text-xs text-subtle mb-1">Leave blank to score all titles</p>
        <TagInput tags={keepTitles} onChange={onKeepTitlesChange} placeholder="add term, press Enter" />
      </div>
      <div>
        <label className="text-sm text-muted block mb-1">
          Skip these companies <span title="Jobs from these companies are dropped before scoring" className="text-subtle cursor-help">(?)</span>
        </label>
        <TagInput tags={skipCompanies} onChange={onSkipCompaniesChange} placeholder="company name, press Enter" />
      </div>
      <div>
        <label className="text-sm text-muted block mb-1">
          Skip these industries <span title="Jobs tagged with these industries are dropped before scoring" className="text-subtle cursor-help">(?)</span>
        </label>
        <p className="text-xs text-subtle mb-1">e.g. gaming, adtech, gambling</p>
        <TagInput tags={skipIndustries} onChange={onSkipIndustriesChange} placeholder="industry, press Enter" />
      </div>
      {/* Live preview */}
      <div className="text-sm text-muted bg-surface-raised border border-border rounded-lg px-3 py-2">
        {previewLoading ? 'Calculating preview...' :
          preview === null ? '' :
          preview.empty ? 'No collected jobs yet - run the pipeline first.' :
          `With these filters, ${preview.passing} of today's ${preview.total} collected jobs will be sent for scoring.`
        }
      </div>
    </div>
  )
}

export default function SettingsPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<Tab>('profile')
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  // Profile tab
  const [profileMd, setProfileMd] = useState('')
  const [profileVersion, setProfileVersion] = useState<number>(1)
  const [profileUpdatedAt, setProfileUpdatedAt] = useState<string | null>(null)
  const [showPrompt, setShowPrompt] = useState(false)
  const [copiedPrompt, setCopiedPrompt] = useState(false)
  const [mdUploadError, setMdUploadError] = useState('')

  // CV tab
  const [cvText, setCvText] = useState('')
  const [cvUpdatedAt, setCvUpdatedAt] = useState<string | null>(null)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [pdfError, setPdfError] = useState('')

  // Filters tab
  const [locationInput, setLocationInput] = useState('')
  const [skipTitles, setSkipTitles] = useState<string[]>([])
  const [keepTitles, setKeepTitles] = useState<string[]>([])
  const [skipCompanies, setSkipCompanies] = useState<string[]>([])
  const [skipIndustries, setSkipIndustries] = useState<string[]>([])

  // Filter preview
  const [filterPreview, setFilterPreview] = useState<{ passing: number; total: number; empty: boolean } | null>(null)
  const [filterPreviewLoading, setFilterPreviewLoading] = useState(false)

  // API Key tab
  const [newKey, setNewKey] = useState('')
  const [testResult, setTestResult] = useState('')
  const [hasApiKey, setHasApiKey] = useState<boolean | null>(null)
  const [apiKeyLast4, setApiKeyLast4] = useState<string | null>(null)

  // Account tab
  const [newEmail, setNewEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState(false)
  const [userIdentity, setUserIdentity] = useState<{
    name: string; email: string; provider: string; memberSince: string
  } | null>(null)

  async function getToken() {
    const { data: { session } } = await supabase.auth.getSession()
    return session?.access_token ?? ''
  }

  async function api(path: string, opts: RequestInit = {}) {
    const token = await getToken()
    return fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
      ...opts,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, ...(opts.headers ?? {}) },
    })
  }

  function flash(m: string) { setMsg(m); setTimeout(() => setMsg(''), 3000) }

  async function fetchFilterPreview(loc: string, st: string[], kt: string[], sc: string[], si: string[]) {
    setFilterPreviewLoading(true)
    try {
      const token = await getToken()
      const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs/filter-preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          location_terms: loc.trim() ? [loc.trim()] : [],
          skip_title_terms: st,
          keep_title_terms: kt,
          skip_companies: sc,
          skip_industries: si,
        }),
      })
      if (r.ok) setFilterPreview(await r.json())
    } catch { /* silent */ } finally {
      setFilterPreviewLoading(false)
    }
  }

  async function loadMe() {
    const r = await api('/user/me')
    const d = await r.json()
    setProfileMd(d.profile_md ?? '')
    setProfileVersion(d.profile_version ?? 1)
    setProfileUpdatedAt(d.profile_updated_at ?? null)
    setCvText(d.cv_text ?? '')
    setCvUpdatedAt(d.cv_updated_at ?? null)
    setHasApiKey(d.has_api_key ?? false)
    setApiKeyLast4(d.api_key_last4 ?? null)
  }

  useEffect(() => {
    loadMe()
    api('/user/filters').then(r => r.json()).then(d => {
      setLocationInput((d.location_terms ?? [])[0] ?? '')
      setSkipTitles(d.skip_title_terms ?? [])
      setKeepTitles(d.keep_title_terms ?? [])
      setSkipCompanies(d.skip_companies ?? [])
      setSkipIndustries(d.skip_industries ?? [])
    })
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) return
      const meta = user.user_metadata ?? {}
      const identities = user.identities ?? []
      const provider = identities[0]?.provider ?? 'email'
      setUserIdentity({
        name: meta.full_name ?? meta.name ?? '—',
        email: user.email ?? '—',
        provider: provider === 'google' ? 'Google' : 'Email',
        memberSince: user.created_at ? new Date(user.created_at).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }) : '—',
      })
    })
  }, [])

  useEffect(() => {
    if (activeTab !== 'filters') return
    const t = setTimeout(() => fetchFilterPreview(locationInput, skipTitles, keepTitles, skipCompanies, skipIndustries), 400)
    return () => clearTimeout(t)
  }, [activeTab, locationInput, skipTitles, keepTitles, skipCompanies, skipIndustries])

  async function saveProfile() {
    setSaving(true)
    const r = await api('/user/profile', { method: 'PATCH', body: JSON.stringify({ profile_md: profileMd }) })
    if (r.ok) {
      const d = await r.json()
      setProfileVersion(d.profile_version ?? (profileVersion + 1))
      setProfileUpdatedAt(d.profile_updated_at ?? null)
      flash('Profile saved')
    } else {
      flash('Save failed')
    }
    setSaving(false)
  }

  function uploadMdFile(file: File) {
    setMdUploadError('')
    if (!file.name.endsWith('.md') && file.type !== 'text/markdown' && file.type !== 'text/plain') {
      setMdUploadError('Only .md files are supported')
      return
    }
    if (file.size > 1024 * 1024) {
      setMdUploadError('File must be under 1 MB')
      return
    }
    const reader = new FileReader()
    reader.onload = e => {
      const text = e.target?.result as string
      setProfileMd(text)
    }
    reader.readAsText(file, 'utf-8')
  }

  async function saveCv() {
    setSaving(true)
    const r = await api('/user/cv', { method: 'PATCH', body: JSON.stringify({ cv_text: cvText }) })
    if (r.ok) {
      const d = await r.json()
      setCvUpdatedAt(d.cv_updated_at ?? null)
      flash('CV saved')
    } else {
      flash('Save failed')
    }
    setSaving(false)
  }

  function downloadCvText() {
    const blob = new Blob([cvText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'cv.txt'; a.click()
    URL.revokeObjectURL(url)
  }

  async function uploadCvFile(file: File) {
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain']
    if (!allowed.includes(file.type)) {
      setPdfError('Only PDF, DOCX, and TXT files are supported')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setPdfError('File must be under 10 MB')
      return
    }
    setPdfLoading(true)
    setPdfError('')
    try {
      const buf = await file.arrayBuffer()
      const bytes = new Uint8Array(buf)
      let binary = ''
      for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i])
      const b64 = btoa(binary)
      const token = await getToken()
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/parse-cv`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ pdf_b64: b64, mime_type: file.type }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail ?? 'Extraction failed')
      setCvText(data.text)
      const saveRes = await api('/user/cv', { method: 'PATCH', body: JSON.stringify({ cv_text: data.text }) })
      if (saveRes.ok) {
        const saved = await saveRes.json()
        setCvUpdatedAt(saved.cv_updated_at ?? null)
        flash('CV uploaded and saved')
      } else {
        flash('CV parsed - click Save CV to store it')
      }
    } catch (err: unknown) {
      setPdfError(err instanceof Error ? err.message : 'Could not extract text - please paste manually')
    } finally {
      setPdfLoading(false)
    }
  }

  async function saveFilters() {
    setSaving(true)
    const r = await api('/user/filters', {
      method: 'PATCH',
      body: JSON.stringify({
        location_terms: locationInput.trim() ? [locationInput.trim()] : [],
        skip_title_terms: skipTitles,
        keep_title_terms: keepTitles,
        skip_companies: skipCompanies,
        skip_industries: skipIndustries,
      }),
    })
    flash(r.ok ? 'Filters saved' : 'Save failed')
    setSaving(false)
  }

  async function saveKey() {
    setSaving(true)
    const r = await api('/user/apikey', { method: 'PATCH', body: JSON.stringify({ gemini_api_key: newKey }) })
    if (r.ok) {
      flash('API key updated')
      setNewKey('')
      await loadMe()
    } else {
      flash('Update failed')
    }
    setSaving(false)
  }

  async function testKey() {
    setTestResult('Testing...')
    const r = await api('/user/test-key', { method: 'POST' })
    const d = await r.json()
    setTestResult(r.ok ? 'Key works!' : d.detail ?? 'Test failed')
  }

  async function deleteKey() {
    await api('/user/apikey', { method: 'DELETE' })
    flash('API key deleted - scoring paused')
    await loadMe()
  }

  async function saveEmail() {
    const { error } = await supabase.auth.updateUser({ email: newEmail })
    if (!error) {
      setUserIdentity(id => id ? { ...id, email: newEmail } : id)
    }
    flash(error ? error.message : 'Email updated')
    setNewEmail('')
  }

  async function savePassword() {
    const { error } = await supabase.auth.updateUser({ password: newPassword })
    flash(error ? error.message : 'Password updated')
    setNewPassword('')
  }

  async function exportData() {
    const token = await getToken()
    const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/export`, { headers: { Authorization: `Bearer ${token}` } })
    const blob = await r.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'careerwatch_export.json'; a.click()
    URL.revokeObjectURL(url)
  }

  async function deleteAccount() {
    await api('/user/account', { method: 'DELETE' })
    await supabase.auth.signOut()
    router.push('/')
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: 'profile', label: 'Profile' },
    { id: 'cv', label: 'CV' },
    { id: 'filters', label: 'Filters' },
    { id: 'apikey', label: 'API Key' },
    { id: 'account', label: 'Account' },
  ]

  const cvWordCount = cvText ? cvText.split(/\s+/).filter(Boolean).length : 0

  const primaryBtn = 'px-4 py-2 bg-accent hover:bg-accent-hover text-accent-foreground disabled:opacity-50 rounded-lg text-sm font-medium transition-colors'
  const secondaryBtn = 'px-4 py-2 bg-surface-raised hover:bg-border-subtle/50 border border-border rounded-lg text-sm transition-colors'
  const dangerBtn = 'px-4 py-2 bg-danger/10 hover:bg-danger/20 border border-danger/30 text-danger rounded-lg text-sm transition-colors'
  const inputCls = 'bg-surface-raised text-foreground px-3 py-2 rounded-lg border border-border placeholder:text-subtle transition-colors focus:outline-none focus:border-accent'
  const fileInputCls = 'block text-sm text-muted file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-accent file:text-accent-foreground file:text-sm file:font-medium hover:file:bg-accent-hover file:transition-colors file:cursor-pointer cursor-pointer'

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="font-display text-4xl tracking-tight mb-6">Settings</h1>

      {msg && <div className="mb-4 px-4 py-2 bg-surface-raised border border-border rounded-lg text-sm">{msg}</div>}

        {/* Tab bar */}
        <div className="flex border-b border-border mb-6 overflow-x-auto">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 text-sm font-medium whitespace-nowrap -mb-px border-b-2 transition-colors ${activeTab === t.id ? 'text-foreground border-accent' : 'text-muted hover:text-foreground border-transparent'}`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Profile tab */}
        {activeTab === 'profile' && (
          <div className="space-y-4">
            {/* Status */}
            <div className="text-sm text-muted">
              {profileMd.trim()
                ? <span className="text-score-high">
                    Profile saved · v{profileVersion}
                    {profileUpdatedAt && ` · updated ${new Date(profileUpdatedAt).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}`}
                  </span>
                : <span className="text-warning">No profile yet - upload a file or generate one with AI below</span>
              }
            </div>

            {/* Path A: Upload .md */}
            <div>
              <label className="text-sm text-muted block mb-1">Upload profile.md</label>
              <input
                type="file"
                accept=".md"
                onChange={e => { const f = e.target.files?.[0]; if (f) uploadMdFile(f); e.target.value = '' }}
                className={fileInputCls}
              />
              {mdUploadError && <p className="text-sm text-danger mt-1">{mdUploadError}</p>}
            </div>

            {/* Path B: Generate with AI */}
            <button type="button" aria-expanded={showPrompt} onClick={() => setShowPrompt(v => !v)} className={`${secondaryBtn} inline-flex items-center gap-1.5`}>
              {showPrompt ? <ChevronDown className="w-3.5 h-3.5" aria-hidden="true" /> : <ChevronRight className="w-3.5 h-3.5" aria-hidden="true" />} Generate with AI
            </button>
            {showPrompt && (
              <div className="space-y-3 bg-surface rounded-xl p-4 border border-border">
                <p className="text-sm font-medium text-foreground">Step 1 - Copy this prompt</p>
                <div className="relative">
                  <textarea readOnly value={PROFILE_PROMPT} rows={10}
                    className="w-full bg-surface-raised font-mono text-xs p-3 rounded-lg border border-border resize-none text-muted focus:outline-none" />
                  <button
                    onClick={() => { navigator.clipboard.writeText(PROFILE_PROMPT); setCopiedPrompt(true); setTimeout(() => setCopiedPrompt(false), 2000) }}
                    className="absolute top-2 right-2 px-2 py-1 bg-surface-raised border border-border hover:bg-border-subtle/50 text-xs rounded transition-colors">
                    {copiedPrompt ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <p className="text-sm text-muted">
                  <span className="font-medium text-foreground">Step 2</span> - Open ChatGPT, Claude, Gemini, or any LLM you prefer. Paste this prompt and answer the questions it asks. The LLM will output a ready-to-use profile.md file.
                </p>
                <p className="text-sm text-muted">
                  <span className="font-medium text-foreground">Step 3</span> - Paste the LLM output into the editor below and click Save profile.
                </p>
              </div>
            )}

            {/* Profile editor */}
            <textarea value={profileMd} onChange={e => setProfileMd(e.target.value)} rows={20}
              placeholder="Paste your profile.md here..."
              className="w-full bg-surface text-foreground p-4 rounded-xl border border-border font-mono text-sm placeholder:text-subtle resize-none transition-colors focus:outline-none focus:border-accent" />
            <button onClick={saveProfile} disabled={saving} className={primaryBtn}>Save profile</button>
          </div>
        )}

        {/* CV tab */}
        {activeTab === 'cv' && (
          <div className="space-y-4">
            {/* Current state header */}
            {cvText ? (
              <div className="flex items-center justify-between text-xs text-subtle font-mono">
                <span>
                  {cvText.length.toLocaleString()} chars · {cvWordCount.toLocaleString()} words
                  {cvUpdatedAt && ` · updated ${new Date(cvUpdatedAt).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}`}
                </span>
                <button onClick={downloadCvText} className="text-accent hover:text-accent-hover underline transition-colors">Download as .txt</button>
              </div>
            ) : (
              <p className="text-sm text-subtle">No CV on file yet. Upload a file or paste text below.</p>
            )}
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm text-muted block mb-1">Upload CV (PDF, DOCX, TXT)</label>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={e => { const f = e.target.files?.[0]; if (f) uploadCvFile(f); e.target.value = '' }}
                  className={fileInputCls}
                />
              </div>
            </div>
            {pdfLoading && <p className="text-sm text-muted">Extracting text...</p>}
            {pdfError && <p className="text-sm text-danger">{pdfError}</p>}
            <textarea value={cvText} onChange={e => setCvText(e.target.value)} rows={18}
              placeholder="Or paste your CV text here..."
              className="w-full bg-surface text-foreground p-4 rounded-xl border border-border text-sm placeholder:text-subtle resize-none transition-colors focus:outline-none focus:border-accent" />
            <button onClick={saveCv} disabled={saving} className={primaryBtn}>Save CV</button>
          </div>
        )}

        {/* Filters tab */}
        {activeTab === 'filters' && (
          <div className="space-y-4">
            {/* Active filters summary */}
            <div className="text-xs text-subtle font-mono bg-surface border border-border px-3 py-2 rounded-lg">
              Location: {locationInput || 'none'}
              {' · '}{skipTitles.length} skip-title{skipTitles.length !== 1 ? 's' : ''}
              {' · '}{keepTitles.length} keep-title{keepTitles.length !== 1 ? 's' : ''}
              {' · '}{skipCompanies.length} excluded {skipCompanies.length !== 1 ? 'companies' : 'company'}
              {' · '}{skipIndustries.length} excluded {skipIndustries.length !== 1 ? 'industries' : 'industry'}
            </div>
            <FilterPanel
              locationInput={locationInput}
              onLocationChange={v => setLocationInput(v)}
              skipTitles={skipTitles}
              onSkipTitlesChange={setSkipTitles}
              keepTitles={keepTitles}
              onKeepTitlesChange={setKeepTitles}
              skipCompanies={skipCompanies}
              onSkipCompaniesChange={setSkipCompanies}
              skipIndustries={skipIndustries}
              onSkipIndustriesChange={setSkipIndustries}
              preview={filterPreview}
              previewLoading={filterPreviewLoading}
            />
            <button onClick={saveFilters} disabled={saving} className={primaryBtn}>Save filters</button>
          </div>
        )}

        {/* API Key tab */}
        {activeTab === 'apikey' && (
          <div className="space-y-4">
            {/* Status pill */}
            {hasApiKey !== null && (
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm border ${hasApiKey ? 'bg-score-high/10 border-score-high/25 text-score-high' : 'bg-warning/10 border-warning/30 text-warning'}`}>
                {hasApiKey
                  ? <span className="inline-flex items-center gap-1.5"><Check className="w-4 h-4" aria-hidden="true" /> Gemini key configured{apiKeyLast4 ? ` · AIza••••••••${apiKeyLast4}` : ''}</span>
                  : <span className="inline-flex items-center gap-1.5"><AlertTriangle className="w-4 h-4" aria-hidden="true" /> No API key - scoring is paused</span>
                }
              </div>
            )}
            <p className="text-sm text-muted">Replace your Gemini API key. The current key is never shown.</p>
            <p className="text-sm text-accent">It&apos;s fully free - Google&apos;s Gemini API has a free tier that&apos;s plenty for scoring jobs. <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="underline">Get your free key here</a>.</p>
            <ol className="text-sm text-muted space-y-1 list-decimal list-inside bg-surface border border-border p-4 rounded-lg">
              <li>Go to <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="text-accent underline">Google AI Studio</a></li>
              <li>Sign in with your Google account</li>
              <li>Click &quot;Get API key&quot; then &quot;Create API key&quot;</li>
              <li>Copy and paste the key below</li>
            </ol>
            <input type="password" value={newKey} onChange={e => setNewKey(e.target.value)} placeholder="AIza..."
              className={`w-full ${inputCls}`} />
            <div className="flex gap-3">
              <button onClick={saveKey} disabled={!newKey || saving} className={primaryBtn}>Replace key</button>
              <button onClick={testKey} className={secondaryBtn}>Test key</button>
              <button onClick={deleteKey} className={dangerBtn}>Delete key</button>
            </div>
            {testResult && <p className="text-sm text-muted">{testResult}</p>}
          </div>
        )}

        {/* Account tab */}
        {activeTab === 'account' && (
          <div className="space-y-6">
            {/* Read-only identity block */}
            {userIdentity && (
              <div className="bg-surface border border-border rounded-xl p-4 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted">Name</span>
                  <span>{userIdentity.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Email</span>
                  <span>{userIdentity.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Sign-in</span>
                  <span>{userIdentity.provider}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Member since</span>
                  <span>{userIdentity.memberSince}</span>
                </div>
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm text-muted block">New email</label>
              <div className="flex gap-2">
                <input type="email" value={newEmail} onChange={e => setNewEmail(e.target.value)} placeholder="new@email.com"
                  className={`flex-1 ${inputCls}`} />
                <button onClick={saveEmail} disabled={!newEmail} className={primaryBtn}>Save</button>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted block">New password</label>
              <div className="flex gap-2">
                <input type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} placeholder="new password"
                  className={`flex-1 ${inputCls}`} />
                <button onClick={savePassword} disabled={!newPassword} className={primaryBtn}>Save</button>
              </div>
            </div>
            <button onClick={exportData} className={secondaryBtn}>Export data (JSON)</button>
            <div className="border-t border-border pt-4">
              {!deleteConfirm ? (
                <button onClick={() => setDeleteConfirm(true)} className={dangerBtn}>Delete account</button>
              ) : (
                <div className="space-y-2">
                  <p className="text-sm text-danger">This will delete all your data permanently. Are you sure?</p>
                  <div className="flex gap-2">
                    <button onClick={deleteAccount} className="px-4 py-2 bg-danger hover:bg-danger/85 text-white rounded-lg text-sm transition-colors">Yes, delete everything</button>
                    <button onClick={() => setDeleteConfirm(false)} className={secondaryBtn}>Cancel</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
    </div>
  )
}
