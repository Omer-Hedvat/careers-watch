'use client'

import Link from 'next/link'
import { useEffect, useRef, useState } from 'react'
import { JobCard, type Job } from '@/app/components/JobCard'

const FAQ_ITEMS = [
  {
    q: 'How often are jobs updated?',
    a: 'Jobs are pulled from each company\'s ATS once per day. New roles appear in your next digest run.',
  },
  {
    q: 'Which companies are tracked?',
    a: 'Over 100 Israeli cyber, fraud and fintech companies - spanning VC portfolio companies from YL Ventures, Team8, Glilot, Cyberstarts and others, plus large established players like Palo Alto Networks, CrowdStrike, and Wiz. Coverage is Israel-focused; global roles at these companies may appear but are not the primary target.',
  },
  {
    q: 'Is it really free?',
    a: 'Yes. CareerWatch itself is free and open source. You bring your own Google Gemini API key, which has a generous free tier - most users will never hit the quota limit.',
  },
  {
    q: 'Do you store my CV or API key?',
    a: 'Your CV and API key are stored only in your account on the database (encrypted at rest). They are never logged, never used to train any model, and are not shared with third parties.',
  },
  {
    q: 'Can I use it if I\'m not a data scientist?',
    a: 'The scoring rubric and company list are tuned for ML engineers, data scientists, and security engineers in Israel. If you are in a different role or geography, the scores will be less accurate - but you can still use it and read the raw digest.',
  },
  {
    q: 'What\'s the catch?',
    a: 'None, really. It is an open-source side project built for personal use and shared publicly. You bring your own Gemini key, so you bear the compute cost proportionally. There is no business model, no ads, no upsell.',
  },
]

// Static sample fed to the real JobCard so the landing preview can never
// drift from the digest's actual card. The far-future scored_at is a fixed
// constant chosen so timeAgo() deterministically renders "just now" on both
// the prerender and the client - a past date would drift as real time
// advances and cause a hydration mismatch.
const SAMPLE_JOB: Job = {
  id: 'sample-preview',
  company: 'Cybereason',
  title: 'Lead Data Scientist - Threat Detection',
  location: 'Tel Aviv, Israel',
  score: 8,
  reasoning: 'Strong match - fraud domain, team lead scope, Israel location. Minor gap: role leans endpoint telemetry rather than pure fintech fraud.',
  flags: ['tier1-vc', 'lead-path-implied', 'fraud-domain'],
  scored_at: '2099-01-01T00:00:00Z',
  applied: false,
  apply_url: '/auth',
}

