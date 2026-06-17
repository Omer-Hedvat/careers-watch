---
model: sonnet
effort: high
---
# /wrap_task

Archive a QA-passed task, commit, and push.

## Usage

```
/wrap_task <slug>
```

## Pre-flight

- Confirm status is `🟢 Completed` or `completed` — refuse if not
- Confirm `/qa_task` was run and passed in this session — if QA was not run, run it now and only proceed on pass

## Steps

### 1. Archive

**Bug:**
- Update row in `bugs_to_fix/BUG_TRACKER.md` → `✅ Wrapped`
- Cut the row and paste into `bugs_to_fix/ARCHIVE.md`
- Update status in `bugs_to_fix/<slug>.md` → `✅ Wrapped`

**Feature:**
- Update row in `ROADMAP.md` → `wrapped`
- Cut and paste row into `ROADMAP_ARCHIVE.md` (under matching phase)
- Move spec: `git mv future_devs/<slug>_SPEC.md future_devs/archive/<slug>_SPEC.md`
- Update Spec Index entry in `ROADMAP.md` to point to `future_devs/archive/<slug>_SPEC.md`

### 2. Unblock downstream

- Find all tasks with `Depends on: <slug>` in ROADMAP.md or BUG_TRACKER.md
- Add `✅` suffix to the dependency reference: `<slug> ✅`

### 3. Update epic rollup (if child of an epic)

- Increment `wrapped` count in the Epic row in `ROADMAP.md`
- If all children are wrapped: mark epic as `wrapped`, move epic row to `ROADMAP_ARCHIVE.md`

### 4. Commit and push

Stage only the files touched by the wrap (tracker, archive, spec):

```bash
git add bugs_to_fix/BUG_TRACKER.md bugs_to_fix/ARCHIVE.md bugs_to_fix/<slug>.md   # bug
# OR
git add ROADMAP.md ROADMAP_ARCHIVE.md future_devs/archive/<slug>_SPEC.md           # feature
```

Commit:
```bash
git commit -m "wrap(<slug>): <one-line description>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

Push:
```bash
git push
```

## Rules

- Never wrap if Tier 1 QA has not passed
- Never delete spec files — always archive
- Always update the Spec Index after moving files
- Never `git add -A` — stage only wrap-related files
- Always push after committing
