'use client'

import { useState, useEffect, useRef } from 'react'
import { loadStripe } from '@stripe/stripe-js'
import { markSubscribed, setVerifiedEmail, restoreByEmail } from '../../../solintel/lib/subscription'

const API = 'https://awake-integrity-production-faa0.up.railway.app'
const STRIPE_KEY = 'pk_live_51T83ANJjMzyHDzeQlrggekWLypSX5CUd01DW8gCqjo32KnKrDsdDtg61CbbrJUzMF82T4z5INGWROuLMlIfp1zKE00oMYmW08Y'

const PLANS = [
  {
    key: 'yearly',
    label: 'Best Value',
    price: '$39.99/yr',
    sub: 'under $4/mo',
    priceId: 'price_1T8KOQJjMzyHDzeQfcU1C1MQ',
    features: ['Unlimited wallets monitored', 'Real-time alerts', 'Unlimited watchlists', 'All alert types', 'Priority support'],
    badge: 'Save 80%',
    badgeStyle: { background: 'linear-gradient(135deg, #00ff87, #00e87a)', color: '#020508' },
  },
  {
    key: 'monthly',
    label: 'Monthly',
    price: '$11.99/mo',
    sub: 'cancel anytime',
    priceId: 'price_1T8KOUJjMzyHDzeQxaqPFOSB',
    features: ['Unlimited wallets monitored', 'Real-time alerts', 'Unlimited watchlists', 'All alert types'],
    badge: 'Popular',
    badgeStyle: { background: 'rgba(153,69,255,0.22)', color: '#c4a8ff', border: '1px solid rgba(153,69,255,0.30)' },
  },
  {
    key: 'weekly',
    label: 'Try It',
    price: '$3.99/wk',
    sub: 'no commitment',
    priceId: 'price_1T8KOTJjMzyHDzeQDDg1A2TF',
    features: ['Full access', 'Cancel anytime', 'No long-term commitment'],
    badge: 'Try It',
    badgeStyle: { background: 'rgba(0,255,135,0.10)', color: 'var(--green)', border: '1px solid rgba(0,255,135,0.22)' },
  },
]

type View = 'plans' | 'checkout' | 'restore'

interface Props {
  open: boolean
  onClose: () => void
  defaultPlan?: string
  onSubscribed?: () => void
}

