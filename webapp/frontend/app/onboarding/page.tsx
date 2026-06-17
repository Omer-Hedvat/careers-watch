'use client'

import { useState } from 'react'
import { supabase } from '@/lib/supabaseClient'

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

type Filters = {
  location_terms: string[]
  skip_title_terms: string[]
  keep_title_terms: string[]
  skip_companies: string[]
  skip_industries: string[]
}

function TagInput({ tags, onChange, placeholder }: { tags: string[]; onChange: (t: string[]) => void; placeholder?: string }) {
  const [input, setInput] = useState('')
  function addTag(val: string) {
    const trimmed = val.trim().replace(/,$/, '')
    if (trimmed && !tags.includes(trimmed)) onChange([...tags, trimmed])
    setInput('')
  }
  return (
    <div className="flex flex-wrap gap-1 p-2 bg-gray-800 rounded-lg border border-gray-700 min-h-[42px]">
      {tags.map(t => (
        <span key={t} className="flex items-center gap-1 px-2 py-0.5 bg-gray-700 rounded text-sm text-white">
          {t}
          <button onClick={() => onChange(tags.filter(x => x !== t))} className="text-gray-400 hover:text-white">×</button>
        </span>
      ))}
      <input
        value={input}
        placeholder={placeholder}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => {
          if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); addTag(input) }
        }}
        onBlur={() => input && addTag(input)}
        className="flex-1 min-w-[120px] bg-transparent text-white text-sm outline-none placeholder-gray-500"
      />
    </div>
  )
}

