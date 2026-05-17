# Spec: Fix Viola Getro Duplicate Jobs

## Status
`wrapped`

## Problem
The Viola VC adapter registers ~60 portfolio companies in `companies.json`, each with `ats: getro` and `ats_params: {board_host: careers.viola-group.com}`. The Getro puller is called once per company entry, fetching the same ~20 board-level jobs every time. This produces ~1,200 near-identical jobs in `new_jobs.json`, all sent to Gemini even though only 20 unique `apply_url` values exist.

See `bugs_to_fix/BUG_VIOLA_GETRO_DUPES.md` for reproduction steps.

## Fix

Deduplicate `all_jobs` by `apply_url` in `collect_jobs.py` after the main loop, before writing `new_jobs.json`.

- Jobs with empty `apply_url` are **not** deduplicated (keep all).
- On collision, keep the first occurrence.
- Print a summary line: `Dedup: {before} → {after} jobs ({dropped} duplicates removed)`.

### Files to change

- `collect_jobs.py` — add dedup step after the collection loop

### No changes needed

- `ats/getro.py` — puller is correct; the duplication is structural (same board, many companies)
- `vcs/viola.py` — adapter is correct
- `companies.json` — do not remove Viola entries; the dedup handles it at collection time

## Implementation

In `collect_jobs.py`, after `save_companies(companies)` and before writing `new_jobs.json`:

```python
# Deduplicate by apply_url (Getro boards return the same jobs per portfolio company)
before = len(all_jobs)
seen_urls: set[str] = set()
deduped = []
for job in all_jobs:
    url = (job.get("apply_url") or "").strip()
    if not url:
        deduped.append(job)
        continue
    if url not in seen_urls:
        seen_urls.add(url)
        deduped.append(job)
all_jobs = deduped
if len(all_jobs) < before:
    print(f"Dedup: {before} → {len(all_jobs)} jobs ({before - len(all_jobs)} duplicates removed)")
```

## Exit gate

```bash
uv run python3 -m pytest tests/ -v
uv run python score.py --dry-run
```

Also run manually and verify the dedup line appears:
```bash
uv run python collect_jobs.py 2>&1 | grep -i dedup
```

## Closes
Bug `BUG_VIOLA_GETRO_DUPES`
