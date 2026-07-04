'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Mail } from 'lucide-react'
import { supabase } from '@/lib/supabaseClient'

type View = 'login' | 'signup' | 'forgot' | 'check-email'

export default function AuthPage() {
  const router = useRouter()
  const [view, setView] = useState<View>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function signInWithEmail() {
    setLoading(true)
    setError('')
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) { setError(error.message); setLoading(false); return }
    router.push('/digest')
  }

  async function signUpWithEmail() {
    setLoading(true)
    setError('')
    const { data, error } = await supabase.auth.signUp({ email, password })
    if (error) { setError(error.message); setLoading(false); return }
    if (!data.session) {
      // Email confirmation required
      setLoading(false)
      setView('check-email')
      return
    }
    router.push('/onboarding')
  }

  async function sendResetEmail() {
    setLoading(true)
    setError('')
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: window.location.origin + '/auth/reset',
    })
    if (error) { setError(error.message); setLoading(false); return }
    setLoading(false)
    setView('check-email')
  }

  async function signInWithGoogle() {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin + '/auth/callback' },
    })
  }

  // --- Check-email confirmation screen ---
  if (view === 'check-email') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="bg-surface rounded-xl p-8 w-full max-w-md text-center">
          <Mail className="w-10 h-10 mx-auto mb-4 text-accent" aria-hidden="true" />
          <h1 className="text-2xl font-bold text-foreground mb-3">Check your email</h1>
          <p className="text-muted text-sm mb-6">
            We sent a link to <span className="text-foreground font-medium">{email}</span>.
            Click it to confirm your account and continue.
          </p>
          <button
            onClick={() => { setView('login'); setError('') }}
            className="text-accent hover:text-accent-hover text-sm underline transition-colors"
          >
            Back to log in
          </button>
        </div>
      </div>
    )
  }

  // --- Forgot password screen ---
  if (view === 'forgot') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="bg-surface rounded-xl p-8 w-full max-w-md">
          <Link href="/" className="text-muted hover:text-foreground text-sm inline-flex items-center gap-1 mb-6 transition-colors">
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            Back to landing
          </Link>
          <h1 className="text-2xl font-bold text-foreground mb-2">Reset password</h1>
          <p className="text-muted text-sm mb-6">
            Enter your email and we&apos;ll send you a reset link.
          </p>
          <div className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-surface-raised text-foreground rounded-lg border border-subtle focus:outline-none focus:border-accent transition-colors"
            />
            {error && <p className="text-danger text-sm">{error}</p>}
            <button
              onClick={sendResetEmail}
              disabled={loading}
              className="w-full py-2 bg-accent hover:bg-accent-hover text-accent-foreground rounded-lg font-medium disabled:opacity-50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-surface"
            >
              {loading ? 'Sending...' : 'Send reset email'}
            </button>
            <button
              onClick={() => { setView('login'); setError('') }}
              className="w-full py-2 text-muted hover:text-foreground text-sm transition-colors"
            >
              Back to log in
            </button>
          </div>
        </div>
      </div>
    )
  }

  // --- Main login / signup screen ---
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="bg-surface rounded-xl p-8 w-full max-w-md">
        <Link href="/" className="text-muted hover:text-foreground text-sm inline-flex items-center gap-1 mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          Back to landing
        </Link>

        <h1 className="text-2xl font-bold text-foreground mb-6">CareerWatch</h1>

        <div className="flex mb-6 border-b border-subtle">
          {(['login', 'signup'] as const).map(t => (
            <button
              key={t}
              onClick={() => { setView(t); setError('') }}
              className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
                view === t
                  ? 'text-foreground border-b-2 border-accent'
                  : 'text-muted hover:text-foreground'
              }`}
            >
              {t === 'login' ? 'Log in' : 'Sign up'}
            </button>
          ))}
        </div>

        <div className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full px-3 py-2 bg-surface-raised text-foreground rounded-lg border border-subtle focus:outline-none focus:border-accent transition-colors"
          />
          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full px-3 py-2 bg-surface-raised text-foreground rounded-lg border border-subtle focus:outline-none focus:border-accent transition-colors"
            />
            {view === 'signup' && (
              <p className="text-subtle text-xs mt-1 ml-1">At least 6 characters</p>
            )}
          </div>

          {view === 'login' && (
            <div className="text-right">
              <button
                onClick={() => { setView('forgot'); setError('') }}
                className="text-muted hover:text-accent text-sm transition-colors"
              >
                Forgot password?
              </button>
            </div>
          )}

          {error && (
            <div className="bg-red-950 border border-red-800 rounded-lg px-3 py-2">
              <p className="text-danger text-sm">{error}</p>
            </div>
          )}

          <button
            onClick={view === 'login' ? signInWithEmail : signUpWithEmail}
            disabled={loading}
            className="w-full py-2 bg-accent hover:bg-accent-hover text-accent-foreground rounded-lg font-medium disabled:opacity-50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-surface"
          >
            {loading ? 'Loading...' : view === 'login' ? 'Log in' : 'Sign up'}
          </button>

          <div className="flex items-center gap-3 my-2">
            <div className="flex-1 h-px bg-border-subtle" />
            <span className="text-subtle text-xs">or</span>
            <div className="flex-1 h-px bg-border-subtle" />
          </div>

          <button
            onClick={signInWithGoogle}
            className="w-full py-2 bg-surface-raised hover:bg-border-subtle text-foreground rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-surface"
          >
            Continue with Google
          </button>

          {view === 'signup' && (
            <p className="text-subtle text-xs text-center mt-4">
              By signing up you agree to our{' '}
              <Link href="/terms" className="text-accent hover:text-accent-hover underline transition-colors">
                Terms
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="text-accent hover:text-accent-hover underline transition-colors">
                Privacy Policy
              </Link>
              .
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
