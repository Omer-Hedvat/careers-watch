'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '@/lib/supabaseClient'

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

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="bg-gray-900 rounded-xl p-8 w-full max-w-md text-center">
          <div className="text-4xl mb-4">✅</div>
          <h1 className="text-2xl font-bold text-white mb-3">Password updated</h1>
          <p className="text-gray-400 text-sm mb-6">
            Your password has been set. Redirecting you to sign in...
          </p>
          <Link href="/auth" className="text-green-500 hover:text-green-400 text-sm underline">
            Sign in now
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="bg-gray-900 rounded-xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-white mb-2">Set new password</h1>
        <p className="text-gray-400 text-sm mb-6">
          Choose a new password for your account.
        </p>

        <div className="space-y-4">
          <div>
            <input
              type="password"
              placeholder="New password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-green-500"
            />
            <p className="text-gray-500 text-xs mt-1 ml-1">At least 6 characters</p>
          </div>
          <input
            type="password"
            placeholder="Confirm new password"
            value={confirm}
            onChange={e => setConfirm(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-green-500"
          />

          {error && (
            <div className="bg-red-950 border border-red-800 rounded-lg px-3 py-2">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <button
            onClick={setNewPassword}
            disabled={loading}
            className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Set password'}
          </button>

          <div className="text-center">
            <Link href="/auth" className="text-gray-400 hover:text-white text-sm">
              Back to log in
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
