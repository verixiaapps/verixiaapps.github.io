import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SolIntel — Solana Intelligence Platform',
  description: 'Monitor Solana wallets in real time. Get alerts when whales move, smart money enters positions, and important ecosystem events happen.',
  keywords: 'solana wallet monitor, whale alerts, solana intelligence, wallet tracking, defi monitoring',
  openGraph: {
    title: 'SolIntel — Solana Intelligence Platform',
    description: 'Never miss an important Solana event again.',
    type: 'website',
  },
}

export default function SolIntelLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      {children}
    </>
  )
}
