'use client'

import Link from 'next/link'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-950 py-16 px-4">
      <div className="max-w-2xl mx-auto">
        <Link href="/auth" className="text-gray-400 hover:text-white text-sm flex items-center gap-1 mb-8">
          ← Back
        </Link>

        <h1 className="text-3xl font-bold text-white mb-8">Privacy Policy</h1>

        <div className="space-y-6 text-gray-300 text-sm leading-relaxed">
          <section>
            <h2 className="text-white font-semibold text-base mb-2">What we store</h2>
            <p>
              CareerWatch stores your email address (for authentication), your CV text or file
              (if you upload one), and your Gemini API key (if you provide one). All data is
              stored in Supabase with encryption at rest.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">How we use your data</h2>
            <p>
              Your CV and API key are used only to score job listings on your behalf.
              Your CV is sent to the Gemini API (using your own key) during scoring runs.
              We do not sell, share, or otherwise transfer your data to any third party
              beyond the Gemini API calls you explicitly trigger.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">Data retention</h2>
            <p>
              Your data is retained as long as your account is active. You can delete your
              account at any time from the Settings page, which will permanently remove all
              stored data including your CV and API key.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">Export</h2>
            <p>
              You can export your stored data (CV, settings, scored jobs) at any time from
              the Settings page.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">Cookies and tracking</h2>
            <p>
              CareerWatch uses session cookies only for authentication. We do not use
              analytics trackers or advertising cookies.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">Contact</h2>
            <p>
              Questions about your data? Reach out via the email you used to sign up.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}
