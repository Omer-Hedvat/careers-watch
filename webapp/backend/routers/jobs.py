from fastapi import APIRouter, HTTPException, Header
from db.supabase_client import supabase

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_user(authorization: str) -> str:
    token = authorization.removeprefix("Bearer ")
    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return resp.user.id


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
