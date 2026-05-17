'use client'

import { useState } from 'react'
import { supabase } from '@/lib/supabaseClient'

const PROFILE_PROMPT = `I'm setting up a job-matching tool that scores job postings against my profile.
I need you to create a profile.md file for me by asking me questions about:
- My background and years of experience
- My target roles (title, seniority)
- My preferred domains/industries
- What I consider a strong fit vs. a dealbreaker
- My location and commute constraints
- What I explicitly don't want

Ask me one section at a time. When done, output a complete profile.md in markdown.`

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
  const [showKeyHelp, setShowKeyHelp] = useState(false)
  const [copied, setCopied] = useState(false)

  function copyPrompt() {
    navigator.clipboard.writeText(PROFILE_PROMPT)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
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
            <h2 className="text-2xl font-bold">Generate your profile</h2>
            <p className="text-gray-400 text-sm">Your profile tells the AI what to look for. Use an AI assistant to generate it.</p>
            <div className="relative">
              <textarea readOnly value={PROFILE_PROMPT} rows={9} className="w-full bg-gray-800 text-gray-300 font-mono text-xs p-3 rounded-lg border border-gray-700 resize-none" />
              <button onClick={copyPrompt} className="absolute top-2 right-2 px-2 py-1 bg-gray-700 hover:bg-gray-600 text-xs rounded">
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <p className="text-sm text-gray-400">Paste your profile.md result here:</p>
            <textarea value={profileMd} onChange={e => setProfileMd(e.target.value)} rows={8} placeholder="# My Profile&#10;&#10;..." className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-700 resize-none focus:outline-none focus:border-green-500" />
            <div className="flex justify-end">
              <button onClick={() => setStep(2)} disabled={!profileMd.trim()} className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-40 rounded-lg font-medium">Next -&gt;</button>
            </div>
          </div>
        )}

        {/* Step 2 */}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Upload your CV</h2>
            <p className="text-gray-400 text-sm">Your CV is used verbatim in scoring prompts.</p>
            <textarea value={cvText} onChange={e => setCvText(e.target.value)} rows={12} placeholder="Paste your CV text here..." className="w-full bg-gray-800 text-white p-3 rounded-lg border border-gray-700 resize-none focus:outline-none focus:border-green-500" />
            <div className="flex justify-between">
              <button onClick={() => setStep(1)} className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg">&lt;- Back</button>
              <button onClick={() => setStep(3)} disabled={!cvText.trim()} className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-40 rounded-lg font-medium">Next -&gt;</button>
            </div>
          </div>
        )}

        {/* Step 3 */}
        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Your Gemini API key</h2>
            <p className="text-gray-400 text-sm">Used only for scoring. Never logged or shared.</p>
            <input type="password" value={geminiKey} onChange={e => setGeminiKey(e.target.value)} placeholder="AIza..." className="w-full bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-green-500" />
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
