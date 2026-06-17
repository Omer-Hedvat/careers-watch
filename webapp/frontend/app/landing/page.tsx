'use client'

import Link from 'next/link'
import { useState } from 'react'

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

function FaqAccordion() {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  return (
    <div className="divide-y divide-gray-800 border border-gray-800 rounded-xl overflow-hidden">
      {FAQ_ITEMS.map((item, i) => (
        <div key={i}>
          <button
            className="w-full text-left px-6 py-5 flex justify-between items-center hover:bg-gray-900 transition-colors"
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
            aria-expanded={openIndex === i}
          >
            <span className="font-medium text-white">{item.q}</span>
            <span className="ml-4 text-gray-400 text-xl leading-none select-none">
              {openIndex === i ? '-' : '+'}
            </span>
          </button>
          {openIndex === i && (
            <div className="px-6 pb-5 text-gray-400 text-sm leading-relaxed">
              {item.a}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center py-20">
        <h1 className="text-5xl font-bold mb-4 tracking-tight">CareerWatch</h1>
        <p className="text-xl text-gray-400 mb-3 max-w-xl">
          Find the right job without the noise. AI-powered job matching for tech professionals in Israel.
        </p>
        <p className="text-base text-gray-500 mb-10 max-w-xl">
          Tracks 100+ Israeli cyber, fraud and fintech companies and scores every open role against your profile.
        </p>
        <div className="flex gap-4 flex-wrap justify-center">
          <Link
            href="/auth"
            className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition-colors"
          >
            Get started free
          </Link>
          <a
            href="https://github.com/omerhedvat/careers-watch"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-semibold transition-colors"
          >
            View on GitHub
          </a>
        </div>
      </main>

      {/* How it works */}
      <section className="py-20 px-4 bg-gray-900">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How it works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
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
            ].map(step => (
              <div key={step.n} className="flex flex-col items-center text-center">
                <div className="w-10 h-10 rounded-full bg-green-600 flex items-center justify-center font-bold text-lg mb-4">
                  {step.n}
                </div>
                <h3 className="font-semibold text-lg mb-2">{step.title}</h3>
                <p className="text-gray-400 text-sm">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Bring your own key */}
      <section className="py-16 px-4 bg-gray-950">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-4">Bring your own free AI key</h2>
          <p className="text-gray-400 text-sm leading-relaxed mb-3">
            Scoring runs on Google Gemini - a model with a free tier generous enough that most users never hit the limit.
            During onboarding you will paste your own API key. That key is stored in your account and used only to run scoring on your behalf.
          </p>
          <p className="text-gray-400 text-sm leading-relaxed">
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
      </section>

      {/* Digest preview */}
      <section className="py-20 px-4 bg-gray-900">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">What your digest looks like</h2>
          <p className="text-gray-400 text-center text-sm mb-10">Example scored job card - your real digest is personalised to your profile.</p>

          <div className="bg-gray-950 border border-gray-800 rounded-xl p-6">
            {/* Score + company row */}
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Cybereason</p>
                <h3 className="text-lg font-semibold text-white">Lead Data Scientist - Threat Detection</h3>
              </div>
              <div className="flex-shrink-0 w-14 h-14 rounded-xl bg-green-600 flex flex-col items-center justify-center">
                <span className="text-xl font-bold leading-none">8</span>
                <span className="text-xs text-green-200 leading-none">/ 10</span>
              </div>
            </div>

            {/* Reasoning */}
            <p className="text-gray-400 text-sm mb-4">
              Strong match - fraud domain, team lead scope, Israel location. Minor gap: role leans endpoint telemetry rather than pure fintech fraud.
            </p>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-5">
              {['fraud', 'team-lead', 'tel-aviv', 'cyber'].map(tag => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-800 text-gray-300 text-xs rounded-md"
                >
                  {tag}
                </span>
              ))}
            </div>

            {/* Action buttons */}
            <div className="flex gap-3">
              <button
                disabled
                className="px-4 py-2 bg-green-600 rounded-lg text-sm font-semibold opacity-80 cursor-default"
              >
                Apply
              </button>
              <button
                disabled
                className="px-4 py-2 bg-gray-800 rounded-lg text-sm font-semibold text-gray-300 opacity-80 cursor-default"
              >
                Mark applied
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Who it's for */}
      <section className="py-16 px-4 bg-gray-950">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-6">Who it is for</h2>
          <p className="text-gray-400 text-sm leading-relaxed mb-4">
            CareerWatch is built for senior technical job seekers in Israel - data scientists, ML engineers, applied researchers, and security/fraud engineers who want signal without noise.
          </p>
          <p className="text-gray-400 text-sm leading-relaxed">
            The company list and scoring rubric are tuned for the Israeli cyber, fraud and fintech ecosystem.
            If you are based outside Israel or looking for roles in unrelated domains, you can still use it - but coverage and score accuracy will be lower.
            Non-Israel company coverage is out of scope for now.
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 px-4 bg-gray-900">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-10">Frequently asked questions</h2>
          <FaqAccordion />
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-800 text-center text-gray-500 text-sm">
        CareerWatch &middot; Built by Omer Hedvat &middot;{' '}
        <a href="https://github.com/omerhedvat/careers-watch" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">
          GitHub
        </a>
      </footer>
    </div>
  )
}
