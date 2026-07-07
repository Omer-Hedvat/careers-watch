from fastapi import APIRouter, HTTPException, Header
from pathlib import Path
import json
import os
from typing import List
from pydantic import BaseModel
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
    jobs = json.loads(NEW_JOBS_PATH.read_text(encoding="utf-8")) if NEW_JOBS_PATH.exists() else []
    counts: dict[str, int] = {}
    for j in jobs:
        name = j.get("company", "")
        counts[name] = counts.get(name, 0) + 1
    result = []
    for c in sorted(companies, key=lambda x: x.get("name", "").lower()):
        result.append({
            "name": c.get("name", ""),
            "category": c.get("category", ""),
            "ats": c.get("ats", ""),
            "careers_url": c.get("careers_url", ""),
            "last_verified_at": c.get("last_verified_at"),
            "consecutive_failures": c.get("consecutive_failures", 0),
            "open_positions": counts.get(c.get("name", ""), 0),
        })
    return result


@router.get("/positions")
def list_positions(authorization: str = Header(...)):
    # The Positions page is the SHARED catalog of every open role - one copy for
    # all users - so a brand-new user with no profile or scoring still sees the
    # full market. This deliberately does NOT read the per-user scored_jobs
    # table (that backs the personalized Digest); scores stay on the Digest.
    _get_user(authorization)  # require a signed-in session, but do not scope by user
    # PostgREST returns at most 1000 rows per request; the catalog is ~10k, so
    # page through in 1000-row windows until a short page signals the end.
    PAGE = 1000
    rows: list[dict] = []
    start = 0
    while True:
        chunk = (
            supabase.table("positions")
            .select("company,title,location,apply_url")
            .order("company")
            .order("title")
            .range(start, start + PAGE - 1)
            .execute()
            .data
        )
        rows.extend(chunk)
        if len(chunk) < PAGE:
            break
        start += PAGE
    return [
        {
            "company": r.get("company", ""),
            "title": r.get("title", ""),
            "location": r.get("location", ""),
            "apply_url": r.get("apply_url", ""),
            "score": None,   # catalog is unscored; ranking lives on the Digest
            "status": "open",
        }
        for r in rows
    ]


# Explicit columns: the digest list stays light - full `description` (multi-KB
# per row) is only served by the per-job detail endpoint below.
LIST_COLUMNS = "id,user_id,apply_url,company,title,location,score,reasoning,flags,scored_at,applied,profile_version,first_seen,status,closed_at"


@router.get("/")
def list_jobs(authorization: str = Header(...)):
    user_id = _get_user(authorization)
    rows = (
        supabase.table("scored_jobs")
        .select(LIST_COLUMNS)
        .eq("user_id", user_id)
        .order("score", desc=True)
        .order("scored_at", desc=True)
        .execute()
        .data
    )
    return rows


class FilterPreviewRequest(BaseModel):
    location_terms: List[str] = []
    skip_title_terms: List[str] = []
    keep_title_terms: List[str] = []
    skip_companies: List[str] = []
    skip_industries: List[str] = []


@router.post("/filter-preview")
def filter_preview(body: FilterPreviewRequest, authorization: str = Header(...)):
    _get_user(authorization)
    if not NEW_JOBS_PATH.exists():
        return {"empty": True, "passing": 0, "total": 0}
    jobs = json.loads(NEW_JOBS_PATH.read_text(encoding="utf-8"))
    total = len(jobs)
    passing = 0
    for job in jobs:
        title = job.get("title", "").lower()
        location = job.get("location", "").lower()
        company = job.get("company", "").lower()
        # location filter
        if body.location_terms and not any(t.lower() in location for t in body.location_terms):
            continue
        # skip title filter
        if any(t.lower() in title for t in body.skip_title_terms):
            continue
        # keep title filter
        if body.keep_title_terms and not any(t.lower() in title for t in body.keep_title_terms):
            continue
        # skip company filter
        if any(t.lower() in company for t in body.skip_companies):
            continue
        passing += 1
    return {"passing": passing, "total": total, "empty": False}


# Digest surfaces roles scored at or above this; "suitable" mirrors that set.
SURFACE_THRESHOLD = 5


@router.get("/stats")
def jobs_stats(authorization: str = Header(...)):
    # Declared before /{job_id} so "stats" isn't captured as a job id.
    user_id = _get_user(authorization)
    suitable = (
        supabase.table("scored_jobs")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .gte("score", SURFACE_THRESHOLD)
        .execute()
        .count
    ) or 0
    # collected = the raw market pulled from ATSes before scoring. Prefer the
    # local snapshot; on the deployed backend (where new_jobs.json may be absent)
    # fall back to the shared positions catalog count. null if neither resolves.
    collected: int | None = None
    if NEW_JOBS_PATH.exists():
        try:
            collected = len(json.loads(NEW_JOBS_PATH.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            collected = None
    if collected is None:
        try:
            collected = (
                supabase.table("positions").select("apply_url", count="exact").execute().count
            )
        except Exception:
            collected = None
    return {"suitable": suitable, "collected": collected}


@router.get("/{job_id}")
def get_job(job_id: str, authorization: str = Header(...)):
    user_id = _get_user(authorization)
    row = (
        supabase.table("scored_jobs")
        .select("*")
        .eq("id", job_id)
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
        .data
    )
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    # Rows scored before migration 006 have no stored description - fall back
    # to a request-time match against new_jobs.json by apply_url. Fragile if
    # the file has rotated, so newly scored rows persist it durably instead.
    if not row.get("description") and NEW_JOBS_PATH.exists():
        apply_url = row.get("apply_url", "")
        jobs = json.loads(NEW_JOBS_PATH.read_text(encoding="utf-8"))
        match = next((j for j in jobs if j.get("apply_url", "") == apply_url), None)
        if match:
            row["description"] = match.get("description", "")
    return row


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
