'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
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
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="bg-gray-900 rounded-xl p-8 w-full max-w-md text-center">
          <div className="text-4xl mb-4">📬</div>
          <h1 className="text-2xl font-bold text-white mb-3">Check your email</h1>
          <p className="text-gray-400 text-sm mb-6">
            We sent a link to <span className="text-white font-medium">{email}</span>.
            Click it to confirm your account and continue.
          </p>
          <button
            onClick={() => { setView('login'); setError('') }}
            className="text-green-500 hover:text-green-400 text-sm underline"
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
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="bg-gray-900 rounded-xl p-8 w-full max-w-md">
          <Link href="/" className="text-gray-400 hover:text-white text-sm flex items-center gap-1 mb-6">
            ← Back to landing
          </Link>
          <h1 className="text-2xl font-bold text-white mb-2">Reset password</h1>
          <p className="text-gray-400 text-sm mb-6">
            Enter your email and we&apos;ll send you a reset link.
          </p>
          <div className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-green-500"
            />
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <button
              onClick={sendResetEmail}
              disabled={loading}
              className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send reset email'}
            </button>
            <button
              onClick={() => { setView('login'); setError('') }}
              className="w-full py-2 text-gray-400 hover:text-white text-sm"
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
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="bg-gray-900 rounded-xl p-8 w-full max-w-md">
        <Link href="/" className="text-gray-400 hover:text-white text-sm flex items-center gap-1 mb-6">
          ← Back to landing
        </Link>

        <h1 className="text-2xl font-bold text-white mb-6">CareerWatch</h1>

        <div className="flex mb-6 border-b border-gray-700">
          {(['login', 'signup'] as const).map(t => (
            <button
              key={t}
              onClick={() => { setView(t); setError('') }}
              className={`px-4 py-2 text-sm font-medium capitalize ${
                view === t
                  ? 'text-white border-b-2 border-green-500'
                  : 'text-gray-400 hover:text-white'
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
            className="w-full px-3 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-green-500"
          />
          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-green-500"
            />
            {view === 'signup' && (
              <p className="text-gray-500 text-xs mt-1 ml-1">At least 6 characters</p>
            )}
          </div>

          {view === 'login' && (
            <div className="text-right">
              <button
                onClick={() => { setView('forgot'); setError('') }}
                className="text-gray-400 hover:text-green-500 text-sm"
              >
                Forgot password?
              </button>
            </div>
          )}

          {error && (
            <div className="bg-red-950 border border-red-800 rounded-lg px-3 py-2">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <button
            onClick={view === 'login' ? signInWithEmail : signUpWithEmail}
            disabled={loading}
            className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium disabled:opacity-50"
          >
            {loading ? 'Loading...' : view === 'login' ? 'Log in' : 'Sign up'}
          </button>

          <div className="flex items-center gap-3 my-2">
            <div className="flex-1 h-px bg-gray-700" />
            <span className="text-gray-500 text-xs">or</span>
            <div className="flex-1 h-px bg-gray-700" />
          </div>

          <button
            onClick={signInWithGoogle}
            className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium"
          >
            Continue with Google
          </button>

          {view === 'signup' && (
            <p className="text-gray-500 text-xs text-center mt-4">
              By signing up you agree to our{' '}
              <Link href="/terms" className="text-green-500 hover:text-green-400 underline">
                Terms
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="text-green-500 hover:text-green-400 underline">
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