export default function UpgradeModal({ open, onClose, defaultPlan = 'monthly', onSubscribed }: Props) {
  const [view, setView] = useState<View>('plans')
  const [selectedPlan, setSelectedPlan] = useState(defaultPlan)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const mountRef = useRef<HTMLDivElement>(null)
  const checkoutRef = useRef<{ destroy: () => void } | null>(null)
  const [restoreEmail, setRestoreEmail] = useState('')
  const [restoreStatus, setRestoreStatus] = useState<'idle' | 'loading' | 'success' | 'notfound' | 'error'>('idle')

  useEffect(() => {
    if (!open) {
      destroyCheckout()
      setView('plans')
      setLoading(false)
      setError('')
      setRestoreEmail('')
      setRestoreStatus('idle')
    }
  }, [open])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('solintel_subscribed') === 'true') {
      const plan = (params.get('plan') || 'monthly') as any
      markSubscribed(plan)
      window.history.replaceState({}, document.title, window.location.pathname)
      onSubscribed?.()
    }
  }, [])

  async function destroyCheckout() {
    if (checkoutRef.current) {
      try { await checkoutRef.current.destroy() } catch {}
      checkoutRef.current = null
    }
    if (mountRef.current) mountRef.current.innerHTML = ''
  }

  async function openCheckout(planKey: string) {
    const plan = PLANS.find(p => p.key === planKey)
    if (!plan?.priceId) return
    setLoading(true)
    setError('')
    setView('checkout')
    try {
      await destroyCheckout()
      const stripe = await loadStripe(STRIPE_KEY)
      if (!stripe) throw new Error('Stripe failed to load')
      const fetchClientSecret = async () => {
        const res = await fetch(`${API}/create-embedded-subscription`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            priceId: plan.priceId,
            returnUrl: `${window.location.origin}${window.location.pathname}?solintel_subscribed=true&plan=${planKey}`,
          }),
        })
        const data = await res.json()
        if (!data?.clientSecret) throw new Error('No client secret returned')
        return data.clientSecret
      }
      const checkout = await (stripe as any).initEmbeddedCheckout({ fetchClientSecret })
      checkoutRef.current = checkout
      if (mountRef.current) checkout.mount(mountRef.current)
    } catch (e) {
      setError('Could not load checkout. Please try again.')
      setView('plans')
    } finally {
      setLoading(false)
    }
  }

  async function handleRestore() {
    if (!restoreEmail.trim()) return
    setRestoreStatus('loading')
    setError('')
    const result = await restoreByEmail(restoreEmail.trim())
    if (result === 'active') {
      setVerifiedEmail(restoreEmail.trim())
      setRestoreStatus('success')
      setTimeout(() => { onSubscribed?.(); onClose() }, 1500)
    } else if (result === 'not_found') {
      setRestoreStatus('notfound')
    } else {
      setRestoreStatus('error')
    }
  }

  if (!open) return null

  return (
    <div
      style={{ position: 'fixed', inset: 0, zIndex: 500, background: 'rgba(0,0,0,0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div style={{ background: 'linear-gradient(180deg, rgba(6,12,26,0.98) 0%, rgba(2,5,8,0.99) 100%)', border: '1px solid rgba(0,255,135,0.14)', borderRadius: 4, padding: 24, maxWidth: 560, width: '100%', boxShadow: '0 0 32px rgba(0,255,135,0.10), 0 22px 56px rgba(0,0,0,0.60)', maxHeight: '90vh', overflowY: 'auto' }}>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div>
            <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 20, fontWeight: 800, color: 'var(--t0)', marginBottom: 4 }}>
              {view === 'restore' ? 'Restore Access' : 'Never Miss an Important Solana Event'}
            </div>
            <div style={{ fontSize: 12, color: 'var(--t1)', lineHeight: 1.5 }}>
              {view === 'restore' ? 'Enter the email you used at checkout to restore your subscription.' : 'Monitor wallets, get real-time alerts, track what matters.'}
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--t2)', fontSize: 20, cursor: 'pointer', padding: '0 0 0 16px', flexShrink: 0 }}>×</button>
        </div>

        {view === 'plans' && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, margin: '0 0 12px' }}>
              {PLANS.map(plan => (
                <div key={plan.key} onClick={() => setSelectedPlan(plan.key)} style={{ padding: '13px 12px', border: selectedPlan === plan.key ? '1.5px solid rgba(0,255,135,0.46)' : '1px solid var(--b2)', background: selectedPlan === plan.key ? 'linear-gradient(135deg, rgba(0,255,135,0.09), rgba(0,0,0,0))' : 'rgba(255,255,255,0.03)', cursor: 'pointer', transition: 'all 0.12s' }}>
                  <div style={{ marginBottom: 4 }}><span style={{ fontSize: 8, fontWeight: 700, padding: '2px 7px', borderRadius: 999, ...plan.badgeStyle }}>{plan.badge}</span></div>
                  <div style={{ fontSize: 13, fontWeight: 900, color: selectedPlan === plan.key ? 'var(--green)' : 'var(--t0)', marginBottom: 2 }}>{plan.label}</div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--t0)' }}>{plan.price}</div>
                  <div style={{ fontSize: 10, color: 'var(--t2)', marginBottom: 8 }}>{plan.sub}</div>
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 4 }}>
                    {plan.features.map(f => (
                      <li key={f} style={{ fontSize: 10, color: 'var(--t1)', display: 'flex', gap: 5 }}><span style={{ color: 'var(--gdim)' }}>✓</span> {f}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
            <button onClick={() => openCheckout(selectedPlan)} disabled={loading} style={{ width: '100%', background: 'var(--green)', color: '#000', border: 'none', padding: '12px', fontFamily: 'Space Mono, monospace', fontSize: 11, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: loading ? 'wait' : 'pointer', opacity: loading ? 0.7 : 1, marginBottom: 10 }}>
              {loading ? 'Loading...' : `Start Monitoring — ${PLANS.find(p => p.key === selectedPlan)?.price}`}
            </button>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 16, fontSize: 9, color: 'var(--t2)', marginBottom: 12 }}>
              <span>Stripe secured</span><span>Cancel anytime</span><span>No hidden fees</span>
            </div>
            <div style={{ textAlign: 'center' }}>
              <button onClick={() => { setView('restore'); setRestoreStatus('idle'); setError('') }} style={{ background: 'none', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 10, color: 'var(--t2)', cursor: 'pointer', letterSpacing: '0.06em', textDecoration: 'underline', textDecorationColor: 'var(--b2)' }}>
                Already subscribed? Restore access →
              </button>
            </div>
            {error && <div style={{ marginTop: 8, fontSize: 11, color: 'var(--red)', textAlign: 'center' }}>{error}</div>}
          </>
        )}

        {view === 'checkout' && (
          <>
            <div style={{ fontSize: 11, color: 'var(--t1)', marginBottom: 12 }}>Complete payment below to start monitoring.</div>
            <div ref={mountRef} style={{ minHeight: 400, borderRadius: 4, overflow: 'hidden', display: 'block' }} />
            <button onClick={() => { destroyCheckout(); setView('plans') }} style={{ marginTop: 10, padding: '7px 12px', border: '1px solid var(--b2)', background: 'rgba(255,255,255,0.04)', color: 'var(--t1)', fontSize: 11, cursor: 'pointer', fontFamily: 'Space Mono, monospace' }}>← Back to plans</button>
          </>
        )}

        {view === 'restore' && (
          <>
            {restoreStatus === 'success' ? (
              <div style={{ padding: '16px', background: 'var(--gfaint2)', border: '1px solid rgba(0,255,135,0.2)', textAlign: 'center' }}>
                <div style={{ fontSize: 20, marginBottom: 8 }}>✓</div>
                <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 14, fontWeight: 700, color: 'var(--green)', marginBottom: 4 }}>Subscription restored</div>
                <div style={{ fontSize: 11, color: 'var(--t1)' }}>Your access has been unlocked. Closing…</div>
              </div>
            ) : (
              <>
                <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
                  <input type="email" value={restoreEmail} onChange={e => { setRestoreEmail(e.target.value); setRestoreStatus('idle') }} onKeyDown={e => e.key === 'Enter' && handleRestore()} placeholder="Payment email address…" style={{ flex: 1, background: 'var(--s2)', border: '1px solid var(--b2)', color: 'var(--t0)', padding: '10px 12px', fontFamily: 'Space Mono, monospace', fontSize: 12, outline: 'none' }} />
                  <button onClick={handleRestore} disabled={restoreStatus === 'loading' || !restoreEmail.trim()} style={{ padding: '10px 16px', background: 'var(--green)', color: '#000', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: restoreStatus === 'loading' ? 'wait' : 'pointer', opacity: restoreStatus === 'loading' || !restoreEmail.trim() ? 0.6 : 1, flexShrink: 0 }}>
                    {restoreStatus === 'loading' ? '...' : 'Restore'}
                  </button>
                </div>
                {restoreStatus === 'notfound' && <div style={{ fontSize: 11, color: 'var(--yel)', marginBottom: 8 }}>No active subscription found for that email. Check the address or subscribe below.</div>}
                {restoreStatus === 'error' && <div style={{ fontSize: 11, color: 'var(--red)', marginBottom: 8 }}>Could not check subscription. Please try again.</div>}
                <div style={{ fontSize: 10, color: 'var(--t2)', lineHeight: 1.6, marginBottom: 12 }}>Enter the email you used at Stripe checkout. Access is verified against your active subscription and stored locally on this device.</div>
                <button onClick={() => setView('plans')} style={{ background: 'none', border: 'none', fontFamily: 'Space Mono, monospace', fontSize: 10, color: 'var(--t2)', cursor: 'pointer', letterSpacing: '0.06em' }}>← Back to plans</button>
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
