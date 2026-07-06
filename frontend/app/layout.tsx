import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Jan Awaaz — Constituency Development Priorities",
  description:
    "AI-powered platform for citizens to submit development suggestions and MPs to discover ranked constituency priorities.",
  keywords: ["constituency", "development", "citizen", "AI", "India", "MP", "governance"],
  openGraph: {
    title: "Jan Awaaz — Constituency Development Priorities",
    description: "Citizens speak. AI listens. MPs act.",
    type: "website",
  },
  manifest: "/manifest.json",
};

export const viewport = {
  themeColor: "#3b82f6",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} font-sans bg-surface-900 text-white antialiased min-h-screen`}
      >
        {children}
      </body>
    </html>
  );
}
