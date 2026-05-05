#!/usr/bin/env python3
"""Orchestrator: new_jobs.json + profiles/ → per-profile digest.md via Gemini.

Digest is cumulative: each run merges newly relevant jobs into scored_jobs.json
(deduped by apply_url), then regenerates digest.md sorted newest-first.

Single-profile fallback: if profiles/ has no valid subdirectories, reads
profile.md + cv.md + .env from the repo root and writes to the root.
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from matcher.gemini_scorer import build_prompt, score_job

# Jobs below this score are not persisted in the digest.
RELEVANCE_THRESHOLD = 5


def _discover_profiles(profiles_dir: Path) -> list[Path]:
    if not profiles_dir.is_dir():
        return []
    return sorted(
        d for d in profiles_dir.iterdir()
        if d.is_dir() and (d / "profile.md").exists() and (d / "cv.md").exists()
    )


def _job_key(job: dict) -> str:
    url = (job.get("apply_url") or "").strip()
    if url:
        return url
    return f"{job.get('company', '')}::{job.get('title', '')}".lower()


def _load_scored_jobs(store_path: Path) -> dict:
    """Returns {key: job_dict} for all previously persisted jobs."""
    if not store_path.exists():
        return {}
    with open(store_path, encoding="utf-8") as f:
        jobs = json.load(f)
    return {_job_key(j): j for j in jobs}


def _save_scored_jobs(store_path: Path, jobs_by_key: dict) -> None:
    store_path.write_text(
        json.dumps(list(jobs_by_key.values()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _merge_new_results(existing: dict, new_scored: list[dict], today: str) -> tuple[dict, int]:
    """Add newly relevant jobs not already in the store. Returns (merged, added_count)."""
    merged = dict(existing)
    added = 0
    for job in new_scored:
        if job.get("score", 0) < RELEVANCE_THRESHOLD:
            continue
        key = _job_key(job)
        if key in merged:
            continue
        merged[key] = {
            "company": job.get("company", ""),
            "title": job.get("title", ""),
            "location": job.get("location", ""),
            "apply_url": job.get("apply_url", ""),
            "source_vc": job.get("source_vc", ""),
            "score": job["score"],
            "reasoning": job.get("reasoning", ""),
            "flags": job.get("flags", []),
            "scored_at": today,
        }
        added += 1
    return merged, added


def _write_digest(jobs_by_key: dict, out_path: Path) -> None:
    """Write digest.md grouped by date (newest first), score desc within each date."""
    all_jobs = list(jobs_by_key.values())
    all_jobs.sort(key=lambda j: (j.get("scored_at", ""), j.get("score", 0)), reverse=True)

    # Group by date
    dates: dict[str, list[dict]] = {}
    for job in all_jobs:
        d = job.get("scored_at", "unknown")
        dates.setdefault(d, []).append(job)

    lines = ["# Job Digest\n"]
    for day in sorted(dates.keys(), reverse=True):
        lines.append(f"## {day}\n")
        for job in dates[day]:  # already sorted score desc within date from the sort above
            title = job.get("title", "")
            company = job.get("company", "")
            apply_url = job.get("apply_url", "")
            location = job.get("location", "unknown location")
            score = job.get("score", 0)
            reasoning = job.get("reasoning", "")
            flags = job.get("flags", [])

            title_link = f"[{title}]({apply_url})" if apply_url else title
            flag_str = f" `{'` `'.join(flags)}`" if flags else ""

            lines.append(f"### **{company}** - {title_link}")
            lines.append(f"**Score:** {score}/10 | **Location:** {location}")
            lines.append(f"**Reasoning:** {reasoning}{flag_str}")
            lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def _score_one_profile(profile_dir: Path, jobs: list, args) -> None:
    name = profile_dir.name

    env_file = profile_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"[{name}] Error: GEMINI_API_KEY not set.", file=sys.stderr)
        return

    profile_md = (profile_dir / "profile.md").read_text(encoding="utf-8")
    cv_md = (profile_dir / "cv.md").read_text(encoding="utf-8")

    from google import genai
    client = genai.Client(api_key=api_key)

    scored = []
    for i, job in enumerate(jobs, 1):
        label = f"{job.get('company', '?')} - {job.get('title', '?')}"
        result = score_job(job, profile_md, cv_md, client)
        score = result["score"]
        print(f"[{name}] [{i}/{len(jobs)}] {label}: score={score}")
        scored.append({**job, **result})

    store_path = profile_dir / "scored_jobs.json"
    existing = _load_scored_jobs(store_path)
    merged, added = _merge_new_results(existing, scored, date.today().isoformat())
    _save_scored_jobs(store_path, merged)

    out_path = profile_dir / "digest.md"
    _write_digest(merged, out_path)
    print(f"[{name}] +{added} new positions | total {len(merged)} | wrote {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Score jobs and write per-profile digest.md")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt for first job and exit")
    parser.add_argument("--input", default="new_jobs.json", help="Input jobs JSON file")
    parser.add_argument("--sample", action="store_true", help="Use tests/sample_jobs.json instead")
    parser.add_argument("--profiles-dir", default="profiles", help="Directory containing profile subdirectories")
    parser.add_argument("--profile", help="Run only this profile name (subdirectory under --profiles-dir)")
    args = parser.parse_args()

    input_file = "tests/sample_jobs.json" if args.sample else args.input
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found. Run collect_jobs.py first.", file=sys.stderr)
        sys.exit(1)

    with open(input_file, encoding="utf-8") as f:
        jobs = json.load(f)

    if not jobs:
        print("No jobs to score.")
        return

    profiles_dir = Path(args.profiles_dir)
    profiles = _discover_profiles(profiles_dir)

    if args.profile:
        profiles = [p for p in profiles if p.name == args.profile]
        if not profiles:
            print(f"Error: profile '{args.profile}' not found under {profiles_dir}", file=sys.stderr)
            sys.exit(1)

    if not profiles:
        _run_root_profile(jobs, args)
        return

    if args.dry_run:
        first_profile = profiles[0]
        profile_md = (first_profile / "profile.md").read_text(encoding="utf-8")
        cv_md = (first_profile / "cv.md").read_text(encoding="utf-8")
        print(f"=== DRY RUN - profile: {first_profile.name} - prompt for first job ===\n")
        print(build_prompt(jobs[0], profile_md, cv_md))
        return

    if len(profiles) == 1:
        _score_one_profile(profiles[0], jobs, args)
    else:
        with ThreadPoolExecutor(max_workers=len(profiles)) as pool:
            futures = {pool.submit(_score_one_profile, p, jobs, args): p.name for p in profiles}
            for fut in as_completed(futures):
                exc = fut.exception()
                if exc:
                    print(f"[{futures[fut]}] Error: {exc}", file=sys.stderr)


def _run_root_profile(jobs: list, args) -> None:
    """Single-profile fallback using root profile.md + cv.md + .env."""
    load_dotenv()

    profile_path = Path("profile.md")
    cv_path = Path("cv.md")

    if not profile_path.exists() or not cv_path.exists():
        print("Error: no profiles found and root profile.md/cv.md missing.", file=sys.stderr)
        sys.exit(1)

    profile_md = profile_path.read_text(encoding="utf-8")
    cv_md = cv_path.read_text(encoding="utf-8")

    if args.dry_run:
        print("=== DRY RUN - prompt for first job ===\n")
        print(build_prompt(jobs[0], profile_md, cv_md))
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set in environment.", file=sys.stderr)
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)

    scored = []
    for i, job in enumerate(jobs, 1):
        label = f"{job.get('company', '?')} - {job.get('title', '?')}"
        result = score_job(job, profile_md, cv_md, client)
        score = result["score"]
        print(f"[{i}/{len(jobs)}] {label}: score={score}")
        scored.append({**job, **result})

    store_path = Path("scored_jobs.json")
    existing = _load_scored_jobs(store_path)
    merged, added = _merge_new_results(existing, scored, date.today().isoformat())
    _save_scored_jobs(store_path, merged)

    out_path = Path("digest.md")
    _write_digest(merged, out_path)
    print(f"\n+{added} new positions | total {len(merged)} | wrote {out_path}")


if __name__ == "__main__":
    main()
