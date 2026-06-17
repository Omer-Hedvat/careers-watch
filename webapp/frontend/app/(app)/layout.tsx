import Nav from '@/app/components/Nav'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Nav />
      <main>{children}</main>
    </div>
  )
}
