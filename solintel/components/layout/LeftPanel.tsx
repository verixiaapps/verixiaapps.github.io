'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'
import { getMonitoredWallets, getPlanLimits, isSubscribed } from '../../lib/subscription'

export default function LeftPanel() {
  const path = usePathname()
  const [walletCount, setWalletCount] = useState(0)
  const [limits, setLimits] = useState({ maxWallets: 3, maxWatchlists: 1 })
  const [subscribed, setSubscribed] = useState(false)

  useEffect(() => {
    setWalletCount(getMonitoredWallets().length)
    setLimits(getPlanLimits())
    setSubscribed(isSubscribed())
  }, [])

  const walletPct = (walletCount / limits.maxWallets) * 100
  const atLimit = walletCount >= limits.maxWallets

  const nl = (href: string, icon: string, label: string, badge?: { val: string; type: 'red' | 'green' | 'neu' }) => {
    const active = path === href
    return (
      <Link href={href} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 14px', fontSize: 10, color: active ? 'var(--green)' : 'var(--t1)', background: active ? 'var(--gfaint)' : 'transparent', textDecoration: 'none', transition: 'all 0.1s' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 13, textAlign: 'center', fontSize: 10 }}>{icon}</span>
          {label}
        </div>
        {badge && (
          <span style={{ fontSize: 8, padding: '1px 5px', fontWeight: 700, borderRadius: 1, background: badge.type === 'red' ? 'var(--rfaint)' : badge.type === 'green' ? 'var(--gfaint)' : 'var(--s2)', border: `1px solid ${badge.type === 'red' ? 'var(--red)' : badge.type === 'green' ? 'var(--gdim)' : 'var(--b2)'}`, color: badge.type === 'red' ? 'var(--red)' : badge.type === 'green' ? 'var(--gdim)' : 'var(--t2)' }}>
            {badge.val}
          </span>
        )}
      </Link>
    )
  }

  const groupLabel = (label: string) => (
    <div style={{ fontSize: 8, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--t3)', padding: '0 14px', marginBottom: 3 }}>{label}</div>
  )

  return (
    <div style={{ width: 192, borderRight: '1px solid var(--b1)', display: 'flex', flexDirection: 'column', overflowY: 'auto', overflowX: 'hidden', flexShrink: 0 }}>

      <div style={{ padding: '14px 14px 13px', background: 'linear-gradient(180deg, var(--gfaint2) 0%, var(--gfaint) 100%)', borderBottom: '1px solid var(--b2)' }}>
        <div style={{ fontSize: 8, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--gdim)', marginBottom: 11, display: 'flex', alignItems: 'center', gap: 7 }}>
          <div className="live-dot" style={{ width: 5, height: 5 }} />
          {subscribed ? 'Pro Monitoring' : 'Free Plan'}
        </div>

        {[
          { key: 'Wallets tracked', val: `${walletCount} / ${limits.maxWallets}`, color: atLimit ? 'var(--red)' : 'var(--green)' },
          { key: 'Alerts today', val: '7 fired', color: 'var(--red)' },
          { key: 'Feed events', val: '47 today', color: 'var(--t0)' },
        ].map(row => (
          <div key={row.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 7 }}>
            <div style={{ fontSize: 10, color: 'var(--t1)' }}>{row.key}</div>
            <div style={{ fontSize: 11, fontWeight: 700, color: row.color }}>{row.val}</div>
          </div>
        ))}

        <div style={{ height: 2, background: 'var(--b2)', margin: '9px 0 4px', position: 'relative' }}>
          <div style={{ height: '100%', width: `${Math.min(100, walletPct)}%`, background: atLimit ? 'var(--red)' : 'var(--green)', boxShadow: atLimit ? '0 0 6px rgba(255,61,85,0.5)' : '0 0 6px rgba(0,255,135,0.5)', transition: 'width 0.3s ease' }} />
        </div>
        <div style={{ fontSize: 8, color: atLimit ? 'var(--red)' : 'var(--t2)', marginBottom: 10 }}>
          {atLimit ? '⚠ Wallet limit reached' : `${limits.maxWallets - walletCount} slots remaining`}
        </div>

        <Link href="/solintel/pricing" style={{ display: 'block', width: '100%', background: 'transparent', border: '1px solid rgba(0,255,135,0.22)', color: 'var(--green)', padding: 7, fontFamily: 'Space Mono, monospace', fontSize: 9, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', cursor: 'pointer', textAlign: 'center', textDecoration: 'none', transition: 'all 0.15s' }}>
          {subscribed ? 'Manage Plan' : 'Upgrade to Unlimited →'}
        </Link>
      </div>

      <div style={{ borderBottom: '1px solid var(--b1)', padding: '8px 0' }}>
        {groupLabel('Monitor')}
        {nl('/solintel', '⚡', 'Feed', { val: '47', type: 'green' })}
        {nl('/solintel/alerts', '🔔', 'Alerts Center', { val: '7', type: 'red' })}
        {nl('/solintel/watchlists', '👁', 'Watchlists', { val: '1', type: 'neu' })}
        {nl('/solintel/wallet', '🐋', 'Smart Money')}
      </div>

      <div style={{ borderBottom: '1px solid var(--b1)', padding: '8px 0' }}>
        {groupLabel('Research')}
        {nl('/solintel/wallet', '🔍', 'Wallet Lookup')}
        {nl('/solintel/pricing', '💎', 'Pricing')}
      </div>
    </div>
  )
}
