from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
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
