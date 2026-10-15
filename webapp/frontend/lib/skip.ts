// Per-user Skip list (hidden_jobs, keyed by apply_url). Callers flip their row
// optimistically and roll back if this returns false.
import { supabase } from '@/lib/supabaseClient'

export async function saveSkip(applyUrl: string, skip: boolean): Promise<boolean> {
  try {
    const { data: { session } } = await supabase.auth.getSession()
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs/skip`, {
      method: skip ? 'POST' : 'DELETE',
      headers: { Authorization: `Bearer ${session?.access_token ?? ''}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ apply_url: applyUrl }),
    })
    return res.ok
  } catch {
    return false
  }
}