export default function OnboardingPage() {
  const [step, setStep] = useState(1)
  const [profileMd, setProfileMd] = useState('')
  const [cvText, setCvText] = useState('')
  const [geminiKey, setGeminiKey] = useState('')
  const [locationInput, setLocationInput] = useState('')
  const [filters, setFilters] = useState<Filters>({
    location_terms: [],
    skip_title_terms: ['data engineer', 'analyst', 'data analyst', 'bi developer', 'bi analyst'],
    keep_title_terms: [],
    skip_companies: [],
    skip_industries: ['gaming', 'adtech', 'gambling', 'crypto'],
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [pdfLoading, setPdfLoading] = useState(false)
  const [pdfError, setPdfError] = useState('')
  const [showKeyHelp, setShowKeyHelp] = useState(false)
  const [copied, setCopied] = useState(false)
  const [mdUploadError, setMdUploadError] = useState('')
  const [keyTestResult, setKeyTestResult] = useState('')
  const [keyTesting, setKeyTesting] = useState(false)

  async function testKeyInline() {
    setKeyTesting(true)
    setKeyTestResult('')
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token ?? ''
      const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/test-key-inline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ gemini_api_key: geminiKey }),
      })
      const d = await r.json()
      setKeyTestResult(r.ok ? 'Key works!' : (d.detail ?? 'Test failed'))
    } catch {
      setKeyTestResult('Test failed - check your connection')
    } finally {
      setKeyTesting(false)
    }
  }

  function copyPrompt() {
    navigator.clipboard.writeText(PROFILE_PROMPT)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
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

  async function finish() {
    setSaving(true)
    setError('')
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token
      if (!token) throw new Error('Not authenticated')

      const effectiveFilters = {
        ...filters,
        location_terms: locationInput.trim() ? [locationInput.trim()] : [],
      }

      const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ profile_md: profileMd, cv_text: cvText, gemini_api_key: geminiKey, filters: effectiveFilters }),
      })
      if (!r.ok) throw new Error('Setup failed')

      // Trigger first scoring run (ignore errors - user can retry)
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/score/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => {})
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Something went wrong')
      setSaving(false)
      return
    }
    window.location.href = '/digest'
  }

  const steps = ['Profile', 'CV', 'API Key', 'Filters']

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-4 py-12">
      {/* Progress */}
      <div className="flex gap-3 mb-8">
        {steps.map((label, i) => (
          <div key={label} className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${i + 1 <= step ? 'bg-green-600' : 'bg-gray-700'}`}>
              {i + 1}
            </div>
            <span className={`text-sm hidden sm:block ${i + 1 === step ? 'text-white' : 'text-gray-500'}`}>{label}</span>
          </div>
        ))}
      </div>

      <div className="bg-gray-900 rounded-xl p-8 w-full max-w-2xl">

        {/* Step 1 */}
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Set up your profile <span className="text-sm font-normal text-gray-500">(optional)</span></h2>
            <p className="text-gray-400 text-sm">Your profile tells the AI what to look for - roles, domains, location, dealbreakers, and a scoring rubric. You can skip this and add it later in settings.</p>

            {/* Path A: Upload */}
            <div>
              <label className="text-sm text-gray-400 block mb-1">Upload an existing profile.md</label>
              <input
                type="file"
                accept=".md"
                onChange={e => { const f = e.target.files?.[0]; if (f) uploadMdFile(f); e.target.value = '' }}
                className="block w-full text-sm text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-gray-700 file:text-white file:text-sm hover:file:bg-gray-600 cursor-pointer"
              />
              {mdUploadError && <p className="text-sm text-red-400 mt-1">{mdUploadError}</p>}
            </div>

            {/* Path B: Generate with AI */}
            <div className="space-y-2 bg-gray-800/50 rounded-xl p-4 border border-gray-700">
              <p className="text-sm font-medium text-white">Or generate one with AI</p>
              <p className="text-xs text-gray-400 mb-2">Step 1 - Copy this prompt. Step 2 - Paste into ChatGPT, Claude, or any LLM and answer its questions. Step 3 - Paste the result below.</p>
              <div className="relative">
                <textarea readOnly value={PROFILE_PROMPT} rows={8} className="w-full bg-gray-800 text-gray-300 font-mono text-xs p-3 rounded-lg border border-gray-700 resize-none" />
                <button onClick={copyPrompt} className="absolute top-2 right-2 px-2 py-1 bg-gray-700 hover:bg-gray-600 text-xs rounded">
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>

            <textarea value={profileMd} onChange={e => setProfileMd(e.target.value)} rows={8}
              placeholder="Paste the LLM output here (or your profile.md content)..."
              className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-700 resize-none focus:outline-none focus:border-green-500" />
            <div className="flex justify-end">
              <button onClick={() => setStep(2)} className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium">{profileMd.trim() ? 'Next ->' : 'Skip ->'}</button>
            </div>
          </div>
        )}

        {/* Step 2 */}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Upload your CV <span className="text-sm font-normal text-gray-500">(optional)</span></h2>
            <p className="text-gray-400 text-sm">Your CV is used verbatim in scoring prompts. You can skip this and add it later in settings.</p>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Upload CV (PDF, DOCX, TXT)</label>
              <input
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={async (e) => {
                  const file = e.target.files?.[0]
                  if (!file) return
                  setPdfLoading(true)
                  setPdfError('')
                  try {
                    const buf = await file.arrayBuffer()
                    const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)))
                    const { data: { session } } = await supabase.auth.getSession()
                    const token = session?.access_token ?? ''
                    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/parse-cv`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                      body: JSON.stringify({ pdf_b64: b64, mime_type: file.type || 'application/pdf' }),
                    })
                    const data = await res.json()
                    if (!res.ok) throw new Error(data.detail ?? 'Extraction failed')
                    setCvText(data.text)
                  } catch (err: unknown) {
                    setPdfError(err instanceof Error ? err.message : 'Could not extract text - please paste manually')
                  } finally {
                    setPdfLoading(false)
                  }
                }}
                className="block w-full text-sm text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-gray-700 file:text-white file:text-sm hover:file:bg-gray-600 cursor-pointer"
              />
              {pdfLoading && <p className="text-sm text-gray-400 mt-1">Extracting text...</p>}
              {pdfError && <p className="text-sm text-red-400 mt-1">{pdfError}</p>}
              <p className="text-xs text-gray-500 mt-1">Or paste text directly below</p>
            </div>
            <textarea value={cvText} onChange={e => setCvText(e.target.value)} rows={12} placeholder="Paste your CV text here..." className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-700 resize-none focus:outline-none focus:border-green-500" />
            <div className="flex justify-between">
              <button onClick={() => setStep(1)} className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg">&lt;- Back</button>
              <button onClick={() => setStep(3)} className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium">{cvText.trim() ? 'Next ->' : 'Skip ->'}</button>
            </div>
          </div>
        )}

        {/* Step 3 */}
        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Your Gemini API key</h2>
            <p className="text-gray-400 text-sm">Used only for scoring. Never logged or shared.</p>
            <p className="text-sm text-green-400">It&apos;s fully free - Google&apos;s Gemini API has a free tier that&apos;s plenty for scoring jobs. <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="underline">Get your free key here</a>.</p>
            <input type="password" value={geminiKey} onChange={e => { setGeminiKey(e.target.value); setKeyTestResult('') }} placeholder="AIza..." className="w-full bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-green-500" />
            <div className="flex items-center gap-3">
              <button onClick={testKeyInline} disabled={!geminiKey.trim() || keyTesting}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 rounded-lg text-sm">
                {keyTesting ? 'Testing...' : 'Test key'}
              </button>
              {keyTestResult && (
                <span className={`text-sm ${keyTestResult === 'Key works!' ? 'text-green-400' : 'text-red-400'}`}>
                  {keyTestResult}
                </span>
              )}
            </div>
            <button onClick={() => setShowKeyHelp(!showKeyHelp)} className="text-sm text-green-400 hover:text-green-300">
              {showKeyHelp ? '▾' : '▸'} How to get a key
            </button>
            {showKeyHelp && (
              <ol className="text-sm text-gray-400 space-y-1 list-decimal list-inside bg-gray-800 p-4 rounded-lg">
                <li>Go to <a href="https://aistudio.google.com" target="_blank" rel="noopener noreferrer" className="text-green-400 underline">Google AI Studio</a></li>
                <li>Sign in with your Google account</li>
                <li>Click &quot;Get API key&quot; then &quot;Create API key&quot;</li>
                <li>Copy and paste the key here</li>
                <li>The free tier is enough to get started (quota resets daily)</li>
              </ol>
            )}
            <p className="text-xs text-gray-500">We never score jobs without your key. If you delete it, scoring stops.</p>
            <div className="flex justify-between">
              <button onClick={() => setStep(2)} className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg">&lt;- Back</button>
              <button onClick={() => setStep(4)} disabled={!geminiKey.trim()} className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-40 rounded-lg font-medium">Next -&gt;</button>
            </div>
          </div>
        )}

        {/* Step 4 */}
        {step === 4 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Configure filters</h2>
            <p className="text-gray-400 text-sm">Jobs not matching these filters are dropped before scoring.</p>

            <div>
              <label className="text-sm text-gray-400 block mb-1">Location (leave blank for no filter)</label>
              <input value={locationInput} onChange={e => setLocationInput(e.target.value)} placeholder="e.g. israel" className="w-full bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-green-500" />
            </div>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Title denylist (auto-excluded titles)</label>
              <TagInput tags={filters.skip_title_terms} onChange={v => setFilters(f => ({ ...f, skip_title_terms: v }))} placeholder="add term, press Enter" />
            </div>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Title allowlist (leave blank to score everything)</label>
              <TagInput tags={filters.keep_title_terms} onChange={v => setFilters(f => ({ ...f, keep_title_terms: v }))} placeholder="add term, press Enter" />
            </div>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Excluded companies</label>
              <TagInput tags={filters.skip_companies} onChange={v => setFilters(f => ({ ...f, skip_companies: v }))} placeholder="company name, press Enter" />
            </div>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Excluded industries</label>
              <TagInput tags={filters.skip_industries} onChange={v => setFilters(f => ({ ...f, skip_industries: v }))} placeholder="industry, press Enter" />
            </div>

            {error && <p className="text-red-400 text-sm">{error}</p>}
            <div className="flex justify-between">
              <button onClick={() => setStep(3)} className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg">&lt;- Back</button>
              <button onClick={finish} disabled={saving} className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-40 rounded-lg font-medium">
                {saving ? 'Starting...' : 'Start scoring ->'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
