'use client'

import { useState, useEffect } from 'react'
import Topbar from '../../components/layout/Topbar'
import LeftPanel from '../../components/layout/LeftPanel'
import Statusbar from '../../components/layout/Statusbar'
import UpgradeModal from '../../components/ui/UpgradeModal'
import { isSubscribed, getPlanLimits } from '../../lib/subscription'

interface Alert {
  id: string
  type: 'whale_buy' | 'whale_sell' | 'smart_entry' | 'smart_exit' | 'treasury' | 'governance'
  title: string
  detail: string
  wallet?: string
  amount?: string
  timestamp: number
  read: boolean
  delayed?: boolean
}

const DEMO_ALERTS: Alert[] = [
  { id: '1', type: 'whale_buy', title: '9aRK...3vNz bought 85,000 SOL', detail: 'Your monitored wallet accumulated $15.4M SOL via Jupiter', wallet: '9aRK...3vNz', amount: '$15.4M', timestamp: Date.now() - 2 * 60000, read: false },
  { id: '2', type: 'smart_entry', title: '7xKX...gAs2 entered $840K JUP', detail: 'Smart wallet you follow built a new position via DCA', wallet: '7xKX...gAs2', amount: '$840K', timestamp: Date.now() - 14 * 60000, read: false },
  { id: '3', type: 'treasury', title: 'Solana Foundation moved $4.2M', detail: 'Treasury wallet transferred to new 3-of-5 multisig', amount: '$4.2M', timestamp: Date.now() - 38 * 60000, read: false },
  { id: '4', type: 'whale_sell', title: 'BzWq...7dYc fully exited BONK', detail: 'High-performance wallet (84% win rate) sold entire position', wallet: 'BzWq...7dYc', amount: '$1.2M', timestamp: Date.now() - 3 * 3600000, read: true },
  { id: '5', type: 'governance', title: 'JUP DAO Proposal #41 created', detail: 'New governance proposal — voting opens in 6 hours', timestamp: Date.now() - 14 * 60000, read: true },
]

const LOCKED_ALERTS: Alert[] = [
  { id: 'l1', type: 'whale_buy', title: 'D4kL...9mPq bought 42,000 SOL', detail: 'Largest single SOL purchase in 72h — new unknown wallet', amount: '$7.6M', timestamp: Date.now() - 6 * 3600000, read: false, delayed: true },
  { id: 'l2', type: 'treasury', title: 'Jito Foundation transferred $2.1M', detail: 'Destination wallet created 12h before transfer', amount: '$2.1M', timestamp: Date.now() - 7 * 3600000, read: false, delayed: true },
  { id: 'l3', type: 'smart_entry', title: 'New smart money wallet entered JUP', detail: '92% win rate wallet built new position', amount: '$290K', timestamp: Date.now() - 8 * 3600000, read: false, delayed: true },
]

const TYPE_COLOR: Record<string, string> = {
  whale_buy: 'var(--green)', whale_sell: 'var(--red)',
  smart_entry: 'var(--green)', smart_exit: 'var(--red)',
  treasury: 'var(--blu)', governance: 'var(--yel)',
}

const TYPE_LABEL: Record<string, string> = {
  whale_buy: '🐋 Whale Buy', whale_sell: '⚠️ Whale Sell',
  smart_entry: '💡 Smart Entry', smart_exit: '⚠️ Smart Exit',
  treasury: '🏦 Treasury', governance: '🏛 Governance',
}

