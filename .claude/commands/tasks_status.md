---
model: sonnet
effort: high
---
# /tasks_status

Print a read-only dashboard of all active work.

## Usage

```
/tasks_status
```

## Output format

```
## Epics
| Epic | Phase | Status | Rollup |
|---|---|---|---|
| <name> | P<N> | <status> | X wrapped · Y completed · Z in-progress · N not-started |

## 🔴 Blocked
<tasks with unmet Depends on>

## 🟡 In Progress
<bugs + features currently being worked>

## 🟢 Completed (awaiting QA)
<tasks that need /qa_task + /wrap_task>

## 🔵 Open Bugs
| Slug | Title | Severity |
(sorted P0 → P3)

## Not Started (by phase)
| Phase | Feature | Effort | Depends on |
(only actionable = Depends on met)

## Recently Wrapped (last 5)
<from ROADMAP_ARCHIVE.md + bugs_to_fix/ARCHIVE.md>
```

## Data sources

- `ROADMAP.md` — features + epics
- `bugs_to_fix/BUG_TRACKER.md` — active bugs
- `bugs_to_fix/ARCHIVE.md` — recently wrapped bugs
- `ROADMAP_ARCHIVE.md` — recently wrapped features
