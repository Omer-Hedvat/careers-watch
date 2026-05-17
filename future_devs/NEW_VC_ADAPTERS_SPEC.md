| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `not-started` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `vcs/state_of_mind.py` (new), `vcs/sequoia_israel.py` (new), `vcs/aleph.py` (new), `vcs/lightspeed_israel.py` (new), `vcs/greylock_israel.py` (new), `vcs/insight_israel.py` (new), `refresh_companies.py` |

## Overview

Add six new Israeli VC portfolio adapters so their portfolio companies are auto-discovered, careers-URL-detected, and ATS-identified on each weekly `refresh_companies.py` run. Each new adapter is expected to surface 10-50 companies, widening the job funnel meaningfully.

VCs to add:
1. **State of Mind Ventures** — cyber-focused IL VC
2. **Sequoia Israel** — Sequoia's re-established Israel office (post-2024)
3. **Aleph** — generalist with strong cyber/fintech signal
4. **Lightspeed Israel** — Lightspeed's Israel presence
5. **Greylock** — Israel-adjacent bets (e.g. Cylake)
6. **Insight Partners Israel** — IL-specific portfolio (global Insight already tracked)

Tier assignments for `vc_tier` in `companies.json` (per CLAUDE.md tier guide):
- State of Mind → Tier 1 (cyber-pure)
- Sequoia Israel → Tier 2 (generalist + strong cyber)
- Aleph → Tier 2
- Lightspeed Israel → Tier 2
- Greylock → Tier 2
- Insight Israel → Tier 2

## Behaviour

- Each adapter follows the `vcs/yl_ventures.py` pattern: exports one function `get_portfolio() -> list[{"name": str, "website": str}]`
- Playwright used wherever portfolio page is JS-rendered or lazy-loaded (scroll to bottom + wait for network idle)
- Each adapter has a `__main__` block that prints the result list for easy manual testing
- Register each in `refresh_companies.py`'s VC list alongside the existing adapters
- Each discovered company goes through `ats/detect.py` for careers URL + ATS identification on first encounter
- `vc_tier` set per the tier table above

## Files to Touch

- `vcs/state_of_mind.py` — new
- `vcs/sequoia_israel.py` — new
- `vcs/aleph.py` — new
- `vcs/lightspeed_israel.py` — new
- `vcs/greylock_israel.py` — new
- `vcs/insight_israel.py` — new
- `refresh_companies.py` — register each adapter in the VC list

## How to QA

1. `uv run vcs/<name>.py` for each new adapter prints ≥5 `{name, website}` dicts with no exceptions.
2. `uv run python refresh_companies.py` runs to completion with no crashes; output shows each new VC's companies being processed.
3. `companies.json` gains ≥20 new entries with `source_vc` set to the new VC name.
4. `uv run python collect_jobs.py` runs to completion; at least some of the new companies contribute jobs to `new_jobs.json`.
5. `uv run python -m pytest tests/ -v` passes.
