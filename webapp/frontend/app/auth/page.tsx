'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabaseClient'

export default function AuthPage() {
  const router = useRouter()
  const [tab, setTab] = useState<'login' | 'signup'>('login')
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
    const { error } = await supabase.auth.signUp({ email, password })
    if (error) { setError(error.message); setLoading(false); return }
    router.push('/onboarding')
  }

  async function signInWithGoogle() {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin + '/auth/callback' },
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="bg-gray-900 rounded-xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-white mb-6">CareerWatch</h1>

        <div className="flex mb-6 border-b border-gray-700">
          {(['login', 'signup'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium capitalize ${
                tab === t
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
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-green-500"
          />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button
            onClick={tab === 'login' ? signInWithEmail : signUpWithEmail}
            disabled={loading}
            className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium disabled:opacity-50"
          >
            {loading ? 'Loading...' : tab === 'login' ? 'Log in' : 'Sign up'}
          </button>
          <button
            onClick={signInWithGoogle}
            className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium"
          >
            Continue with Google
          </button>
        </div>
      </div>
    </div>
  )
}
