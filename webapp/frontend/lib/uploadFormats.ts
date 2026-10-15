// Single source of truth for the file types both upload flows (CV + profile)
// accept. Keep this in sync with the backend parser's extension map in
// webapp/backend/routers/user.py (_DOC_EXTENSIONS / _TEXT_EXTENSIONS).
//
// Supported set: .md, .txt, .pdf, .docx, .doc
//  - .md / .txt        -> read as UTF-8 text in the browser (no backend call)
//  - .pdf / .docx/.doc -> base64 POST to /user/parse-cv, extracted via MarkItDown

export const SUPPORTED_EXTENSIONS = ['.md', '.txt', '.pdf', '.docx', '.doc'] as const

// The value for every <input type="file"> accept= attribute.
export const ACCEPT_ATTR = SUPPORTED_EXTENSIONS.join(',')

// Human-readable list for labels and error messages.
export const SUPPORTED_LABEL = '.md, .txt, .pdf, .docx, .doc'

// Types we can decode as UTF-8 text directly.
const TEXT_EXTENSIONS = ['.md', '.txt']
const TEXT_MIME = ['text/markdown', 'text/x-markdown', 'text/plain']

// Types that need backend extraction.
const DOC_EXTENSIONS = ['.pdf', '.docx', '.doc']
const DOC_MIME = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
]

export const MAX_TEXT_BYTES = 1024 * 1024 // 1 MB for plain text
export const MAX_DOC_BYTES = 10 * 1024 * 1024 // 10 MB for documents

function extensionOf(name: string): string {
  const i = name.lastIndexOf('.')
  return i >= 0 ? name.slice(i).toLowerCase() : ''
}

export type UploadKind = 'text' | 'doc' | null

// Classify by extension first - browsers frequently report an empty or wrong
// MIME type for .md - falling back to MIME only when the extension is unknown.
export function classifyUpload(file: File): UploadKind {
  const ext = extensionOf(file.name)
  if (TEXT_EXTENSIONS.includes(ext)) return 'text'
  if (DOC_EXTENSIONS.includes(ext)) return 'doc'
  if (TEXT_MIME.includes(file.type)) return 'text'
  if (DOC_MIME.includes(file.type)) return 'doc'
  return null
}

// Extract plain text from an uploaded file, shared by every CV/profile upload
// input. Text files are read locally; documents are sent to the backend
// parser. Throws with a user-facing message on unsupported type, oversize, or
// extraction failure.
export async function extractUploadText(
  file: File,
  token: string,
  apiUrl: string,
): Promise<string> {
  const kind = classifyUpload(file)
  if (kind === null) {
    throw new Error(`Unsupported file type. Supported: ${SUPPORTED_LABEL}`)
  }
  if (kind === 'text') {
    if (file.size > MAX_TEXT_BYTES) throw new Error('File must be under 1 MB')
    return await file.text()
  }
  // Document - extract server-side.
  if (file.size > MAX_DOC_BYTES) throw new Error('File must be under 10 MB')
  const b64 = await toBase64(file)
  const res = await fetch(`${apiUrl}/user/parse-cv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ pdf_b64: b64, mime_type: file.type || '', extension: extensionOf(file.name) }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail ?? 'Extraction failed')
  return data.text
}

async function toBase64(file: File): Promise<string> {
  const bytes = new Uint8Array(await file.arrayBuffer())
  let binary = ''
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i])
  return btoa(binary)
}

// The original file kept for Settings' file card (name/size/date only - never a path).
export type StoredFile = { name: string; size?: number; uploaded_at?: string }
export type StoredKind = 'cv' | 'profile'

// Keep the original upload so Settings can show it. Scoring still uses the extracted
// text, so callers treat a failure here as non-fatal.
export async function storeUploadedFile(file: File, kind: StoredKind, token: string, apiUrl: string): Promise<StoredFile> {
  if (file.size > MAX_DOC_BYTES) throw new Error('File must be under 10 MB')
  const res = await fetch(`${apiUrl}/user/file/${kind}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ file_b64: await toBase64(file), name: file.name, mime_type: file.type || '' }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail ?? 'Could not keep the file')
  return data as StoredFile
}

// Open a kept file in a new tab via a short-lived signed link. The tab is opened
// before the await so popup blockers treat it as part of the click.
export async function openStoredFile(kind: StoredKind, token: string, apiUrl: string): Promise<void> {
  const win = window.open('', '_blank')
  if (win) win.opener = null // the file tab serves user content - no handle back to this tab
  try {
    const res = await fetch(`${apiUrl}/user/file/${kind}`, { headers: { Authorization: `Bearer ${token}` } })
    const data = await res.json().catch(() => ({}))
    if (!res.ok || !data.url) throw new Error(data.detail ?? 'Could not open the file')
    if (win) win.location.href = data.url
    else window.location.href = data.url
  } catch (err) {
    win?.close()
    throw err
  }
}

export function formatBytes(n?: number): string {
  if (!n && n !== 0) return ''
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${Math.round(n / 1024)} KB`
  return `${(n / (1024 * 1024)).toFixed(1)} MB`
}
