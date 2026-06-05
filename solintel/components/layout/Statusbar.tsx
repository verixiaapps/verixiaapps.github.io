'use client'

import { useEffect, useState } from 'react'
import { getMonitoredWallets } from '../../lib/subscription'

export default function Statusbar() {
  const [slot, setSlot] = useState(284912441)
  const [monitoredCount, setMonitoredCount] = useState(0)

  useEffect(() => {
    setMonitoredCount(getMonitoredWallets().length)
    const interval = setInterval(() => {
      setSlot(s => s + Math.floor(Math.random() * 3 + 1))
    }, 400)
    return () => clearInterval(interval)
  }, [])

  const item = (color: string, label: string) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 8, letterSpacing: '0.09em', textTransform: 'uppercase', color: 'var(--t3)' }}>
      <div style={{ width: 4, height: 4, borderRadius: '50%', background: color, boxShadow: color === 'var(--green)' ? '0 0 4px var(--green)' : undefined }} />
      {label}
    </div>
  )

  return (
    <div style={{ height: 24, background: 'var(--s1)', borderTop: '1px solid var(--b1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', flexShrink: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {item('var(--green)', 'RPC Live')}
        {item('var(--green)', 'Feed Active')}
        {item('var(--yel)', `Slot ${slot.toLocaleString()}`)}
        {item('var(--t3)', '47 events today')}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {item('var(--t3)', `${monitoredCount} wallets monitored`)}
        {item('var(--t3)', 'SOLINTEL — The Operating System for Solana')}
      </div>
    </div>
  )
}
