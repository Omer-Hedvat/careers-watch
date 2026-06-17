'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabaseClient'

type Tab = 'profile' | 'cv' | 'filters' | 'apikey' | 'account'

const PROFILE_PROMPT = `I'm setting up a job-matching tool that scores job postings against my profile.
I need you to create a profile.md file for me by asking me questions about:
- My background and years of experience
- My target roles (title, seniority)
- My preferred domains/industries
- What I consider a strong fit vs. a dealbreaker
- My location and commute constraints
- What I explicitly don't want

Ask me one section at a time. When done, output a complete profile.md in markdown.`

function TagInput({ tags, onChange, placeholder }: { tags: string[]; onChange: (t: string[]) => void; placeholder?: string }) {
  const [input, setInput] = useState('')
  function addTag(val: string) {
    const trimmed = val.trim().replace(/,$/, '')
    if (trimmed && !tags.includes(trimmed)) onChange([...tags, trimmed])
    setInput('')
  }
  return (
    <div className="flex flex-wrap gap-1 p-2 bg-gray-800 rounded-lg border border-gray-700 min-h-[42px]">
      {tags.length === 0 && !input && (
        <span className="text-sm text-gray-600 self-center px-1">None set</span>
      )}
      {tags.map(t => (
        <span key={t} className="flex items-center gap-1 px-2 py-0.5 bg-gray-700 rounded text-sm text-white">
          {t}
          <button onClick={() => onChange(tags.filter(x => x !== t))} className="text-gray-400 hover:text-white">×</button>
        </span>
      ))}
      <input
        value={input}
        placeholder={tags.length === 0 ? undefined : placeholder}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); addTag(input) } }}
        onBlur={() => input && addTag(input)}
        className="flex-1 min-w-[120px] bg-transparent text-white text-sm outline-none placeholder-gray-500"
      />
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
  const [showPrompt, setShowPrompt] = useState(false)
  const [copiedPrompt, setCopiedPrompt] = useState(false)

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

  async function loadMe() {
    const r = await api('/user/me')
    const d = await r.json()
    setProfileMd(d.profile_md ?? '')
    setProfileVersion(d.profile_version ?? 1)
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

  async function saveProfile() {
    setSaving(true)
    const r = await api('/user/profile', { method: 'PATCH', body: JSON.stringify({ profile_md: profileMd }) })
    if (r.ok) {
      setProfileVersion(v => v + 1)
      flash('Profile saved')
    } else {
      flash('Save failed')
    }
    setSaving(false)
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
      const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)))
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

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Settings</h1>
          <a href="/digest" className="text-sm text-gray-400 hover:text-white">← Back to digest</a>
        </div>

        {msg && <div className="mb-4 px-4 py-2 bg-gray-800 rounded-lg text-sm">{msg}</div>}

        {/* Tab bar */}
        <div className="flex border-b border-gray-700 mb-6 overflow-x-auto">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 text-sm font-medium whitespace-nowrap ${activeTab === t.id ? 'text-white border-b-2 border-green-500' : 'text-gray-400 hover:text-white'}`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Profile tab */}
        {activeTab === 'profile' && (
          <div className="space-y-4">
            <div className="text-sm text-gray-400">
              {profileMd.trim()
                ? <span className="text-green-400">Profile saved · v{profileVersion}</span>
                : <span className="text-amber-400">No profile yet</span>
              }
            </div>
            <textarea value={profileMd} onChange={e => setProfileMd(e.target.value)} rows={20}
              className="w-full bg-gray-900 text-white p-4 rounded-xl border border-gray-700 font-mono text-sm resize-none focus:outline-none focus:border-green-500" />
            <div className="flex gap-3">
              <button onClick={saveProfile} disabled={saving} className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-lg text-sm font-medium">Save profile</button>
              <button onClick={() => setShowPrompt(v => !v)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm">Regenerate with AI</button>
            </div>
            {showPrompt && (
              <div className="relative">
                <textarea readOnly value={PROFILE_PROMPT} rows={8} className="w-full bg-gray-800 font-mono text-xs p-3 rounded-lg border border-gray-700 resize-none text-gray-300" />
                <button onClick={() => { navigator.clipboard.writeText(PROFILE_PROMPT); setCopiedPrompt(true); setTimeout(() => setCopiedPrompt(false), 2000) }}
                  className="absolute top-2 right-2 px-2 py-1 bg-gray-700 hover:bg-gray-600 text-xs rounded">
                  {copiedPrompt ? 'Copied!' : 'Copy'}
                </button>
              </div>
            )}
          </div>
        )}

        {/* CV tab */}
        {activeTab === 'cv' && (
          <div className="space-y-4">
            {/* Current state header */}
            {cvText ? (
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>
                  {cvText.length.toLocaleString()} chars · {cvWordCount.toLocaleString()} words
                  {cvUpdatedAt && ` · updated ${new Date(cvUpdatedAt).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}`}
                </span>
                <button onClick={downloadCvText} className="text-green-400 hover:text-green-300 underline">Download as .txt</button>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No CV on file yet. Upload a file or paste text below.</p>
            )}
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm text-gray-400 block mb-1">Upload CV (PDF, DOCX, TXT)</label>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={e => { const f = e.target.files?.[0]; if (f) uploadCvFile(f); e.target.value = '' }}
                  className="block text-sm text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-gray-700 file:text-white file:text-sm hover:file:bg-gray-600 cursor-pointer"
                />
              </div>
            </div>
            {pdfLoading && <p className="text-sm text-gray-400">Extracting text...</p>}
            {pdfError && <p className="text-sm text-red-400">{pdfError}</p>}
            <textarea value={cvText} onChange={e => setCvText(e.target.value)} rows={18}
              placeholder="Or paste your CV text here..."
              className="w-full bg-gray-900 text-white p-4 rounded-xl border border-gray-700 text-sm resize-none focus:outline-none focus:border-green-500" />
            <button onClick={saveCv} disabled={saving} className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-lg text-sm font-medium">Save CV</button>
          </div>
        )}

        {/* Filters tab */}
        {activeTab === 'filters' && (
          <div className="space-y-4">
            {/* Active filters summary */}
            <div className="text-xs text-gray-500 bg-gray-800/50 px-3 py-2 rounded-lg">
              Location: {locationInput || 'none'}
              {' · '}{skipTitles.length} skip-title{skipTitles.length !== 1 ? 's' : ''}
              {' · '}{keepTitles.length} keep-title{keepTitles.length !== 1 ? 's' : ''}
              {' · '}{skipCompanies.length} excluded {skipCompanies.length !== 1 ? 'companies' : 'company'}
              {' · '}{skipIndustries.length} excluded {skipIndustries.length !== 1 ? 'industries' : 'industry'}
            </div>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Location (leave blank for no filter)</label>
              <input value={locationInput} onChange={e => setLocationInput(e.target.value)} placeholder="e.g. israel"
                className="w-full bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-green-500" />
            </div>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Title denylist</label>
              <TagInput tags={skipTitles} onChange={setSkipTitles} placeholder="add term, press Enter" />
            </div>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Title allowlist</label>
              <TagInput tags={keepTitles} onChange={setKeepTitles} placeholder="add term, press Enter" />
            </div>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Excluded companies</label>
              <TagInput tags={skipCompanies} onChange={setSkipCompanies} placeholder="company name" />
            </div>
            <div>
              <label className="text-sm text-gray-400 block mb-1">Excluded industries</label>
              <TagInput tags={skipIndustries} onChange={setSkipIndustries} placeholder="industry" />
            </div>
            <button onClick={saveFilters} disabled={saving} className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-lg text-sm font-medium">Save filters</button>
          </div>
        )}

        {/* API Key tab */}
        {activeTab === 'apikey' && (
          <div className="space-y-4">
            {/* Status pill */}
            {hasApiKey !== null && (
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${hasApiKey ? 'bg-green-900/30 text-green-400' : 'bg-amber-900/30 text-amber-400'}`}>
                {hasApiKey
                  ? <span>✓ Gemini key configured{apiKeyLast4 ? ` · AIza••••••••${apiKeyLast4}` : ''}</span>
                  : <span>⚠ No API key - scoring is paused</span>
                }
              </div>
            )}
            <p className="text-sm text-gray-400">Replace your Gemini API key. The current key is never shown.</p>
            <p className="text-sm text-green-400">It&apos;s fully free - Google&apos;s Gemini API has a free tier that&apos;s plenty for scoring jobs. <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="underline">Get your free key here</a>.</p>
            <ol className="text-sm text-gray-400 space-y-1 list-decimal list-inside bg-gray-800 p-4 rounded-lg">
              <li>Go to <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="text-green-400 underline">Google AI Studio</a></li>
              <li>Sign in with your Google account</li>
              <li>Click &quot;Get API key&quot; then &quot;Create API key&quot;</li>
              <li>Copy and paste the key below</li>
            </ol>
            <input type="password" value={newKey} onChange={e => setNewKey(e.target.value)} placeholder="AIza..."
              className="w-full bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-green-500" />
            <div className="flex gap-3">
              <button onClick={saveKey} disabled={!newKey || saving} className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-lg text-sm font-medium">Replace key</button>
              <button onClick={testKey} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm">Test key</button>
              <button onClick={deleteKey} className="px-4 py-2 bg-red-900 hover:bg-red-800 rounded-lg text-sm">Delete key</button>
            </div>
            {testResult && <p className="text-sm text-gray-400">{testResult}</p>}
          </div>
        )}

        {/* Account tab */}
        {activeTab === 'account' && (
          <div className="space-y-6">
            {/* Read-only identity block */}
            {userIdentity && (
              <div className="bg-gray-800 rounded-lg p-4 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Name</span>
                  <span>{userIdentity.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Email</span>
                  <span>{userIdentity.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sign-in</span>
                  <span>{userIdentity.provider}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Member since</span>
                  <span>{userIdentity.memberSince}</span>
                </div>
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm text-gray-400 block">New email</label>
              <div className="flex gap-2">
                <input type="email" value={newEmail} onChange={e => setNewEmail(e.target.value)} placeholder="new@email.com"
                  className="flex-1 bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-green-500" />
                <button onClick={saveEmail} disabled={!newEmail} className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-lg text-sm">Save</button>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm text-gray-400 block">New password</label>
              <div className="flex gap-2">
                <input type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} placeholder="new password"
                  className="flex-1 bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-green-500" />
                <button onClick={savePassword} disabled={!newPassword} className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-lg text-sm">Save</button>
              </div>
            </div>
            <button onClick={exportData} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm">Export data (JSON)</button>
            <div className="border-t border-gray-700 pt-4">
              {!deleteConfirm ? (
                <button onClick={() => setDeleteConfirm(true)} className="px-4 py-2 bg-red-900 hover:bg-red-800 rounded-lg text-sm">Delete account</button>
              ) : (
                <div className="space-y-2">
                  <p className="text-sm text-red-400">This will delete all your data permanently. Are you sure?</p>
                  <div className="flex gap-2">
                    <button onClick={deleteAccount} className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm">Yes, delete everything</button>
                    <button onClick={() => setDeleteConfirm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm">Cancel</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
