import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req, res })
  const { data: { session } } = await supabase.auth.getSession()

  const protectedPaths = ['/digest', '/onboarding', '/settings', '/companies', '/positions', '/gaps', '/help']
  const isProtected = protectedPaths.some(p => req.nextUrl.pathname.startsWith(p))

  if (isProtected && !session) {
    return NextResponse.redirect(new URL('/auth', req.url))
  }
  return res
}

export const config = {
  matcher: [
    '/digest/:path*',
    '/onboarding/:path*',
    '/settings/:path*',
    '/companies/:path*',
    '/positions/:path*',
    '/gaps/:path*',
    '/help/:path*',
  ],
}
