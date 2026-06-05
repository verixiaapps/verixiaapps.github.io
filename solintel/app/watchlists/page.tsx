'use client'

import { useState, useEffect } from 'react'
import Topbar from '../../components/layout/Topbar'
import LeftPanel from '../../components/layout/LeftPanel'
import Statusbar from '../../components/layout/Statusbar'
import UpgradeModal from '../../components/ui/UpgradeModal'
import {
  getWatchlists, addWatchlist, addMonitoredWallet,
  getMonitoredWallets, removeMonitoredWallet,
  getPlanLimits, isSubscribed, type Watchlist,
} from '../../lib/subscription'

export default function WatchlistsPage() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([])
  const [monitored, setMonitored] = useState<string[]>([])
  const [limits, setLimits] = useState(getPlanLimits())
  const [subscribed, setSubscribed] = useState(false)
  const [upgradeOpen, setUpgradeOpen] = useState(false)
  const [newListName, setNewListName] = useState('')
  const [newAddr, setNewAddr] = useState('')
  const [activeList, setActiveList] = useState<string | null>(null)

  useEffect(() => {
    setWatchlists(getWatchlists())
    setMonitored(getMonitoredWallets())
    setLimits(getPlanLimits())
    setSubscribed(isSubscribed())
  }, [])

  function createList() {
    if (!newListName.trim()) return
    if (watchlists.length >= limits.maxWatchlists) { setUpgradeOpen(true); return }
    const wl = addWatchlist(newListName.trim())
    if (wl) { setWatchlists(getWatchlists()); setNewListName('') }
  }

  function handleAddWallet() {
    const addr = newAddr.trim()
    if (!addr) return
    const success = addMonitoredWallet(addr)
    if (!success) setUpgradeOpen(true)
    else { setMonitored(getMonitoredWallets()); setNewAddr('') }
  }

  function handleRemoveWallet(addr: string) {
    removeMonitoredWallet(addr)
    setMonitored(getMonitoredWallets())
  }

  const atWalletLimit = monitored.length >= limits.maxWallets
  const atListLimit = watchlists.length >= limits.maxWatchlists

  return (
    <>
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Topbar />
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          <LeftPanel />

          <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

            <div style={{ width: 260, borderRight: '1px solid var(--b1)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div style={{ padding: '8px 13px', borderBottom: '1px solid var(--b1)', background: 'var(--s1)', fontSize: 8, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--t2)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
                <span>My Watchlists ({watchlists.length}/{limits.maxWatchlists})</span>
                {atListLimit && <span onClick={() => setUpgradeOpen(true)} style={{ color: 'var(--red)', cursor: 'pointer' }}>Limit reached</span>}
              </div>

              <div style={{ flex: 1, overflowY: 'auto' }}>
                {watchlists.length === 0 && (
                  <div style={{ padding: '20px 13px', fontSize: 10, color: 'var(--t3)' }}>No watchlists yet. Create one below.</div>
                )}
                {watchlists.map(list => (
                  <div key={list.id} onClick={() => setActiveList(list.id)} style={{ padding: '10px 13px', borderBottom: '1px solid var(--b1)', cursor: 'pointer', background: activeList === list.id ? 'var(--gfaint)' : 'transparent', borderLeft: `3px solid ${activeList === list.id ? 'var(--green)' : 'transparent'}` }}>
                    <div style={{ fontSize: 11, color: 'var(--t0)', marginBottom: 2 }}>{list.name}</div>
                    <div style={{ fontSize: 9, color: 'var(--t2)' }}>{list.wallets.length} wallets</div>
                  </div>
                ))}
              </div>

              <div style={{ padding: '10px 13px', borderTop: '1px solid var(--b1)', flexShrink: 0 }}>
                <div style={{ fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--t2)', marginBottom: 6 }}>New Watchlist</div>
                <div style={{ display: 'flex', gap: 6 }}>
                  <input value={newListName} onChange={e => setNewListName(e.target.value)} onKeyDown={e => e.key === 'Enter' && createList()} placeholder="Smart Money, Whales…" style={{ flex: 1, background: 'var(--s2)', border: '1px solid var(--b2)', color: 'var(--t0)', padding: '5px 8px', fontFamily: 'Space Mono, monospace', fontSize: 10, outline: 'none' }} />
                  <button onClick={atListLimit ? () => setUpgradeOpen(true) : createList} style={{ padding: '5px 9px', background: atListLimit ? 'var(--s2)' : 'var(--green)', color: atListLimit ? 'var(--t2)' : '#000', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 9, fontWeight: 700, cursor: 'pointer' }}>+</button>
                </div>
                {atListLimit && !subscribed && <div style={{ marginTop: 6, fontSize: 9, color: 'var(--yel)' }}>Upgrade for unlimited watchlists</div>}
              </div>
            </div>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div style={{ padding: '0 16px', height: 44, borderBottom: '1px solid var(--b1)', background: 'var(--s1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
                <div style={{ fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--t1)', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div className="live-dot" />
                  Monitored Wallets ({monitored.length}/{limits.maxWallets})
                  {atWalletLimit && <span style={{ fontSize: 8, background: 'var(--rfaint)', border: '1px solid var(--red)', color: 'var(--red)', padding: '1px 5px' }}>Limit reached</span>}
                </div>
                {atWalletLimit && (
                  <button onClick={() => setUpgradeOpen(true)} style={{ padding: '5px 12px', background: 'var(--green)', color: '#000', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 9, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer' }}>Upgrade for Unlimited →</button>
                )}
              </div>

              <div style={{ padding: '10px 16px', borderBottom: '1px solid var(--b1)', background: 'var(--s1)', flexShrink: 0 }}>
                <div style={{ display: 'flex', gap: 8 }}>
                  <input value={newAddr} onChange={e => setNewAddr(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleAddWallet()} placeholder="Paste Solana wallet address to monitor…" style={{ flex: 1, background: 'var(--s2)', border: '1px solid var(--b2)', color: 'var(--t0)', padding: '8px 12px', fontFamily: 'Space Mono, monospace', fontSize: 11, outline: 'none' }} />
                  <button onClick={atWalletLimit ? () => setUpgradeOpen(true) : handleAddWallet} style={{ padding: '8px 14px', background: atWalletLimit ? 'var(--s2)' : 'var(--green)', color: atWalletLimit ? 'var(--t2)' : '#000', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 9, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer' }}>
                    {atWalletLimit ? 'Limit Reached' : 'Watch Wallet →'}
                  </button>
                </div>
              </div>

              <div style={{ flex: 1, overflowY: 'auto' }}>
                {monitored.length === 0 ? (
                  <div style={{ padding: '40px 20px', textAlign: 'center' }}>
                    <div style={{ fontSize: 24, marginBottom: 12 }}>👁</div>
                    <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 16, fontWeight: 700, color: 'var(--t0)', marginBottom: 6 }}>No wallets monitored yet</div>
                    <div style={{ fontSize: 11, color: 'var(--t1)', lineHeight: 1.6 }}>Paste a Solana wallet address above to start monitoring.<br />You&apos;ll get alerts when it makes a significant move.</div>
                  </div>
                ) : (
                  monitored.map(addr => (
                    <div key={addr} style={{ display: 'grid', gridTemplateColumns: '8px 36px 1fr auto', alignItems: 'center', gap: 12, padding: '12px 16px', borderBottom: '1px solid var(--b1)', transition: 'background 0.1s' }}
                      onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = 'var(--s2)'}
                      onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = 'transparent'}
                    >
                      <div style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--green)', boxShadow: '0 0 5px var(--green)', animation: 'pulse 2s infinite' }} />
                      <div style={{ width: 32, height: 32, background: 'var(--s2)', border: '1px solid var(--b2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 8, fontWeight: 700, color: 'var(--t1)', fontFamily: 'Syne, sans-serif' }}>
                        {addr.slice(0, 3).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontSize: 11, color: 'var(--t0)', fontFamily: 'Space Mono, monospace', marginBottom: 2 }}>{addr.slice(0, 8)}...{addr.slice(-6)}</div>
                        <div style={{ fontSize: 9, color: 'var(--t2)' }}>Monitoring · Real-time alerts active</div>
                      </div>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <a href={`/solintel/wallet?address=${addr}`} style={{ fontSize: 8, letterSpacing: '0.08em', textTransform: 'uppercase', border: '1px solid var(--b2)', padding: '3px 8px', color: 'var(--t2)', textDecoration: 'none' }}>View</a>
                        <button onClick={() => handleRemoveWallet(addr)} style={{ fontSize: 8, letterSpacing: '0.08em', textTransform: 'uppercase', border: '1px solid var(--rfaint)', padding: '3px 8px', color: 'var(--red)', background: 'var(--rfaint)', cursor: 'pointer', fontFamily: 'Space Mono, monospace' }}>Remove</button>
                      </div>
                    </div>
                  ))
                )}

                {atWalletLimit && (
                  <div style={{ margin: '16px', border: '1px solid rgba(0,255,135,0.2)', background: 'var(--gfaint)', padding: '16px' }}>
                    <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 13, fontWeight: 700, color: 'var(--t0)', marginBottom: 6 }}>Wallet limit reached ({limits.maxWallets}/{limits.maxWallets})</div>
                    <div style={{ fontSize: 10, color: 'var(--t1)', lineHeight: 1.5, marginBottom: 10 }}>Upgrade to monitor unlimited wallets and never miss a move.</div>
                    <button onClick={() => setUpgradeOpen(true)} style={{ width: '100%', background: 'var(--green)', color: '#000', border: 'none', padding: '9px', fontFamily: 'Space Mono, monospace', fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer' }}>
                      Upgrade to Unlimited — $11.99/mo
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
        <Statusbar />
      </div>
      <UpgradeModal open={upgradeOpen} onClose={() => setUpgradeOpen(false)} />
    </>
  )
}
