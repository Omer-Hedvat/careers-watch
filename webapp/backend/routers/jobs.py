from fastapi import APIRouter, HTTPException, Header
from pathlib import Path
import json
import os
from db.supabase_client import supabase

router = APIRouter(prefix="/jobs", tags=["jobs"])

_companies_env = os.environ.get("COMPANIES_PATH")
COMPANIES_PATH = Path(_companies_env) if _companies_env else Path(__file__).parent.parent.parent.parent / "companies.json"

_jobs_env = os.environ.get("NEW_JOBS_PATH")
NEW_JOBS_PATH = Path(_jobs_env) if _jobs_env else Path(__file__).parent.parent.parent.parent / "new_jobs.json"


def _get_user(authorization: str) -> str:
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return resp.user.id


@router.get("/companies")
def list_companies(authorization: str = Header(...)):
    _get_user(authorization)
    if not COMPANIES_PATH.exists():
        return []
    companies = json.loads(COMPANIES_PATH.read_text(encoding="utf-8"))
    result = []
    for c in sorted(companies, key=lambda x: x.get("name", "").lower()):
        result.append({
            "name": c.get("name", ""),
            "category": c.get("category", ""),
            "ats": c.get("ats", ""),
            "careers_url": c.get("careers_url", ""),
            "last_verified_at": c.get("last_verified_at"),
            "consecutive_failures": c.get("consecutive_failures", 0),
        })
    return result


@router.get("/positions")
def list_positions(authorization: str = Header(...)):
    _get_user(authorization)
    if not NEW_JOBS_PATH.exists():
        return []
    jobs = json.loads(NEW_JOBS_PATH.read_text(encoding="utf-8"))
    result = sorted(
        [
            {
                "company": j.get("company", ""),
                "title": j.get("title", ""),
                "location": j.get("location", ""),
                "apply_url": j.get("apply_url", ""),
            }
            for j in jobs
        ],
        key=lambda j: (j["company"].lower(), j["title"].lower()),
    )
    return result


@router.get("/")
def list_jobs(authorization: str = Header(...)):
    user_id = _get_user(authorization)
    rows = (
        supabase.table("scored_jobs")
        .select("*")
        .eq("user_id", user_id)
        .order("score", desc=True)
        .order("scored_at", desc=True)
        .execute()
        .data
    )
    return rows


@router.post("/{job_id}/applied")
def toggle_applied(job_id: str, authorization: str = Header(...)):
    user_id = _get_user(authorization)
    row = (
        supabase.table("scored_jobs")
        .select("applied")
        .eq("id", job_id)
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
        .data
    )
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    new_val = not row["applied"]
    supabase.table("scored_jobs").update({"applied": new_val}).eq("id", job_id).execute()
    return {"applied": new_val}
