from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import List, Optional
import os
from cryptography.fernet import Fernet
from db.supabase_client import supabase

router = APIRouter(prefix="/user", tags=["user"])

FERNET_KEY = os.environ.get("FERNET_KEY", "")


class SetupRequest(BaseModel):
    profile_md: str
    cv_text: str
    gemini_api_key: str
    filters: dict


@router.post("/setup")
def setup_user(body: SetupRequest, authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = resp.user.id

    f = Fernet(FERNET_KEY.encode())
    encrypted_key = f.encrypt(body.gemini_api_key.encode()).decode()

    supabase.table("users").upsert({
        "id": user_id,
        "profile_md": body.profile_md,
        "cv_text": body.cv_text,
        "gemini_api_key_encrypted": encrypted_key,
    }).execute()

    filters = body.filters
    supabase.table("score_configs").upsert({
        "user_id": user_id,
        "location_terms": filters.get("location_terms", []),
        "skip_title_terms": filters.get("skip_title_terms", []),
        "keep_title_terms": filters.get("keep_title_terms", []),
        "skip_companies": filters.get("skip_companies", []),
        "skip_industries": filters.get("skip_industries", []),
    }, on_conflict="user_id").execute()

    return {"status": "ok"}


@router.get("/me")
def get_me(authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    row = supabase.table("users").select("scoring_runs_this_week,last_week_reset,profile_md,cv_text").eq("id", resp.user.id).maybe_single().execute().data
    return row or {}


class ProfileUpdate(BaseModel):
    profile_md: str

class CvUpdate(BaseModel):
    cv_text: str

class FiltersUpdate(BaseModel):
    location_terms: List[str] = []
    skip_title_terms: List[str] = []
    keep_title_terms: List[str] = []
    skip_companies: List[str] = []
    skip_industries: List[str] = []

class ApiKeyUpdate(BaseModel):
    gemini_api_key: str


@router.patch("/profile")
def update_profile(body: ProfileUpdate, authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    supabase.table("users").update({"profile_md": body.profile_md}).eq("id", resp.user.id).execute()
    return {"status": "ok"}


@router.patch("/cv")
def update_cv(body: CvUpdate, authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    supabase.table("users").update({"cv_text": body.cv_text}).eq("id", resp.user.id).execute()
    return {"status": "ok"}


@router.get("/filters")
def get_filters(authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    row = supabase.table("score_configs").select("*").eq("user_id", resp.user.id).maybe_single().execute().data
    return row or {}


@router.patch("/filters")
def update_filters(body: FiltersUpdate, authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    supabase.table("score_configs").upsert({
        "user_id": resp.user.id,
        **body.model_dump(),
    }, on_conflict="user_id").execute()
    return {"status": "ok"}


@router.patch("/apikey")
def update_apikey(body: ApiKeyUpdate, authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    fernet_key = os.environ.get("FERNET_KEY", "")
    f = Fernet(fernet_key.encode())
    encrypted = f.encrypt(body.gemini_api_key.encode()).decode()
    supabase.table("users").update({"gemini_api_key_encrypted": encrypted}).eq("id", resp.user.id).execute()
    return {"status": "ok"}


@router.post("/test-key")
def test_apikey(authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    row = supabase.table("users").select("gemini_api_key_encrypted").eq("id", resp.user.id).maybe_single().execute().data
    if not row or not row.get("gemini_api_key_encrypted"):
        raise HTTPException(status_code=400, detail="No API key stored")
    fernet_key = os.environ.get("FERNET_KEY", "")
    f = Fernet(fernet_key.encode())
    api_key = f.decrypt(row["gemini_api_key_encrypted"].encode()).decode()
    try:
        import google.genai as genai
        client = genai.Client(api_key=api_key)
        client.models.generate_content(model="gemini-2.0-flash", contents="ping")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/apikey")
def delete_apikey(authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    supabase.table("users").update({"gemini_api_key_encrypted": None}).eq("id", resp.user.id).execute()
    return {"status": "ok"}


@router.get("/export")
def export_data(authorization: str = Header(...)):
    from fastapi.responses import JSONResponse
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    jobs = supabase.table("scored_jobs").select("*").eq("user_id", resp.user.id).execute().data
    return JSONResponse(content=jobs, headers={"Content-Disposition": "attachment; filename=careerwatch_export.json"})


@router.delete("/account")
def delete_account(authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = resp.user.id
    supabase.table("users").delete().eq("id", user_id).execute()
    try:
        supabase.auth.admin.delete_user(user_id)
    except Exception:
        pass
    return {"status": "ok"}


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
            raise HTTPException(status_code=422, detail="Could not extract text - please paste manually")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not extract text - please paste manually")
    return {"text": text}
