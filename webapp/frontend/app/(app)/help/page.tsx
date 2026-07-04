import Link from 'next/link'
import { SCORE_BANDS } from '@/lib/scoreBands'

// Derived from the shared SCORE_BANDS so the numbers/labels here can't drift
// from the digest legend and badge tooltips.
const scoreBandsSummary =
  `Score bands: ${SCORE_BANDS.map(b => `${b.range} - ${b.blurb}`).join(' ')} Jobs below 5 are filtered out before they reach your digest.`

const sections = [
  {
    id: 'how-it-works',
    heading: 'How it works',
    content: [
      'CareerWatch monitors job boards at Israeli cyber and fintech companies daily, pulling new postings directly from each company\'s ATS. Once new jobs are collected, the scoring engine compares each posting against your CV and profile using Gemini AI and produces a ranked digest.',
      'The pipeline runs in three stages: company refresh (weekly, to discover new companies and re-verify stale entries), job collection (daily), and scoring (up to twice a week per user). You always see the most recently scored batch in your Digest.',
    ],
  },
  {
    id: 'scoring',
    heading: 'How scoring works',
    content: [
      'Each job is scored from 0 to 10 by Gemini AI based on how well it matches your profile and CV. The model reads the full job description alongside your background, stated preferences, and any dealbreakers you listed.',
      scoreBandsSummary,
      'Scores are relative to your profile, not absolute. A 7 for you means something different than a 7 for someone with a different background. The more specific your profile, the more precise the scores.',
    ],
  },
  {
    id: 'flags',
    heading: 'What the flags mean',
    content: [
      'Flags are short tags attached to each scored job that explain why a score landed where it did. Examples: "team-lead signal" means the posting shows signs of a leadership track; "IC-heavy" means the role looks like an individual-contributor track with limited lead scope; "location mismatch" means the office is outside your stated commute radius.',
      'Positive flags (green) reinforce the score. Caution flags (yellow or gray) explain gaps or trade-offs. Reading the flags takes about three seconds and tells you whether a 7 is worth your time today.',
    ],
  },
  {
    id: 'cadence',
    heading: 'Collection cadence and run limits',
    content: [
      'Jobs are collected daily from each company\'s ATS. Scoring runs up to twice a week per user to keep Gemini API costs manageable. This means your digest may be one or two days behind the very latest postings - but it will never be more than a few days stale.',
      'The collection step is fast and runs on our side; you do not need to trigger it. Scoring is triggered automatically on the backend after collection completes.',
    ],
  },
  {
    id: 'data-privacy',
    heading: 'Data and privacy',
    content: [
      'Your CV and Gemini API key are stored encrypted in Supabase. They are never sent to any third party except Gemini (for scoring only). We do not sell, share, or use your data for any purpose other than running the job-matching pipeline on your behalf.',
      'Your Gemini API key is used solely to make scoring calls - each call sends your CV, your profile, and one job description to Gemini and returns a score. Nothing else.',
      'You can export or permanently delete all your data at any time from Settings > Account. Deletion removes your CV, profile, API key, and all stored job scores.',
    ],
  },
  {
    id: 'improve',
    heading: 'How to improve your results',
    content: [
      'The single highest-leverage change you can make is sharpening your profile. A vague profile produces vague scores. A profile that names your exact role target, lists your dealbreakers, and describes what a 9/10 role looks like for you produces scores you can act on.',
      'Specifically: state the seniority level you want (e.g. "Team Lead, not IC"), name the domains you want to stay in (e.g. "fraud detection or cloud security ML"), and list at least one or two hard dealbreakers (e.g. "no consulting", "no pure infra roles"). The more the model knows what you will say no to, the better it can surface the yeses.',
      'You can update your profile in Settings > Profile. Changes take effect on the next scoring run.',
    ],
  },
]

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-2xl mx-auto px-4 py-10">
        {/* Back link */}
        <Link
          href="/digest"
          className="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-white mb-8 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Digest
        </Link>

        {/* Page title */}
        <h1 className="text-3xl font-bold text-white mb-2">Help & FAQ</h1>
        <p className="text-gray-400 mb-10 text-sm">
          Everything you need to get the most out of CareerWatch.
        </p>

        {/* Quick-jump links */}
        <nav className="mb-10 p-4 bg-gray-900 rounded-lg border border-gray-800">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-3 font-medium">Jump to</p>
          <ul className="space-y-1">
            {sections.map(s => (
              <li key={s.id}>
                <a
                  href={`#${s.id}`}
                  className="text-sm text-gray-400 hover:text-green-400 transition-colors"
                >
                  {s.heading}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        {/* Sections */}
        <div className="space-y-12">
          {sections.map(s => (
            <section key={s.id} id={s.id} className="scroll-mt-20">
              <h2 className="text-xl font-semibold text-green-500 mb-3">{s.heading}</h2>
              <div className="space-y-3">
                {s.content.map((para, i) => (
                  <p key={i} className="text-gray-300 text-sm leading-relaxed">
                    {para}
                  </p>
                ))}
              </div>
            </section>
          ))}
        </div>

        {/* Footer nudge */}
        <div className="mt-16 pt-8 border-t border-gray-800 text-center">
          <p className="text-gray-500 text-sm">
            Still have questions?{' '}
            <a
              href="mailto:omer.hedvat@gmail.com"
              className="text-green-500 hover:text-green-400 transition-colors"
            >
              Get in touch
            </a>
            .
          </p>
        </div>
      </div>
    </div>
  )
}
