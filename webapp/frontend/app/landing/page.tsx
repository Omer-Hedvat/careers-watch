import Link from 'next/link'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center py-20">
        <h1 className="text-5xl font-bold mb-4 tracking-tight">CareerWatch</h1>
        <p className="text-xl text-gray-400 mb-8 max-w-xl">
          Find the right job without the noise. AI-powered job matching for tech professionals in Israel.
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

      {/* Trust line */}
      <section className="py-12 px-4 text-center">
        <p className="text-gray-500 text-sm">
          Built with your own AI key - your data never trains a model.
        </p>
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
