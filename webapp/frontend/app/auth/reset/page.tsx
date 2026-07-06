'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { CheckCircle2 } from 'lucide-react'
import { supabase } from '@/lib/supabaseClient'
import { ThemeToggle } from '@/app/components/ThemeToggle'

function ResetShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen flex items-center justify-center bg-background px-4 py-12 overflow-hidden">
      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="absolute inset-0 cw-grid [mask-image:radial-gradient(ellipse_60%_60%_at_50%_40%,black,transparent)]" />
        <div className="absolute left-1/2 top-[-16rem] -translate-x-1/2 w-[46rem] h-[32rem] rounded-full bg-accent/10 blur-3xl" />
        <div className="absolute inset-0 cw-grain opacity-[0.05]" />
      </div>
      <ThemeToggle className="absolute top-4 right-4 z-10" />
      <div className="relative w-full max-w-md bg-surface border border-border rounded-2xl p-8 shadow-2xl shadow-black/20">
        {children}
      </div>
    </div>
  )
}

export default function ResetPasswordPage() {
  const router = useRouter()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  async function setNewPassword() {
    setError('')
    if (password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    const { error } = await supabase.auth.updateUser({ password })
    if (error) { setError(error.message); setLoading(false); return }
    setLoading(false)
    setDone(true)
    setTimeout(() => router.push('/auth'), 3000)
  }

  const inputClass =
    'w-full px-3.5 py-2.5 bg-surface-raised text-foreground placeholder:text-subtle rounded-lg border border-border focus:outline-none focus:border-accent transition-colors'

  if (done) {
    return (
      <ResetShell>
        <div className="text-center">
          <div className="w-14 h-14 mx-auto mb-5 rounded-xl bg-score-high/10 border border-score-high/25 flex items-center justify-center">
            <CheckCircle2 className="w-6 h-6 text-score-high" aria-hidden="true" />
          </div>
          <h1 className="font-display text-3xl text-foreground mb-3">Password updated</h1>
          <p className="text-muted text-sm mb-6 leading-relaxed">
            Your password has been set. Redirecting you to sign in...
          </p>
          <Link href="/auth" className="text-accent hover:text-accent-hover text-sm underline underline-offset-2 transition-colors">
            Sign in now
          </Link>
        </div>
      </ResetShell>
    )
  }

  return (
    <ResetShell>
      <h1 className="font-display text-3xl text-foreground mb-2">Set new password</h1>
      <p className="text-muted text-sm mb-6">
        Choose a new password for your account.
      </p>

      <div className="space-y-4">
        <div>
          <input
            type="password"
            placeholder="New password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className={inputClass}
          />
          <p className="text-subtle text-xs mt-1 ml-1">At least 6 characters</p>
        </div>
        <input
          type="password"
          placeholder="Confirm new password"
          value={confirm}
          onChange={e => setConfirm(e.target.value)}
          className={inputClass}
        />

        {error && (
          <div className="bg-danger/10 border border-danger/30 rounded-lg px-3 py-2">
            <p className="text-danger text-sm">{error}</p>
          </div>
        )}

        <button
          onClick={setNewPassword}
          disabled={loading}
          className="w-full py-2.5 bg-accent hover:bg-accent-hover text-accent-foreground rounded-lg font-semibold disabled:opacity-50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-surface"
        >
          {loading ? 'Saving...' : 'Set password'}
        </button>

        <div className="text-center">
          <Link href="/auth" className="text-muted hover:text-foreground text-sm transition-colors">
            Back to log in
          </Link>
        </div>
      </div>
    </ResetShell>
  )
}
