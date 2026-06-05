'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const NAV = [
  { href: '/solintel', label: '⚡ Feed' },
  { href: '/solintel/alerts', label: '🔔 Alerts', badge: '7' },
  { href: '/solintel/watchlists', label: '👁 Watchlists' },
  { href: '/solintel/wallet', label: '🔍 Wallet Lookup' },
  { href: '/solintel/pricing', label: '💎 Pricing' },
]

export default function Topbar() {
  const path = usePathname()

  return (
    <div style={{ height: 46, display: 'flex', alignItems: 'center', borderBottom: '1px solid var(--b1)', background: 'var(--s1)', flexShrink: 0, zIndex: 100 }}>

      <Link href="/solintel" style={{ width: 192, height: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '0 16px', borderRight: '1px solid var(--b1)', flexShrink: 0, textDecoration: 'none' }}>
        <div style={{ width: 22, height: 22, border: '1.5px solid var(--green)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <div style={{ width: 8, height: 8, background: 'var(--green)', boxShadow: '0 0 10px var(--green), 0 0 20px rgba(0,255,135,0.3)', animation: 'breathe 3s ease infinite' }} />
        </div>
        <span style={{ fontFamily: 'Syne, sans-serif', fontSize: 17, fontWeight: 800, color: 'var(--t0)', letterSpacing: '-0.3px' }}>
          SOLINTEL
        </span>
      </Link>

      <div style={{ display: 'flex', height: '100%', flex: 1, overflow: 'hidden' }}>
        {NAV.map(item => {
          const active = path === item.href
          return (
            <Link key={item.href} href={item.href} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '0 14px', fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase', color: active ? 'var(--green)' : 'var(--t2)', borderBottom: active ? '2px solid var(--green)' : '2px solid transparent', borderRight: '1px solid var(--b1)', marginBottom: -1, textDecoration: 'none', whiteSpace: 'nowrap', background: active ? 'var(--gfaint)' : 'transparent', transition: 'all 0.12s' }}>
              {item.label}
              {item.badge && (
                <span style={{ background: 'var(--red)', color: '#fff', fontSize: 8, fontWeight: 700, padding: '1px 4px', borderRadius: 1 }}>
                  {item.badge}
                </span>
              )}
            </Link>
          )
        })}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0 14px', borderLeft: '1px solid var(--b1)', flexShrink: 0 }}>
        <button style={{ padding: '5px 11px', fontFamily: 'Space Mono, monospace', fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase', cursor: 'pointer', border: '1px solid var(--b2)', background: 'transparent', color: 'var(--t1)' }}>
          Sign In
        </button>
        <Link href="/solintel/pricing" style={{ padding: '5px 11px', fontFamily: 'Space Mono, monospace', fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase', background: 'var(--green)', color: '#000', fontWeight: 700, textDecoration: 'none', display: 'inline-block', transition: 'background 0.12s' }}>
          Start Monitoring →
        </Link>
      </div>
    </div>
  )
}
