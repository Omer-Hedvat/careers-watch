| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `in-progress` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/lib/profileCopy.ts, webapp/supabase/migrations/012_user_files.sql, webapp/backend/routers/user.py, webapp/backend/tests/test_user_files.py, webapp/frontend/lib/uploadFormats.ts, webapp/frontend/app/(app)/settings/page.tsx, webapp/frontend/app/onboarding/page.tsx |

## Overview
Settings - Profile / CV show only the extracted text in a big text box; the uploaded file is
thrown away after parsing. Omer wants to see the file he gave (clickable), not a text dump.
Also, after an idle spell the free-plan backend takes up to a minute to wake, and until then
the tabs look empty - indistinguishable from "nothing saved".

## Behaviour
- Uploaded CV/profile files are kept in a private Supabase Storage bucket `user-files`
  at `<user_id>/<kind><ext>` (one file per kind, replaced on re-upload). Only the backend
  (service role) touches the bucket; the browser gets a 5-minute signed URL to open it.
- `users.cv_file` / `users.profile_file` (jsonb): `{path, name, size, mime, uploaded_at}`.
  `/user/me` returns `{name, size, uploaded_at}` only (never the path). If the migration
  isn't applied the file columns are simply absent - nothing else breaks.
- Scoring is unchanged: it reads the extracted text (cv_text / profile_md).
- Settings: when a file is kept, the tab shows a file card (name, size, date) that opens the
  file, plus "Replace file"; the text box is collapsed behind "View text". Without a kept
  file (older uploads, pasted text) the text box shows as before.
- Profile upload now saves straight away, like CV upload already did.
- Storing the file is best-effort: if it fails, the text is still saved and a message says so.
- While `/user/me` is loading, the tab shows "Waking up the server - this can take up to a
  minute after a quiet spell" instead of empty boxes.
- Delete account also removes the user's stored files. Max file size 10 MB (same as parsing).
- Free plan: Supabase Storage includes 1 GB; a few CVs/profiles are a few MB.
- Profile tab (and onboarding step 1) open with a short human explainer of what the profile
  is and how scoring uses it (copy by Fable), and the copyable AI prompt now has the user
  attach their CV: the assistant infers what the CV answers, asks only the rest, and outputs
  profile.md with the eight exact headings the scorer and the completeness check expect.
  Both texts live in `webapp/frontend/lib/profileCopy.ts`.

## Files to Touch
See Touches.

## How to QA
1. Paste migration 012 in Supabase; it returns "Success".
2. Settings - CV: upload a .docx/.pdf; a file card with the right name and date appears;
   clicking it opens the original file; "View text" shows the extracted text.
3. Reload: the card is still there. Settings - Profile: same with a .md file.
4. Upload again: the card shows the new file; the bucket holds one file per kind.
5. Cold backend (or throttled network): tabs show the waking-up message, not empty boxes.
6. Profile tab starts with the two-paragraph explainer; Generate with AI - Copy puts the new
   prompt (attach your CV, eight headings) on the clipboard.
