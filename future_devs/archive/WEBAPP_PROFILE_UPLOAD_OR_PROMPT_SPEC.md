| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `wrapped` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/settings/page.tsx`, `webapp/frontend/app/onboarding/page.tsx`, `webapp/backend/routers/user.py` |

## Overview

New users have no profile.md and no obvious way to create one. Two paths should be supported: direct upload (for users who already have a profile file) and an AI-prompt generator (for users starting from scratch, so they can paste the output from any LLM they choose).

---

## What profile.md is

`profile.md` is the scoring rubric and filter intent for the job matcher. It is read alongside `cv.md` by Gemini when scoring every job. The CV is the ground truth of what the user *has done*. The profile is the ground truth of what they *want next and what to skip*.

A well-formed profile.md contains these sections (all required):

| Section | What it should say |
|---|---|
| **Who I am, in one paragraph** | Seniority, specialization, and one distinctive angle (e.g. adversarial ML, fintech fraud). Tells the matcher what kind of DS this person is. |
| **What I'm looking for, in priority order** | 3-5 ranked role types with concrete titles. The matcher boosts roles that match the top priorities. |
| **Location** | City/region, max commute time, stance on hybrid/remote/relocation. Any location that is a hard skip. |
| **Strong fit signals** | Specific keywords, technologies, company types, or team sizes that should raise the score. The matcher boosts jobs that mention these. |
| **Weak fit / skip** | Things that lower the score but are not dealbreakers (e.g. "heavy MLOps as primary role", "pure NLP"). |
| **Dealbreakers** | Hard filters. Any job matching these gets score = 0 and is not surfaced. Location-based dealbreakers go here. |
| **Notes for the matcher** | Edge-case handling instructions (e.g. "treat 'Senior DS at large company' as a lead-level role if the scope is large"). |
| **Scoring rubric** | Explicit score bands: what a 9-10 looks like vs a 7-8 vs a 5-6. Without this the model invents its own scale. |

---

## Behaviour

### Path A — Upload

- Settings page adds a "Profile" section next to the CV section.
- Accepts a Markdown file (.md) up to 1 MB.
- On upload, the file replaces the stored profile in Supabase.
- A "last updated" timestamp is shown.

### Path B — AI prompt generator

A "Generate with AI" button/link opens a modal or dedicated page. The flow has three steps:

**Step 1 — Copy the prompt**

The page shows a ready-to-copy text block. The user copies it with a single click (copy-to-clipboard button). No API call is made; this is static text rendered from a hardcoded template.

**Step 2 — Paste into any LLM**

Instructions shown on screen:
> Open ChatGPT, Claude, Gemini, or any LLM you prefer. Paste this prompt and answer the questions it asks. The LLM will output a ready-to-use `profile.md` file.

**Step 3 — Paste the output back**

A text area labelled "Paste the LLM output here" with a Save button. On save, the text is stored as the user's profile in Supabase. A "last updated" timestamp is shown.

### The hardcoded prompt (render verbatim in the UI)

```
You are helping me create a job-matching profile file. I will answer your questions and you will produce a structured Markdown document called profile.md that a job-scoring AI will use to evaluate job postings for me.

Ask me the following questions one at a time (or ask them all at once and I will answer):

1. What is your current title and how many years of experience do you have?
2. What is your primary specialization — the area where you are stronger than most people at your level?
3. What job titles are you targeting, in priority order? (e.g. "Team Lead DS first, Senior DS second")
4. What domains do you want to work in? (e.g. cyber security, fraud, fintech, healthcare, general SaaS). Which are required vs. preferred?
5. Where are you located and what is your maximum commute time? Are you open to hybrid, fully remote, or relocation?
6. What are your absolute dealbreakers — roles or companies you will not consider no matter how good the title looks?
7. What specific technologies, methodologies, or company stages are a strong signal that a role is right for you?
8. What kinds of roles look good on paper but are actually wrong for you? (e.g. "MLOps-heavy roles", "pure research", "customer-facing")
9. What nuances should the scorer know that are easy to get wrong? (e.g. "I have military leadership but no formal DS manager title — treat it as a partial fit, not a miss")
10. What does a 9-10 role look like for you? What does a 5-6 look like?

After I answer, produce a profile.md with these exact sections:
- # Candidate Profile
- ## Who I am, in one paragraph
- ## What I'm looking for, in priority order
- ## Location
- ## Strong fit signals (boost the score)
- ## Weak fit / skip (drop the score)
- ## Dealbreakers (score = 0, do not surface)
- ## Notes for the matcher
- ## Scoring rubric for the matcher

Write the scoring rubric as explicit score bands: what a 9-10 looks like, what a 7-8 looks like, what a 5-6 looks like, and what 0-2 means. Be specific — reference the role types and signals I described.
```

### Shared rules

- If no profile is on file, onboarding Step 3 (or wherever profile is collected) surfaces both paths.
- Profile is user-scoped in Supabase; changing it triggers a re-score flag (out of scope for this task — that is [[WEBAPP_RESCORE_ON_PROFILE_CHANGE]]).

---

## Files to Touch

- `webapp/frontend/app/settings/page.tsx` — add Profile section (upload + generate prompt button + paste-back text area)
- `webapp/frontend/app/onboarding/page.tsx` — surface both paths if no profile on file
- `webapp/backend/routers/user.py` — add profile upload/save endpoint (store markdown text)

## How to QA

1. Settings page shows a Profile section with "Upload .md" and "Generate with AI" options.
2. Upload a valid .md file — last-updated timestamp updates.
3. Upload a non-.md file — validation error shown.
4. Click "Generate with AI" — modal/page appears with: (a) the full hardcoded prompt in a copy-able block, (b) step-by-step instructions referencing ChatGPT/Claude/Gemini, (c) a text area to paste the result.
5. Copy button copies the full prompt to clipboard.
6. Paste text into the text area and save — profile stored; Settings page reflects new timestamp.
7. No API call is fired during the generate flow (confirm in browser DevTools Network tab).
8. `uv run python3 -m pytest tests/ -v` passes.
9. `uv run python score.py --dry-run` passes.
