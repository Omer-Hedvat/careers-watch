| Field | Value |
|---|---|
| **Phase** | P2 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | Web App v1 |
| **Depends on** | webapp_onboarding (wrapped) |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/onboarding/page.tsx`, `webapp/backend/routers/user.py`, `webapp/backend/pyproject.toml` |

## Overview

Onboarding Step 2 currently only accepts CV as pasted text. Users with a PDF CV have no good path — they'd need to extract text themselves. This adds a file upload option: user picks a PDF, it's sent to the backend for extraction, and the extracted text fills the textarea.

## Behaviour

- Step 2 shows two options: a "Paste text" textarea (existing) and a "Upload PDF" file input (`accept=".pdf"`)
- On file select: read file as base64, POST to `POST /user/parse-cv` with `{ pdf_b64: "..." }`
- Backend extracts text with `pypdf`, returns `{ text: "..." }`
- Extracted text populates the CV textarea — user can review and edit before continuing
- File input and textarea are mutually exclusive in terms of which populates the state, but both are always visible
- Error handling: if extraction fails (encrypted PDF, scanned image), show inline error "Could not extract text — please paste manually"

## Files to Touch

- `webapp/frontend/app/onboarding/page.tsx` — add file input, base64 encode, call `/user/parse-cv`, populate `cvText` state
- `webapp/backend/routers/user.py` — add `POST /user/parse-cv` endpoint using `pypdf`
- `webapp/backend/pyproject.toml` — add `pypdf>=4.0` to dependencies

## Backend endpoint

```python
@router.post("/parse-cv")
async def parse_cv(request: Request, authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    body = await request.json()
    pdf_b64 = body.get("pdf_b64", "")
    import base64, io
    from pypdf import PdfReader
    try:
        pdf_bytes = base64.b64decode(pdf_b64)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if not text.strip():
            raise HTTPException(status_code=422, detail="Could not extract text — please paste manually")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"text": text}
```

## How to QA

1. Go to `/onboarding`, reach Step 2 — confirm both textarea and file input are visible
2. Upload a standard PDF CV — confirm text populates the textarea automatically
3. Upload an image-only PDF — confirm error message appears and textarea remains editable
4. Paste text directly — confirm it still works without touching the file input
5. Continue through onboarding — confirm CV text is saved correctly
