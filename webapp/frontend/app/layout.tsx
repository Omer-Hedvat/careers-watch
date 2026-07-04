import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "CareerWatch",
  description: "AI-powered job matching for your career search",
  icons: {
    icon: "/favicon.svg",
  },
  openGraph: {
    title: "CareerWatch",
    description: "AI-powered job matching for your career search",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-background text-foreground font-sans antialiased">{children}</body>
    </html>
  );
}
