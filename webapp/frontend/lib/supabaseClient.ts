import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";

// Cookie-based client (PKCE flow) so the browser session is shared with the
// middleware and the /auth/callback route handler, which also use auth-helpers
// cookie storage. A plain createClient() uses localStorage + implicit flow,
// which the server-side middleware cannot read - that mismatch bounced every
// protected page back to /auth and broke the OAuth redirect.
export const supabase = createClientComponentClient();
