'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Topbar from '../../components/layout/Topbar'
import LeftPanel from '../../components/layout/LeftPanel'
import Statusbar from '../../components/layout/Statusbar'
import UpgradeModal from '../../components/ui/UpgradeModal'
import {
  getBalance, getWalletTransactions, getSolPrice,
  isValidSolanaAddress, classifyWallet, computeRiskScore,
} from '../../lib/solana'
import { addMonitoredWallet, isMonitored, getPlanLimits } from '../../lib/subscription'

interface WalletData {
  address: string
  balance: number
  solPrice: number
  transactions: any[]
  walletType: string
  riskScore: number
  isMonitoredNow: boolean
}

function WalletContent() {
  const params = useSearchParams()
  const [address, setAddress] = useState(params.get('address') || '')
  const [inputVal, setInputVal] = useState(params.get('address') || '')
  const [data, setData] = useState<WalletData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [upgradeOpen, setUpgradeOpen] = useState(false)
  const [justTracked, setJustTracked] = useState(false)

  useEffect(() => {
    if (address && isValidSolanaAddress(address)) loadWallet(address)
  }, [address])

  async function loadWallet(addr: string) {
    setLoading(true)
    setError('')
    setData(null)
    try {
      const [balance, txns, solPrice] = await Promise.all([
        getBalance(addr),
        getWalletTransactions(addr, 10),
        getSolPrice(),
      ])
      const txCount = Array.isArray(txns) ? txns.length : 0
      const walletType = classifyWallet(balance, txCount)
      const riskScore = computeRiskScore({ balance, txCount, tokenCount: 0, ageInDays: 180 })
      setData({
        address: addr, balance, solPrice,
        transactions: Array.isArray(txns) ? txns.slice(0, 8) : [],
        walletType, riskScore,
        isMonitoredNow: isMonitored(addr),
      })
    } catch (e) {
      setError('Could not load wallet data. Check the address and try again.')
    } finally {
      setLoading(false)
    }
  }

  function handleSearch() {
    const val = inputVal.trim()
    if (!val) return
    if (!isValidSolanaAddress(val)) { setError('Invalid Solana address. Enter a valid base58 wallet address.'); return }
    setAddress(val)
    window.history.pushState({}, '', `/solintel/wallet?address=${val}`)
  }

  function handleMonitor() {
    if (!data) return
    const success = addMonitoredWallet(data.address)
    if (!success) setUpgradeOpen(true)
    else {
      setData(prev => prev ? { ...prev, isMonitoredNow: true } : null)
      setJustTracked(true)
      setTimeout(() => setJustTracked(false), 3000)
    }
  }

  const riskColor = (score: number) =>
    score >= 70 ? 'var(--green)' : score >= 40 ? 'var(--yel)' : 'var(--red)'

  const typeLabel: Record<string, string> = {
    whale: '🐋 Whale', large: '💰 Large', active: '⚡ Active',
    regular: '👤 Regular', small: '🔍 Small',
  }

  return (
    <>
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Topbar />
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          <LeftPanel />
          <div style={{ flex: 1, overflowY: 'auto', padding: '0 0 24px' }}>

            <div style={{ display: 'flex', alignItems: 'center', borderBottom: '1px solid var(--b1)', background: 'var(--s1)', flexShrink: 0, height: 50, padding: '0 16px', gap: 10 }}>
              <div style={{ fontSize: 9, letterSpacing: '0.12em', color: 'var(--green)', flexShrink: 0 }}>SOL://</div>
              <input value={inputVal} onChange={e => setInputVal(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSearch()} placeholder="Enter Solana wallet address…" style={{ flex: 1, background: 'var(--s2)', border: '1px solid var(--b2)', color: 'var(--t0)', padding: '8px 12px', fontFamily: 'Space Mono, monospace', fontSize: 12, outline: 'none' }} />
              <button onClick={handleSearch} style={{ padding: '8px 16px', background: 'var(--s2)', border: '1px solid var(--b2)', color: 'var(--t1)', fontFamily: 'Space Mono, monospace', fontSize: 9, letterSpacing: '0.09em', textTransform: 'uppercase', cursor: 'pointer' }}>Analyze</button>
              <button onClick={handleMonitor} disabled={!data || data.isMonitoredNow} style={{ padding: '8px 16px', background: data?.isMonitoredNow ? 'var(--s2)' : 'var(--green)', color: data?.isMonitoredNow ? 'var(--gdim)' : '#000', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 9, fontWeight: 700, letterSpacing: '0.09em', textTransform: 'uppercase', cursor: data ? 'pointer' : 'default', opacity: data ? 1 : 0.5 }}>
                {data?.isMonitoredNow ? (justTracked ? '✓ Monitoring' : 'Monitoring') : 'Watch Wallet →'}
              </button>
            </div>

            <div style={{ maxWidth: 800, margin: '0 auto', padding: '20px 16px' }}>
              {!address && !loading && (
                <div style={{ textAlign: 'center', padding: '60px 20px' }}>
                  <div style={{ fontSize: 40, marginBottom: 16 }}>🔍</div>
                  <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 20, fontWeight: 700, color: 'var(--t0)', marginBottom: 8 }}>Wallet Intelligence</div>
                  <div style={{ fontSize: 12, color: 'var(--t1)', marginBottom: 24, lineHeight: 1.6 }}>Enter any Solana wallet address to view activity,<br />assess risk, and start monitoring.</div>
                  <div style={{ fontSize: 10, color: 'var(--t2)', marginBottom: 12 }}>Try a known wallet:</div>
                  <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
                    {[
                      { label: 'Solana Foundation', addr: 'mvines9iiHiQTysrwkJjGf2gb9Ex9jXJX8ns3qwf2kN' },
                      { label: 'Alameda Research', addr: 'CuieVDEDtLo7FypDy3rSJCJ9NyY6BPRYonGLqd5UYMF' },
                    ].map(w => (
                      <button key={w.addr} onClick={() => { setInputVal(w.addr); setAddress(w.addr); window.history.pushState({}, '', `/solintel/wallet?address=${w.addr}`) }} style={{ padding: '6px 12px', background: 'var(--s2)', border: '1px solid var(--b2)', color: 'var(--t1)', fontFamily: 'Space Mono, monospace', fontSize: 9, cursor: 'pointer' }}>
                        {w.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {loading && (
                <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--t1)', fontSize: 12 }}>
                  <div style={{ marginBottom: 8, color: 'var(--green)' }}>⟳</div>
                  Loading wallet data…
                </div>
              )}

              {error && (
                <div style={{ padding: '12px 16px', background: 'var(--rfaint)', border: '1px solid var(--red)', color: 'var(--red)', fontSize: 11, marginBottom: 16 }}>{error}</div>
              )}

              {data && !loading && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 4 }}>
                    <div>
                      <div style={{ fontSize: 9, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--t2)', marginBottom: 4 }}>// Wallet Intelligence — Analysis Entry Point</div>
                      <div style={{ fontFamily: 'Space Mono, monospace', fontSize: 16, fontWeight: 700, color: 'var(--t0)', marginBottom: 6 }}>
                        {data.address.slice(0, 8)}<span style={{ color: 'var(--t3)' }}>···</span>{data.address.slice(-6)}
                      </div>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <span style={{ fontSize: 9, letterSpacing: '0.08em', textTransform: 'uppercase', padding: '2px 7px', border: '1px solid rgba(0,255,135,0.3)', color: 'var(--gdim)', background: 'var(--gfaint)' }}>{typeLabel[data.walletType] || data.walletType}</span>
                        {data.isMonitoredNow && <span style={{ fontSize: 9, padding: '2px 7px', border: '1px solid var(--gdim)', color: 'var(--green)', background: 'var(--gfaint2)' }}>● Monitoring</span>}
                      </div>
                    </div>
                    <button onClick={handleMonitor} disabled={data.isMonitoredNow} style={{ padding: '8px 14px', background: data.isMonitoredNow ? 'var(--s2)' : 'var(--green)', color: data.isMonitoredNow ? 'var(--gdim)' : '#000', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 10, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', cursor: data.isMonitoredNow ? 'default' : 'pointer' }}>
                      {data.isMonitoredNow ? '✓ Monitoring' : 'Watch Wallet →'}
                    </button>
                  </div>

                  <div style={{ background: 'var(--s1)', border: '1px solid var(--b2)', padding: '20px 24px', display: 'flex', alignItems: 'center', gap: 24, position: 'relative', overflow: 'hidden' }}>
                    <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 3, background: riskColor(data.riskScore), boxShadow: `0 0 12px ${riskColor(data.riskScore)}` }} />
                    <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 56, fontWeight: 800, lineHeight: 1, color: riskColor(data.riskScore), textShadow: `0 0 20px ${riskColor(data.riskScore)}44`, minWidth: 80 }}>{data.riskScore}</div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 16, fontWeight: 700, color: 'var(--t0)', marginBottom: 4 }}>
                        {data.riskScore >= 70 ? 'Low Risk — Trusted Wallet' : data.riskScore >= 40 ? 'Medium Risk — Review Needed' : 'High Risk — Caution Required'}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--t1)', marginBottom: 12 }}>Based on on-chain activity and wallet behavior patterns</div>
                      <div style={{ display: 'flex', gap: 12 }}>
                        <div>
                          <div style={{ fontSize: 9, color: 'var(--t2)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>SOL Balance</div>
                          <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--t0)' }}>{data.balance.toFixed(2)} SOL</div>
                        </div>
                        <div>
                          <div style={{ fontSize: 9, color: 'var(--t2)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>USD Value</div>
                          <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--t0)' }}>${(data.balance * data.solPrice).toLocaleString('en-US', { maximumFractionDigits: 0 })}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: 9, color: 'var(--t2)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>Recent Txns</div>
                          <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--t0)' }}>{data.transactions.length}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--t1)', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                      <span style={{ display: 'inline-block', width: 3, height: 12, background: 'var(--green)' }} />
                      Recent Transactions
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {data.transactions.length === 0 ? (
                        <div style={{ padding: '12px 14px', background: 'var(--s1)', border: '1px solid var(--b1)', color: 'var(--t2)', fontSize: 11 }}>No recent transactions found.</div>
                      ) : (
                        data.transactions.map((tx: any, i: number) => (
                          <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', alignItems: 'center', gap: 12, padding: '10px 14px', background: 'var(--s1)', border: '1px solid var(--b1)' }}>
                            <div style={{ fontSize: 11, color: 'var(--t0)', fontFamily: 'Space Mono, monospace' }}>
                              {tx.signature ? `${tx.signature.slice(0, 8)}...` : `Txn #${i + 1}`}
                            </div>
                            <div style={{ fontSize: 10, color: 'var(--t1)' }}>
                              {tx.blockTime ? new Date(tx.blockTime * 1000).toLocaleString() : '—'}
                            </div>
                            <div style={{ fontSize: 10, color: tx.err === null ? 'var(--green)' : 'var(--red)' }}>
                              {tx.err === null ? 'Success' : 'Failed'}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {!data.isMonitoredNow && (
                    <div style={{ background: 'var(--gfaint2)', border: '1px solid rgba(0,255,135,0.2)', padding: '18px 20px' }}>
                      <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 14, fontWeight: 700, color: 'var(--t0)', marginBottom: 8 }}>Monitor This Wallet</div>
                      <div style={{ fontSize: 11, color: 'var(--t1)', lineHeight: 1.6, marginBottom: 14 }}>Get notified the moment this wallet makes a move.</div>
                      <ul style={{ listStyle: 'none', marginBottom: 16, display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {['Never miss a whale move', 'Alerts within seconds', 'Track unlimited wallets'].map(f => (
                          <li key={f} style={{ fontSize: 11, color: 'var(--t1)', display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span style={{ color: 'var(--green)', fontWeight: 700, fontSize: 10 }}>✓</span>{f}
                          </li>
                        ))}
                      </ul>
                      <button onClick={handleMonitor} style={{ width: '100%', background: 'var(--green)', color: '#000', border: 'none', padding: 10, fontFamily: 'Space Mono, monospace', fontSize: 11, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer' }}>
                        Start Monitoring — $11.99/mo
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
        <Statusbar />
      </div>
      <UpgradeModal open={upgradeOpen} onClose={() => setUpgradeOpen(false)} />
    </>
  )
}

export default function WalletPage() {
  return (
    <Suspense fallback={<div style={{ background: 'var(--bg)', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--t1)' }}>Loading…</div>}>
      <WalletContent />
    </Suspense>
  )
}
