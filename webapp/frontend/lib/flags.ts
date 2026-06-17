// Shared flag glossary. The scorer (matcher/gemini_scorer.py) tags each job
// with short slugs; this maps the canonical set to human-readable labels and
// definitions so the digest and any future detail view stay in sync. Keep this
// the single source of truth - do not duplicate the map elsewhere.

export type FlagInfo = {
  label: string
  definition?: string
}

export const FLAG_GLOSSARY: Record<string, Required<FlagInfo>> = {
  'tier1-vc': {
    label: 'Top-tier cyber VC',
    definition: 'Backed by a top-tier cyber VC',
  },
  'location-unclear': {
    label: 'Location unclear',
    definition: 'Location not stated in the posting',
  },
  'dealbreaker-location': {
    label: 'Out of commute range',
    definition: 'Location is outside the commute radius',
  },
  'lead-path-implied': {
    label: 'Lead path implied',
    definition: 'Posting implies a path to a lead role',
  },
  'management-gap': {
    label: 'Management gap',
    definition: 'Requires more people-management than the profile shows',
  },
  'wrong-domain': {
    label: 'Wrong domain',
    definition: 'Domain is outside fraud/cyber/security focus',
  },
  'title-laundering': {
    label: 'Title mismatch',
    definition: 'Title oversells the actual scope of the role',
  },
  'llm-not-security': {
    label: 'LLM, not security',
    definition: 'LLM/GenAI role without a security or fraud focus',
  },
  'scorer-error': {
    label: 'Scoring error',
    definition: 'The scorer failed on this job; treat with caution',
  },
}

// Prettify an unknown slug: split on '-', Title Case each word.
function prettify(slug: string): string {
  return slug
    .split('-')
    .filter(Boolean)
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

// Return the known {label, definition} for a slug, or a fallback with a
// prettified label and no definition for unknown slugs.
export function flagInfo(slug: string): FlagInfo {
  return FLAG_GLOSSARY[slug] ?? { label: prettify(slug), definition: undefined }
}
