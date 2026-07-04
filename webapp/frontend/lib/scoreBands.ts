// Single source of truth for score tiers. The digest legend/popover/badge and
// the help page's scoring explainer all derive from this so copy and colors
// cannot drift. Ordered high to low; the first band whose `min` the score
// meets is the match.
export const SCORE_BANDS = [
  { min: 9, color: 'bg-score-high', range: '9-10', label: 'reach out today', blurb: 'Top fit. A clear match on role, seniority, and domain - worth reaching out today.' },
  { min: 7, color: 'bg-score-mid', range: '7-8', label: 'strong, worth a look', blurb: 'Strong fit with one or two caveats. Worth a look and likely worth applying.' },
  { min: 5, color: 'bg-score-low', range: '5-6', label: 'adjacent', blurb: 'Adjacent. Related but off on role, seniority, or domain - skim before investing time.' },
] as const

export function bandFor(score: number) {
  return SCORE_BANDS.find(b => score >= b.min) ?? SCORE_BANDS[SCORE_BANDS.length - 1]
}
