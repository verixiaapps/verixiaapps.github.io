'use client'

import { useState, useEffect, useCallback } from 'react'
import Topbar from '../components/layout/Topbar'
import LeftPanel from '../components/layout/LeftPanel'
import Statusbar from '../components/layout/Statusbar'
import EventCard from '../components/feed/EventCard'
import UpgradeModal from '../components/ui/UpgradeModal'
import { generateFeedEvents, type FeedEvent } from '../lib/solana'
import { addMonitoredWallet, getPlanLimits, getMonitoredWallets, getWatchlists } from '../lib/subscription'

const FILTERS = ['All', 'Whale', 'Smart$', 'Treasury', 'Gov', 'Protocol']

const TODAY = {
  events: 47, alerts: 7, whaleActions: 5,
  govProposals: 3, treasuryMoved: '$28M', smartEntries: 8,
}

export default function FeedPage() {
  const [events, setEvents] = useState<FeedEvent[]>([])
  const [filter, setFilter] = useState('All')
  const [upgradeOpen, setUpgradeOpen] = useState(false)
  const [searchVal, setSearchVal] = useState('')
  const [wallets, setWallets] = useState<string[]>([])
  const [watchlists, setWatchlists] = useState<ReturnType<typeof getWatchlists>>([])
  const [limits, setLimits] = useState(getPlanLimits())

  useEffect(() => {
    setEvents(generateFeedEvents())
    setWallets(getMonitoredWallets())
    setWatchlists(getWatchlists())
    setLimits(getPlanLimits())
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setEvents(prev => {
        const newEvent: FeedEvent = {
          id: Date.now().toString(),
          type: ['whale_buy', 'smart_entry', 'treasury'][Math.floor(Math.random() * 3)] as FeedEvent['type'],
          title: 'New whale movement detected',
          detail: 'Large SOL transfer between unknown wallets via Jupiter aggregator',
          amount: `$${(Math.random() * 10 + 1).toFixed(1)}M`,
          address: `${Math.random().toString(36).slice(2, 6)}...${Math.random().toString(36).slice(2, 6)}`,
          timestamp: Date.now(),
          isNew: true,
        }
        return [newEvent, ...prev.slice(0, 10)]
      })
    }, 25000)
    return () => clearInterval(interval)
  }, [])

  const handleTrack = useCallback((address: string) => {
    const success = addMonitoredWallet(address)
    if (!success) setUpgradeOpen(true)
    else setWallets(getMonitoredWallets())
  }, [])

  const filteredEvents = events.filter(e => {
    if (filter === 'All') return true
    if (filter === 'Whale') return e.type === 'whale_buy' || e.type === 'whale_sell'
    if (filter === 'Smart$') return e.type === 'smart_entry' || e.type === 'smart_exit'
    if (filter === 'Treasury') return e.type === 'treasury'
    if (filter === 'Gov') return e.type === 'governance'
    return true
  })

  const LOCKED_EVENTS: FeedEvent[] = [
    { id: 'l1', type: 'whale_buy', title: 'Whale accumulated 42,000 SOL in single transaction', detail: 'Largest single SOL purchase in 72 hours — new wallet, first transaction', amount: '$7.6M', address: 'D4kL...9mPq', timestamp: Date.now() - 6 * 3600000 },
    { id: 'l2', type: 'treasury', title: 'Jito Foundation transferred $2.1M to unknown wallet', detail: 'Destination wallet was created 12 hours before transfer — monitoring active', amount: '$2.1M', address: 'JiTo...3mXk', timestamp: Date.now() - 7 * 3600000 },
  ]

  return (
    <>
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Topbar />
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          <LeftPanel />

          <div style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden', borderRight: '1px solid var(--b1)' }}>

            <div style={{ display: 'flex', alignItems: 'center', borderBottom: '1px solid var(--b1)', background: 'var(--s1)', flexShrink: 0, height: 36 }}>
              <div style={{ padding: '0 12px', fontSize: 9, letterSpacing: '0.12em', color: 'var(--green)', borderRight: '1px solid var(--b1)', height: '100%', display: 'flex', alignItems: 'center', flexShrink: 0 }}>SOL://</div>
              <input value={searchVal} onChange={e => setSearchVal(e.target.value)} placeholder="Search wallet, protocol, treasury, entity…" style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--t0)', padding: '0 13px', fontFamily: 'Space Mono, monospace', fontSize: 11, outline: 'none' }} />
              <div style={{ display: 'flex', height: '100%', borderLeft: '1px solid var(--b1)' }}>
                <button style={{ padding: '0 13px', fontFamily: 'Space Mono, monospace', fontSize: 9, letterSpacing: '0.09em', textTransform: 'uppercase', background: 'transparent', border: 'none', borderRight: '1px solid var(--b1)', color: 'var(--t2)', cursor: 'pointer' }} onClick={() => searchVal && (window.location.href = `/solintel/wallet?address=${searchVal}`)}>Analyze</button>
                <button style={{ padding: '0 13px', fontFamily: 'Space Mono, monospace', fontSize: 9, letterSpacing: '0.09em', textTransform: 'uppercase', background: 'transparent', border: 'none', color: 'var(--green)', fontWeight: 700, cursor: 'pointer' }} onClick={() => searchVal && handleTrack(searchVal)}>Watch →</button>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', height: 34, borderBottom: '1px solid var(--b1)', background: 'var(--s1)', flexShrink: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 9, letterSpacing: '0.11em', textTransform: 'uppercase', color: 'var(--t1)' }}>
                <div className="live-dot" />
                Live Intelligence Feed
                <span style={{ color: 'var(--green)', fontWeight: 700 }}>47 events today · {events.filter(e => e.isNew).length} unread</span>
              </div>
              <div style={{ display: 'flex', gap: 2 }}>
                {FILTERS.map(f => (
                  <button key={f} onClick={() => setFilter(f)} style={{ padding: '3px 9px', fontFamily: 'Space Mono, monospace', fontSize: 8, letterSpacing: '0.09em', textTransform: 'uppercase', background: filter === f ? 'var(--gfaint2)' : 'transparent', border: `1px solid ${filter === f ? 'rgba(0,255,135,0.3)' : 'var(--b1)'}`, color: filter === f ? 'var(--green)' : 'var(--t2)', cursor: 'pointer', transition: 'all 0.1s' }}>
                    {f}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ flex: 1, overflowY: 'auto' }}>
              {filteredEvents.map((event, i) => (
                <EventCard key={event.id} event={event} delay={i * 0.04} onTrack={handleTrack} />
              ))}

              {/* Locked events */}
              <div style={{ position: 'relative' }}>
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom, transparent, var(--bg) 60%)', zIndex: 10, pointerEvents: 'none' }} />
                {LOCKED_EVENTS.map(event => (
                  <div key={event.id} style={{ opacity: 0.35, filter: 'blur(2px)', pointerEvents: 'none' }}>
                    <EventCard event={event} />
                  </div>
                ))}
              </div>

              <div style={{ padding: '20px 16px', background: 'linear-gradient(135deg, rgba(0,255,135,0.04), rgba(0,0,0,0))', border: '1px solid rgba(0,255,135,0.12)', margin: '0 16px 16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 13, fontWeight: 700, color: 'var(--t0)', marginBottom: 6 }}>Never miss an important Solana event again.</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                      {['Never miss a whale move', 'Alerts within seconds', 'Unlimited wallet tracking', 'Governance monitoring', 'Treasury alerts', 'Daily intelligence reports'].map(f => (
                        <span key={f} style={{ fontSize: 9, color: 'var(--gdim)', border: '1px solid var(--b2)', padding: '2px 7px' }}>✓ {f}</span>
                      ))}
                    </div>
                  </div>
                  <div style={{ flexShrink: 0, textAlign: 'right' }}>
                    <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 26, fontWeight: 800, color: 'var(--green)', lineHeight: 1 }}>$11.99</div>
                    <div style={{ fontSize: 9, color: 'var(--t2)', marginBottom: 8 }}>/ month · cancel anytime</div>
                    <button onClick={() => setUpgradeOpen(true)} style={{ background: 'var(--green)', color: '#000', border: 'none', padding: '8px 16px', fontFamily: 'Space Mono, monospace', fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer' }}>Start Monitoring →</button>
                  </div>
                </div>
                <div style={{ height: 28, borderTop: '1px solid var(--b1)', marginTop: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ fontSize: 9, color: 'var(--t2)', flex: 1 }}>Intelligence found a position worth acting on? <strong style={{ color: 'var(--t1)' }}>Execute instantly on swap.verixiaapps.com</strong></div>
                  <a href="https://swap.verixiaapps.com" target="_blank" rel="noopener noreferrer" style={{ fontSize: 9, letterSpacing: '0.09em', textTransform: 'uppercase', color: 'var(--t2)', textDecoration: 'none', border: '1px solid var(--b2)', padding: '2px 8px' }}>Open DEX →</a>
                </div>
              </div>
            </div>
          </div>

          <div style={{ width: 252, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ borderBottom: '1px solid var(--b1)', flexShrink: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 13px', borderBottom: '1px solid var(--b1)', background: 'var(--s1)' }}>
                <div style={{ fontSize: 8, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--t2)', display: 'flex', alignItems: 'center', gap: 6 }}><div className="live-dot" />Today&apos;s Activity</div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, background: 'var(--b1)' }}>
                {[
                  { val: TODAY.events, label: 'Events', sub: '12 unread', color: 'var(--green)' },
                  { val: TODAY.alerts, label: 'Your Alerts', sub: '3 critical', color: 'var(--red)' },
                  { val: TODAY.whaleActions, label: 'Whale Actions', sub: '3 buys · 2 exits', color: 'var(--green)' },
                  { val: TODAY.govProposals, label: 'Gov Proposals', sub: '1 vote open', color: 'var(--yel)' },
                  { val: TODAY.treasuryMoved, label: 'Treasury Moved', sub: '4 transactions', color: 'var(--t0)' },
                  { val: TODAY.smartEntries, label: 'Smart Entries', sub: '2 exits detected', color: 'var(--green)' },
                ].map(item => (
                  <div key={item.label} style={{ background: 'var(--s1)', padding: '11px 13px' }}>
                    <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, fontWeight: 800, lineHeight: 1, color: item.color }}>{item.val}</div>
                    <div style={{ fontSize: 8, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--t2)', marginTop: 3 }}>{item.label}</div>
                    <div style={{ fontSize: 9, color: 'var(--t1)', marginTop: 2 }}>{item.sub}</div>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ borderBottom: '1px solid var(--b1)', flexShrink: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 13px', borderBottom: '1px solid var(--b1)', background: 'var(--s1)' }}>
                <div style={{ fontSize: 8, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--t2)' }}>My Watchlist</div>
                <a href="/solintel/watchlists" style={{ fontSize: 8, letterSpacing: '0.09em', textTransform: 'uppercase', color: 'var(--t2)', textDecoration: 'none' }}>Manage →</a>
              </div>
              {wallets.length === 0 ? (
                <div style={{ padding: '12px 13px', fontSize: 10, color: 'var(--t3)' }}>No wallets monitored yet.</div>
              ) : (
                wallets.slice(0, 5).map(addr => (
                  <div key={addr} style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '9px 13px', borderBottom: '1px solid var(--b1)', cursor: 'pointer' }}>
                    <div style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--green)', boxShadow: '0 0 5px var(--green)', flexShrink: 0 }} />
                    <div style={{ width: 26, height: 26, background: 'var(--s2)', border: '1px solid var(--b2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 8, fontWeight: 700, color: 'var(--t1)', flexShrink: 0 }}>{addr.slice(0, 3).toUpperCase()}</div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 10, color: 'var(--t0)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{addr.slice(0, 8)}...{addr.slice(-4)}</div>
                      <div style={{ fontSize: 9, color: 'var(--t2)' }}>Wallet · Monitoring</div>
                    </div>
                  </div>
                ))
              )}
              <div onClick={() => wallets.length >= limits.maxWallets ? setUpgradeOpen(true) : (window.location.href = '/solintel/watchlists')} style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '8px 13px', fontSize: 9, color: 'var(--t3)', cursor: 'pointer', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                + Add wallet or entity
              </div>
            </div>

            <div style={{ flex: 1, overflowY: 'auto' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 13px', borderBottom: '1px solid var(--b1)', background: 'var(--s1)', position: 'sticky', top: 0, zIndex: 10 }}>
                <div style={{ fontSize: 8, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--t2)' }}>Alert Configuration</div>
              </div>
              {[
                { label: '🐋 Whale movements', on: true },
                { label: '💡 Smart wallet entry', on: true },
                { label: '⚠️ Smart wallet exit', on: true },
                { label: '🏛 Governance proposals', on: true },
                { label: '🏦 Treasury activity', on: true },
                { label: '⚙️ Protocol updates', on: false, locked: true },
                { label: '📡 Ecosystem events', on: false, locked: true },
              ].map(item => (
                <div key={item.label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 13px', borderBottom: '1px solid var(--b1)', cursor: 'pointer' }}>
                  <div style={{ fontSize: 10, color: 'var(--t1)', opacity: item.locked ? 0.35 : 1 }}>{item.label}</div>
                  {item.locked ? (
                    <span onClick={() => setUpgradeOpen(true)} style={{ fontSize: 8, color: 'var(--t3)', border: '1px solid var(--b1)', padding: '1px 5px', cursor: 'pointer' }}>Pro</span>
                  ) : (
                    <div className={`toggle ${item.on ? 'on' : ''}`} />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
        <Statusbar />
      </div>
      <UpgradeModal open={upgradeOpen} onClose={() => setUpgradeOpen(false)} />
    </>
  )
}
