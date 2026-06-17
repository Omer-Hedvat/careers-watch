import type { Metadata } from "next";
import "./globals.css";

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
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
