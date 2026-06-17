| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `completed` |
| **Effort** | XS |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/companies/page.tsx`, `webapp/frontend/app/positions/page.tsx`, `webapp/frontend/hooks/useCountUp.ts` (new) |

## Overview

When the Companies or Positions page finishes loading, the count in the heading animates from 0 up to the real number rather than appearing statically. Gives the user a quick sense of scale ("we cover 200+ companies") in a visually engaging way.

## Behaviour

- Animation triggers once, when `loading` transitions from `true` to `false` and the target count is first known.
- Duration: ~800 ms, easing out (fast start, decelerate to final value).
- On Companies page: animates the `(N)` count next to the heading (currently line 86 in `companies/page.tsx`).
- On Positions page: animates the total positions count in the heading (currently `positions.length` part of line 73 in `positions/page.tsx`); the filtered-count portion is NOT animated (it changes on every keystroke so animation there would feel jittery).
- If the count is 0 or loading never completes, no animation runs (display stays as-is).
- Re-filtering (search box) updates the filtered count instantly — no animation on filter changes.
- The hook is a shared `useCountUp(target, duration)` that returns the current display value. Implement via `requestAnimationFrame` — no external library needed.

## Files to Touch

1. `webapp/frontend/hooks/useCountUp.ts` — new hook
2. `webapp/frontend/app/companies/page.tsx` — replace bare `companies.length` with `useCountUp(companies.length)`
3. `webapp/frontend/app/positions/page.tsx` — replace `positions.length` in heading with `useCountUp(positions.length)`

## How to QA

1. Navigate to `/companies` — heading count animates from 0 to the real total over ~800 ms on page load.
2. Navigate to `/positions` — total count animates on load; typing in the search box updates the filtered count instantly (no animation).
3. Hard-refresh both pages — animation re-triggers each time.
4. Resize to mobile — animation still works, no layout shift.
5. In a slow-network simulation (DevTools throttle), count stays at 0 while loading spinner is shown, then animates when data arrives.
