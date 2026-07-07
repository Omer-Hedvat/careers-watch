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
  const buf = await file.arrayBuffer()
  const bytes = new Uint8Array(buf)
  let binary = ''
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i])
  const b64 = btoa(binary)
  const res = await fetch(`${apiUrl}/user/parse-cv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ pdf_b64: b64, mime_type: file.type || '', extension: extensionOf(file.name) }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail ?? 'Extraction failed')
  return data.text
}
