| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `not-started` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `tests/` |

## Overview

The test suite currently has 0 test files. `tests/sample_jobs.json` exists but nothing uses it. As the pipeline grows (more ATS pullers, more VC adapters, more scoring logic), regressions become harder to catch manually. This task adds a focused set of unit and integration tests covering the highest-value paths.

## What to test (priority order)

### 1. ATS pullers — output schema

Each puller must return `{title, location, description, apply_url}` per job. Test against the sample payload format, not a live API call.

```python
# tests/test_ats_schema.py
# For each puller: mock the HTTP response, call the puller, assert output schema
```

### 2. Deduplication in collect_jobs.py

`collect_jobs.py` deduplicates by `apply_url`. Test that duplicate URLs in raw puller output produce a single entry in `new_jobs.json`.

### 3. score_config filtering

The pre-Gemini filter logic in `score.py` (title denylist, allowlist, location filter, industry filter). Use `tests/sample_jobs.json` as input. No Gemini call needed — just test that the right jobs reach the pending list.

### 4. Gemini response parsing in gemini_scorer.py

The scorer strips markdown fences and parses JSON. Test the parser against:
- Clean JSON response
- JSON wrapped in ```json ... ``` fences
- Malformed JSON (should not crash)

### 5. refresh_companies.py merge logic

`big_companies.yml` entries must always win over VC-discovered entries with the same name. Test the merge dedup.

## Files to Touch

- `tests/test_ats_schema.py`
- `tests/test_collect_dedup.py`
- `tests/test_score_filters.py`
- `tests/test_gemini_parser.py`
- `tests/test_refresh_merge.py`

## How to QA

```bash
uv run python3 -m pytest tests/ -v
# All tests pass, no API calls made, no files written
```
