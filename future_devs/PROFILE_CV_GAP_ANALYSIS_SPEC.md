| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `completed` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/gaps/page.tsx` (new), `webapp/backend/routers/gaps.py` (new), `matcher/gap_analyzer.py` (new), `webapp/backend/main.py`, `webapp/frontend/app/digest/page.tsx` |

## Overview

The matcher scores jobs against the profile, but never tells the user *why* certain roles keep scoring in the 5-6 band or what stands between them and a 9. This feature adds a Gap Analysis page that runs three distinct analyses using Gemini:

1. **Profile vs CV** — what the user says they want (profile.md) vs what their CV actually demonstrates. Surfaces skills, experiences, or positioning gaps the user may not have noticed.
2. **Position vs CV** — for each high-scoring job, which specific requirements in the JD are not clearly evidenced in the CV. Surfaces the concrete "missing lines" for the user to either address in a tailored cover letter or by updating their CV.
3. **Position vs Profile** — which aspects of the job description diverge from the stated target (e.g. a role that looks like a lead role on title but is clearly an IC role from the description).

---

## Behaviour

### Backend: `matcher/gap_analyzer.py`

Three analysis functions, each calling Gemini:

**`analyze_profile_cv_gap(profile_md: str, cv_md: str) -> ProfileCVGap`**

Prompt focus: compare what the profile says the user targets with what the CV actually demonstrates.

Returns a structured result:
```json
{
  "alignment_score": 0-10,
  "strengths": ["list of things CV clearly supports from the profile"],
  "gaps": [
    {
      "area": "e.g. formal people management",
      "profile_says": "targeting Team Lead roles with 2-6 direct reports",
      "cv_shows": "military leadership of 70 personnel but no DS team manager title",
      "severity": "moderate",
      "suggestion": "e.g. add a line about technical mentoring at Skyhawk"
    }
  ],
  "positioning_notes": "one paragraph: how aligned is the CV framing with the profile's stated target?"
}
```

Severity levels: `critical` (a dealbreaker gap — the CV actively contradicts the profile goal), `moderate` (a missing proof point), `minor` (a nice-to-have that is absent).

**`analyze_position_cv_gap(job: dict, cv_md: str) -> PositionCVGap`**

Prompt focus: given one job description and the CV, what does the JD require or prefer that is not clearly evidenced in the CV?

Returns:
```json
{
  "job_id": "...",
  "company": "...",
  "title": "...",
  "match_strength": "strong | partial | weak",
  "gaps": [
    {
      "requirement": "e.g. 3+ years managing a DS team",
      "cv_coverage": "none | partial | implicit",
      "note": "Military leadership exists but not framed as DS team management"
    }
  ],
  "strengths": ["list of JD requirements clearly covered by the CV"]
}
```

Only run this for jobs with score >= 6 (lower scores are not worth tailoring for).

**`analyze_position_profile_gap(job: dict, profile_md: str) -> PositionProfileGap`**

Prompt focus: does this job actually match the profile's stated targets, or does the description diverge from what the title suggests?

Returns:
```json
{
  "job_id": "...",
  "alignment": "strong | partial | mismatch",
  "divergences": [
    {
      "profile_says": "e.g. lead/ownership roles only",
      "jd_says": "e.g. 'you will execute tasks assigned by the lead DS'",
      "impact": "high | medium | low"
    }
  ]
}
```

### Backend: `webapp/backend/routers/gaps.py`

- `GET /api/gaps/profile-cv` — runs `analyze_profile_cv_gap` on the user's stored profile + CV. Cached per user (re-runs only if profile or CV was updated since last run).
- `GET /api/gaps/positions?min_score=6` — runs `analyze_position_cv_gap` + `analyze_position_profile_gap` for each qualifying job. Returns the combined result list sorted by match_strength then score descending.

### Frontend: `webapp/frontend/app/gaps/page.tsx`

Two-section layout:

**Section 1 — Profile vs CV**
- An alignment score badge (0-10).
- "Strengths" list: green checkmarks — what your CV clearly supports.
- "Gaps" list: each gap shows the three fields (what profile says, what CV shows, suggestion) in a card. Critical gaps get a red border; moderate amber; minor grey.
- A "Positioning note" paragraph at the top summarising overall alignment.

**Section 2 — Position gaps (score >= 6)**
- A filterable table of jobs (company, title, score, match_strength).
- Clicking a job expands an inline panel showing:
  - JD requirements covered by the CV (green).
  - JD requirements not covered or partially covered (amber/red), each with the `cv_coverage` and `note` field.
  - Profile divergences if `alignment != strong`.
- A "Copy gap summary" button per job — copies a plain text summary for use in a cover letter or tailoring session.

Navigation: "Gaps" link added to the main nav.

---

## Files to Touch

- `matcher/gap_analyzer.py` — new: three analysis functions
- `webapp/backend/routers/gaps.py` — new: two endpoints
- `webapp/backend/main.py` — register gaps router
- `webapp/frontend/app/gaps/page.tsx` — new page
- `webapp/frontend/app/digest/page.tsx` — add "Gaps" nav link (nav lives here, not in layout.tsx)

## How to QA

1. Navigate to `/gaps` — page renders without error.
2. Section 1 shows an alignment score, at least one strength, and at least one gap (assuming a real profile + CV are stored).
3. Section 2 lists jobs with score >= 6. Each row is expandable.
4. Expanding a job shows covered and uncovered JD requirements.
5. "Copy gap summary" copies readable plain text to clipboard.
6. With no CV stored — friendly empty state shown, not a 500.
7. With no jobs scored above 6 — Section 2 shows "No positions above threshold" empty state.
8. `uv run python3 -m pytest tests/ -v` passes.
9. `uv run python score.py --dry-run` passes.