// Fade/slide a section's content in the first time it scrolls into view.
// Reduced-motion users (and environments without IntersectionObserver) get
// an instant, static render.
function Reveal({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    if (
      typeof IntersectionObserver === 'undefined' ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      setVisible(true)
      return
    }
    const obs = new IntersectionObserver(
      entries => {
        if (entries[0]?.isIntersecting) {
          setVisible(true)
          obs.disconnect()
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  return (
    <div
      ref={ref}
      style={{ transitionDelay: `${delay}ms` }}
      className={`${className} transition-[opacity,transform] duration-700 ease-out motion-reduce:transition-none ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'
      }`}
    >
      {children}
    </div>
  )
}

function FaqAccordion() {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  return (
    <div className="divide-y divide-border border border-border rounded-xl overflow-hidden bg-background shadow-lg">
      {FAQ_ITEMS.map((item, i) => {
        const open = openIndex === i
        return (
          <div key={i}>
            <button
              className="w-full text-left px-6 py-5 flex justify-between items-center gap-4 hover:bg-surface transition-colors"
              onClick={() => setOpenIndex(open ? null : i)}
              aria-expanded={open}
            >
              <span className={`font-medium transition-colors ${open ? 'text-foreground' : 'text-gray-200'}`}>{item.q}</span>
              <span
                aria-hidden="true"
                className={`ml-auto flex-shrink-0 text-muted text-xl leading-none select-none transition-transform duration-300 ease-out motion-reduce:transition-none ${
                  open ? 'rotate-45' : ''
                }`}
              >
                +
              </span>
            </button>
            {/* grid-rows 0fr -> 1fr gives a smooth height animation without
                measuring content; motion-reduce collapses it to an instant
                toggle. */}
            <div
              className={`grid transition-[grid-template-rows,opacity] duration-300 ease-out motion-reduce:transition-none ${
                open ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
              }`}
            >
              <div className="overflow-hidden">
                <div className="px-6 pb-5 text-muted text-sm leading-relaxed">
                  {item.a}
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Hero mount + job-card mount animations, both gated behind
          prefers-reduced-motion: no-preference. cwCardIn matches the digest
          page's definition so the shared JobCard animates identically here. */}
      <style>{`
        @keyframes cwCardIn {
          from { opacity: 0; transform: translateY(6px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes cwRise {
          from { opacity: 0; transform: translateY(14px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @media (prefers-reduced-motion: no-preference) {
          .cw-card-in { animation: cwCardIn 0.3s ease-out backwards; }
          .cw-rise { animation: cwRise 0.7s cubic-bezier(0.22, 1, 0.36, 1) backwards; }
        }
      `}</style>

      {/* Hero */}
      <main className="relative flex-1 flex flex-col items-center justify-center px-4 text-center py-24 sm:py-32 overflow-hidden">
        {/* Ambient accent glow + hairline base border, purely decorative */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-[-14rem] -translate-x-1/2 w-[52rem] h-[36rem] rounded-full bg-accent/10 blur-3xl" />
          <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-border-subtle to-transparent" />
        </div>
        <h1 className="cw-rise relative text-5xl sm:text-6xl font-bold mb-5 tracking-tight bg-gradient-to-b from-white to-gray-400 bg-clip-text text-transparent">
          CareerWatch
        </h1>
        <p className="cw-rise relative text-xl sm:text-2xl text-gray-300 mb-3 max-w-xl leading-snug" style={{ animationDelay: '80ms' }}>
          Find the right job without the noise. AI-powered job matching for tech professionals in Israel.
        </p>
        <p className="cw-rise relative text-base text-muted mb-10 max-w-xl" style={{ animationDelay: '160ms' }}>
          Tracks 100+ Israeli cyber, fraud and fintech companies and scores every open role against your profile.
        </p>
        <div className="cw-rise relative flex gap-4 flex-wrap justify-center" style={{ animationDelay: '240ms' }}>
          <Link
            href="/auth"
            className="px-6 py-3 bg-accent hover:bg-accent-hover text-accent-foreground rounded-lg font-semibold shadow-lg shadow-accent/20 hover:shadow-accent/30 transition-[background-color,box-shadow,transform] motion-safe:hover:-translate-y-0.5"
          >
            Get started free
          </Link>
          <a
            href="https://github.com/omerhedvat/careers-watch"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 bg-surface-raised hover:bg-gray-700 border border-border-subtle rounded-lg font-semibold transition-[background-color,transform] motion-safe:hover:-translate-y-0.5"
          >
            View on GitHub
          </a>
        </div>
      </main>

      {/* How it works */}
      <section className="py-20 sm:py-24 px-4 bg-surface border-y border-border">
        <div className="max-w-4xl mx-auto">
          <Reveal>
            <h2 className="text-3xl font-bold text-center tracking-tight mb-14">How it works</h2>
          </Reveal>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-8">
            {[
              {
                n: '1',
                title: 'Set up your profile',
                body: 'Describe your background, target roles, and deal-breakers with AI assistance.',
              },
              {
                n: '2',
                title: 'We scrape the market',
                body: 'CareerWatch pulls open positions from 100+ Israeli cyber and fintech companies daily.',
              },
              {
                n: '3',
                title: 'You get a ranked digest',
                body: 'Every job scored 0-10 against your profile. You only read what matters.',
              },
            ].map((step, i) => (
              <Reveal key={step.n} delay={i * 120}>
                <div className="flex flex-col items-center text-center">
                  <div className="w-11 h-11 rounded-full bg-accent flex items-center justify-center font-bold text-lg mb-5 shadow-lg shadow-accent/25 ring-1 ring-white/15">
                    {step.n}
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{step.title}</h3>
                  <p className="text-muted text-sm leading-relaxed max-w-[17rem]">{step.body}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Bring your own key */}
      <section className="py-16 sm:py-20 px-4 bg-background">
        <Reveal className="max-w-2xl mx-auto">
          <div className="text-center bg-surface border border-border rounded-2xl px-6 py-10 sm:px-10 shadow-lg">
            <h2 className="text-2xl font-bold tracking-tight mb-4">Bring your own free AI key</h2>
            <p className="text-muted text-sm leading-relaxed mb-3">
              Scoring runs on Google Gemini - a model with a free tier generous enough that most users never hit the limit.
              During onboarding you will paste your own API key. That key is stored in your account and used only to run scoring on your behalf.
            </p>
            <p className="text-muted text-sm leading-relaxed">
              Your CV, your key, your quota. Your data never trains a model.
            </p>
            <div className="mt-6">
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noopener noreferrer"
                className="text-green-500 hover:text-green-400 text-sm underline underline-offset-2 transition-colors"
              >
                Get a free Gemini API key at Google AI Studio
              </a>
            </div>
          </div>
        </Reveal>
      </section>

      {/* Digest preview - renders the real JobCard with static sample data,
          so the preview and the digest can never drift apart. */}
      <section className="py-20 sm:py-24 px-4 bg-surface border-y border-border">
        <div className="max-w-2xl mx-auto">
          <Reveal>
            <h2 className="text-3xl font-bold text-center tracking-tight mb-4">What your digest looks like</h2>
            <p className="text-muted text-center text-sm mb-10">Example scored job card - your real digest is personalised to your profile.</p>
          </Reveal>
          <Reveal delay={120}>
            <div className="rounded-2xl border border-border bg-background shadow-2xl overflow-hidden">
              {/* Decorative app-window chrome */}
              <div aria-hidden="true" className="flex items-center gap-1.5 px-4 py-3 border-b border-border bg-surface/60">
                <span className="w-2.5 h-2.5 rounded-full bg-surface-raised" />
                <span className="w-2.5 h-2.5 rounded-full bg-surface-raised" />
                <span className="w-2.5 h-2.5 rounded-full bg-surface-raised" />
              </div>
              <div className="p-4 sm:p-6">
                <JobCard job={SAMPLE_JOB} onToggleApplied={() => {}} currentProfileVersion={1} />
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Who it's for */}
      <section className="py-16 sm:py-20 px-4 bg-background">
        <Reveal className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold tracking-tight mb-6">Who it is for</h2>
          <p className="text-muted text-sm leading-relaxed mb-4">
            CareerWatch is built for senior technical job seekers in Israel - data scientists, ML engineers, applied researchers, and security/fraud engineers who want signal without noise.
          </p>
          <p className="text-muted text-sm leading-relaxed">
            The company list and scoring rubric are tuned for the Israeli cyber, fraud and fintech ecosystem.
            If you are based outside Israel or looking for roles in unrelated domains, you can still use it - but coverage and score accuracy will be lower.
            Non-Israel company coverage is out of scope for now.
          </p>
        </Reveal>
      </section>

      {/* FAQ */}
      <section className="py-20 sm:py-24 px-4 bg-surface border-t border-border">
        <div className="max-w-2xl mx-auto">
          <Reveal>
            <h2 className="text-3xl font-bold text-center tracking-tight mb-10">Frequently asked questions</h2>
          </Reveal>
          <Reveal delay={120}>
            <FaqAccordion />
          </Reveal>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border bg-background text-center text-subtle text-sm">
        CareerWatch &middot; Built by Omer Hedvat &middot;{' '}
        <a href="https://github.com/omerhedvat/careers-watch" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">
          GitHub
        </a>
      </footer>
    </div>
  )
}
