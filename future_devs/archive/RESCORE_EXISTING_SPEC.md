# Spec: Rescore Existing Digest with Updated Profile

## Status
`wrapped`

## Problem
When `profile.md` is updated (scoring rubric, weights, priorities), jobs already in `scored_jobs.json` keep their old scores. There is no way to re-evaluate them without clearing state and re-running the full pipeline.

## Solution

Add `--rescore` flag to `score.py`. When set:

1. Load `scored_jobs.json` for each profile (the accumulated store of relevant jobs).
2. Re-score all jobs in that store using the current `profile.md` and `cv.md` via Gemini batch scoring (same `score_jobs_batch` / `_score_jobs_batched` path as the normal run).
3. Update each job's `score`, `reasoning`, and `flags` fields in-place.
4. Keep `applied`, `scored_at`, and all other metadata unchanged.
5. Regenerate `digest.md`.
6. Do **not** write to `all_scores.jsonl` (rescore is not a new observation).
7. Print a summary: `[{name}] Rescored {n} jobs`.

### Files to change

- `score.py`
  - Add `--rescore` to `argparse`
  - Add `_rescore_profile(profile_dir, args)` helper
  - Call it from `main()` when `args.rescore` is set (instead of the normal scoring path)

### No changes needed

- `matcher/gemini_scorer.py` — existing `score_jobs_batch` is reused as-is
- `profiles/*/scored_jobs.json` — updated in-place by `_rescore_profile`

## Implementation sketch

```python
# In main(), add:
parser.add_argument("--rescore", action="store_true",
                    help="Re-score all jobs already in scored_jobs.json with current profile")

# In main(), after profiles are resolved:
if args.rescore:
    for profile in profiles:
        _rescore_profile(profile, args)
    return
```

```python
def _rescore_profile(profile_dir: Path, args) -> None:
    name = profile_dir.name
    store_path = profile_dir / "scored_jobs.json"
    if not store_path.exists():
        print(f"[{name}] No scored_jobs.json, nothing to rescore.")
        return

    existing = _load_scored_jobs(store_path)
    if not existing:
        print(f"[{name}] scored_jobs.json is empty.")
        return

    # Setup client (same as _score_one_profile)
    env_file = profile_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"[{name}] Error: GEMINI_API_KEY not set.", file=sys.stderr)
        return

    profile_md = (profile_dir / "profile.md").read_text(encoding="utf-8")
    config = _load_profile_config(profile_dir)
    cv_default_path = config.get("cv_default")
    cv_default = _read_cv(Path(cv_default_path)) if cv_default_path else _read_cv(profile_dir / "cv.md")

    from google import genai
    client = genai.Client(api_key=api_key)

    jobs_to_rescore = list(existing.values())
    print(f"[{name}] Rescoring {len(jobs_to_rescore)} jobs...")

    rescored = _score_jobs_batched(jobs_to_rescore, profile_md, cv_default, client, name, all_scores_fp=None)

    # Merge updated scores back into existing
    for job in rescored:
        key = _job_key(job)
        if key in existing:
            existing[key]["score"] = job["score"]
            existing[key]["reasoning"] = job.get("reasoning", "")
            existing[key]["flags"] = job.get("flags", [])

    out_path = profile_dir / "digest.md"
    _save_scored_jobs(store_path, existing)
    _write_digest(existing, out_path)
    print(f"[{name}] Rescored {len(rescored)} jobs | wrote {out_path}")
```

## Notes

- `--rescore` and `--dry-run` are mutually exclusive. If both are passed, `--dry-run` wins (existing behavior).
- Works with `--profile` to target a single profile.
- Does **not** need `new_jobs.json` to exist — reads from `scored_jobs.json` only.

## Exit gate

```bash
uv run python3 -m pytest tests/ -v
uv run python score.py --dry-run
```