function timeAgo(ts: number) {
  const diff = Date.now() - ts
  const min = Math.floor(diff / 60000)
  const hr = Math.floor(diff / 3600000)
  if (min < 1) return 'just now'
  if (min < 60) return `${min}m ago`
  return `${hr}h ago`
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>(DEMO_ALERTS)
  const [upgradeOpen, setUpgradeOpen] = useState(false)
  const [subscribed, setSubscribed] = useState(false)
  const [limits, setLimits] = useState(getPlanLimits())

  useEffect(() => {
    setSubscribed(isSubscribed())
    setLimits(getPlanLimits())
  }, [])

  function markRead(id: string) {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, read: true } : a))
  }

  const unread = alerts.filter(a => !a.read).length

  return (
    <>
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Topbar />
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          <LeftPanel />

          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', borderRight: '1px solid var(--b1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', height: 44, borderBottom: '1px solid var(--b1)', background: 'var(--s1)', flexShrink: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--t1)' }}>
                <div className="live-dot" />
                Alerts Center
                {unread > 0 && <span style={{ background: 'var(--red)', color: '#fff', fontSize: 8, fontWeight: 700, padding: '1px 5px', borderRadius: 1 }}>{unread} unread</span>}
              </div>
              <button onClick={() => setAlerts(prev => prev.map(a => ({ ...a, read: true })))} style={{ fontSize: 9, letterSpacing: '0.08em', textTransform: 'uppercase', background: 'transparent', border: '1px solid var(--b2)', color: 'var(--t2)', padding: '4px 10px', cursor: 'pointer', fontFamily: 'Space Mono, monospace' }}>
                Mark all read
              </button>
            </div>

            {!subscribed && (
              <div style={{ padding: '10px 16px', background: 'var(--yfaint)', borderBottom: '1px solid rgba(240,191,48,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexShrink: 0 }}>
                <div style={{ fontSize: 11, color: 'var(--yel)' }}>⏱ Free plan: alerts are delayed 60 minutes. <span style={{ color: 'var(--t1)' }}>Upgrade for real-time alerts.</span></div>
                <button onClick={() => setUpgradeOpen(true)} style={{ padding: '5px 12px', background: 'var(--green)', color: '#000', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 9, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer', flexShrink: 0 }}>Get Real-Time →</button>
              </div>
            )}

            <div style={{ flex: 1, overflowY: 'auto' }}>
              {alerts.map(alert => (
                <div key={alert.id} onClick={() => markRead(alert.id)} style={{ display: 'grid', gridTemplateColumns: '4px 1fr', borderBottom: '1px solid var(--b1)', background: alert.read ? 'transparent' : 'var(--gfaint)', cursor: 'pointer', transition: 'background 0.1s' }}
                  onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = 'var(--s2)'}
                  onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = alert.read ? 'transparent' : 'var(--gfaint)'}
                >
                  <div style={{ background: TYPE_COLOR[alert.type] }} />
                  <div style={{ padding: '13px 16px', display: 'grid', gridTemplateColumns: '1fr auto', gap: 12, alignItems: 'start' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
                        <span style={{ fontSize: 8, letterSpacing: '0.12em', textTransform: 'uppercase', color: TYPE_COLOR[alert.type], fontWeight: 700 }}>{TYPE_LABEL[alert.type]}</span>
                        {!alert.read && <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--green)', display: 'inline-block' }} />}
                      </div>
                      <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 13, fontWeight: 700, color: 'var(--t0)', marginBottom: 4 }}>{alert.title}</div>
                      <div style={{ fontSize: 10, color: 'var(--t1)', lineHeight: 1.5 }}>{alert.detail}</div>
                      {alert.wallet && <div style={{ marginTop: 6, fontSize: 9, color: 'var(--t2)' }}>Wallet: <span style={{ color: 'var(--t1)' }}>{alert.wallet}</span></div>}
                    </div>
                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      {alert.amount && <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 16, fontWeight: 800, color: alert.type.includes('sell') || alert.type === 'smart_exit' ? 'var(--red)' : 'var(--green)', lineHeight: 1, marginBottom: 4 }}>{alert.amount}</div>}
                      <div style={{ fontSize: 9, color: 'var(--t2)' }}>{timeAgo(alert.timestamp)}</div>
                    </div>
                  </div>
                </div>
              ))}

              <div style={{ borderBottom: '1px solid var(--b2)', background: 'var(--s1)' }}>
                <div style={{ height: 3, background: 'linear-gradient(90deg, var(--yel), var(--red))' }} />
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', gap: 16 }}>
                  <div style={{ fontSize: 11, color: 'var(--t1)', lineHeight: 1.5 }}>
                    <span style={{ color: 'var(--t0)', fontFamily: 'Syne, sans-serif', fontSize: 13, fontWeight: 700 }}>Real-time alerts require Pro</span><br />
                    Free plan shows delayed alerts only. Upgrade to never miss a move.
                  </div>
                  <button onClick={() => setUpgradeOpen(true)} style={{ padding: '8px 16px', background: 'var(--green)', color: '#000', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 10, fontWeight: 700, letterSpacing: '0.09em', textTransform: 'uppercase', cursor: 'pointer', flexShrink: 0 }}>Get Real-Time Alerts →</button>
                </div>
              </div>

              {LOCKED_ALERTS.map(alert => (
                <div key={alert.id} style={{ opacity: 0.25, filter: 'blur(0.6px)', pointerEvents: 'none', display: 'grid', gridTemplateColumns: '4px 1fr', borderBottom: '1px solid var(--b1)' }}>
                  <div style={{ background: TYPE_COLOR[alert.type] }} />
                  <div style={{ padding: '13px 16px', display: 'grid', gridTemplateColumns: '1fr auto', gap: 12 }}>
                    <div>
                      <div style={{ fontSize: 8, letterSpacing: '0.12em', textTransform: 'uppercase', color: TYPE_COLOR[alert.type], fontWeight: 700, marginBottom: 5 }}>{TYPE_LABEL[alert.type]}</div>
                      <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 13, fontWeight: 700, color: 'var(--t0)', marginBottom: 4 }}>{alert.title}</div>
                      <div style={{ fontSize: 10, color: 'var(--t1)' }}>{alert.detail}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      {alert.amount && <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 16, fontWeight: 800, color: 'var(--green)' }}>{alert.amount}</div>}
                      <div style={{ fontSize: 9, color: 'var(--t2)' }}>{timeAgo(alert.timestamp)}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ width: 252, overflowY: 'auto', borderLeft: '1px solid var(--b1)' }}>
            <div style={{ padding: '8px 13px', borderBottom: '1px solid var(--b1)', background: 'var(--s1)', fontSize: 8, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--t2)', position: 'sticky', top: 0, zIndex: 10 }}>Alert Configuration</div>
            {[
              { label: '🐋 Whale movements', desc: 'Buys and sells over $1M', on: true },
              { label: '💡 Smart wallet entry', desc: 'Top wallets building positions', on: true },
              { label: '⚠️ Smart wallet exit', desc: 'Full exits from positions', on: true },
              { label: '🏛 Governance proposals', desc: 'New DAO proposals', on: true },
              { label: '🏦 Treasury activity', desc: 'Major treasury transfers', on: true },
              { label: '⚙️ Protocol updates', desc: 'Mainnet deployments', on: false, locked: true },
              { label: '📡 Ecosystem events', desc: 'Major ecosystem changes', on: false, locked: true },
            ].map(item => (
              <div key={item.label} style={{ padding: '10px 13px', borderBottom: '1px solid var(--b1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                <div style={{ opacity: item.locked ? 0.35 : 1 }}>
                  <div style={{ fontSize: 10, color: 'var(--t1)', marginBottom: 2 }}>{item.label}</div>
                  <div style={{ fontSize: 9, color: 'var(--t2)' }}>{item.desc}</div>
                </div>
                {item.locked ? (
                  <span onClick={() => setUpgradeOpen(true)} style={{ fontSize: 8, color: 'var(--t3)', border: '1px solid var(--b1)', padding: '1px 5px', cursor: 'pointer' }}>Pro</span>
                ) : (
                  <div className={`toggle ${item.on ? 'on' : ''}`} />
                )}
              </div>
            ))}
            {!subscribed && (
              <div style={{ margin: 12, border: '1px solid rgba(0,255,135,0.2)', background: 'var(--gfaint)', padding: '14px' }}>
                <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 13, fontWeight: 700, color: 'var(--t0)', marginBottom: 6 }}>Get Real-Time Alerts</div>
                <div style={{ fontSize: 10, color: 'var(--t1)', lineHeight: 1.5, marginBottom: 10 }}>Free plan: 60min delay.<br />Pro: alerts within seconds.</div>
                <button onClick={() => setUpgradeOpen(true)} style={{ width: '100%', background: 'var(--green)', color: '#000', border: 'none', padding: '8px', fontFamily: 'Space Mono, monospace', fontSize: 9, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer' }}>Upgrade — $11.99/mo</button>
              </div>
            )}
          </div>
        </div>
        <Statusbar />
      </div>
      <UpgradeModal open={upgradeOpen} onClose={() => setUpgradeOpen(false)} />
    </>
  )
}
