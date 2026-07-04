| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | WEBAPP_PDF_CV_UPLOAD ✅ |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/onboarding/page.tsx`, `webapp/frontend/app/settings/page.tsx`, `webapp/backend/routers/user.py`, `webapp/backend/pyproject.toml` |

## Overview

The CV upload currently accepts only PDF files. Many users have their CV as a `.docx` Word document and must convert it or paste text manually. This extends the upload to also accept `.docx` (and `.doc`) files, extracting text server-side via `python-docx`.

Plain text (`.txt`) is included as a trivial addition: no extraction library needed, just decode UTF-8.

## Behaviour

- Accepted formats: `.pdf`, `.docx`, `.doc`, `.txt`
- Frontend `accept` attribute updated to `.pdf,.docx,.doc,.txt`
- Frontend type-guard updated to allow `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/msword`, `text/plain`
- Settings page validation (`uploadCvPdf` function) updated to match — and renamed to `uploadCvFile`
- Backend `POST /user/parse-cv` receives the file as base64 + a `mime_type` field so it can dispatch to the right parser:
  - `application/pdf` → `pypdf` (existing)
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document` / `application/msword` → `python-docx`
  - `text/plain` → UTF-8 decode of bytes
- Error message updated: "Could not extract text — please paste manually"
- Encrypted/unsupported DOC binaries (old `.doc` that `python-docx` can't parse) return the same 422 error

## Files to Touch

- `webapp/frontend/app/onboarding/page.tsx` — update `accept`, pass `mime_type` in POST body, update UI label to "Upload CV (PDF, DOCX, TXT)"
- `webapp/frontend/app/settings/page.tsx` — same changes; rename `uploadCvPdf` → `uploadCvFile`, remove hardcoded `application/pdf` guard
- `webapp/backend/routers/user.py` — update `parse_cv` to accept `mime_type` + dispatch to correct parser
- `webapp/backend/pyproject.toml` — add `python-docx>=1.1` to dependencies

## Backend endpoint (updated)

```python
@router.post("/parse-cv")
async def parse_cv(request: Request, authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    body = await request.json()
    file_b64 = body.get("pdf_b64", "")  # keep key for backwards compat
    mime_type = body.get("mime_type", "application/pdf")
    import base64, io
    file_bytes = base64.b64decode(file_b64)
    try:
        if mime_type == "application/pdf":
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif mime_type in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"):
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join(p.text for p in doc.paragraphs)
        elif mime_type == "text/plain":
            text = file_bytes.decode("utf-8", errors="replace")
        else:
            raise HTTPException(status_code=422, detail="Unsupported file type")
        if not text.strip():
            raise HTTPException(status_code=422, detail="Could not extract text — please paste manually")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail="Could not extract text — please paste manually")
    return {"text": text}
```

## How to QA

1. Go to `/onboarding` Step 2 — confirm file input label says "PDF, DOCX, TXT" and `accept` allows all three
2. Upload a `.pdf` CV — confirm text extracts correctly
3. Upload a `.docx` CV — confirm text extracts correctly (paragraphs joined with newlines)
4. Upload a `.txt` CV — confirm text populates the textarea as-is
5. Upload an unsupported file (e.g. `.png`) — confirm inline error appears
6. In Settings > CV tab — repeat the same four upload tests
7. Paste text directly without uploading — confirm still works
