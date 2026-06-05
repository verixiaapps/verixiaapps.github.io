'use client'

import { useState } from 'react'
import Topbar from '../../components/layout/Topbar'
import LeftPanel from '../../components/layout/LeftPanel'
import Statusbar from '../../components/layout/Statusbar'
import UpgradeModal from '../../components/ui/UpgradeModal'

const PLANS = [
  {
    key: 'weekly',
    name: 'Weekly',
    price: '$3.99',
    period: '/week',
    description: 'Try it with no commitment',
    features: [
      { text: 'Unlimited wallets monitored', included: true },
      { text: 'Unlimited watchlists', included: true },
      { text: 'Full intelligence feed', included: true },
      { text: 'Real-time alerts', included: true },
      { text: 'Smart money tracking', included: true },
      { text: 'Treasury monitoring', included: true },
      { text: 'Governance alerts', included: true },
      { text: 'Cancel anytime', included: true },
    ],
    cta: 'Try It Weekly',
    ctaStyle: { background: 'rgba(0,255,135,0.10)', border: '1px solid rgba(0,255,135,0.22)', color: 'var(--green)' },
    highlight: false,
    badge: 'Try It',
  },
  {
    key: 'monthly',
    name: 'Monthly',
    price: '$11.99',
    period: '/month',
    description: 'For active Solana participants',
    features: [
      { text: 'Unlimited wallets monitored', included: true },
      { text: 'Unlimited watchlists', included: true },
      { text: 'Full intelligence feed', included: true },
      { text: 'Real-time alerts', included: true },
      { text: 'Smart money tracking', included: true },
      { text: 'Treasury monitoring', included: true },
      { text: 'Governance alerts', included: true },
      { text: 'Cancel anytime', included: true },
    ],
    cta: 'Start Monitoring',
    ctaStyle: { background: 'rgba(153,69,255,0.22)', border: '1px solid rgba(153,69,255,0.40)', color: '#c4a8ff' },
    highlight: false,
    badge: 'Popular',
  },
  {
    key: 'yearly',
    name: 'Yearly',
    price: '$39.99',
    period: '/year',
    description: 'Best value — under $4/mo',
    features: [
      { text: 'Unlimited wallets monitored', included: true },
      { text: 'Unlimited watchlists', included: true },
      { text: 'Full intelligence feed', included: true },
      { text: 'Real-time alerts', included: true },
      { text: 'Smart money tracking', included: true },
      { text: 'Treasury monitoring', included: true },
      { text: 'Governance alerts', included: true },
      { text: 'Save 80% vs weekly', included: true },
    ],
    cta: 'Get Best Value',
    ctaStyle: { background: 'var(--green)', border: 'none', color: '#000' },
    highlight: true,
    badge: 'Save 80%',
  },
]

export default function PricingPage() {
  const [upgradeOpen, setUpgradeOpen] = useState(false)
  const [defaultPlan, setDefaultPlan] = useState('monthly')

  function openPlan(key: string) {
    setDefaultPlan(key)
    setUpgradeOpen(true)
  }

  return (
    <>
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Topbar />
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          <LeftPanel />
          <div style={{ flex: 1, overflowY: 'auto' }}>
            <div style={{ maxWidth: 860, margin: '0 auto', padding: '40px 20px 60px' }}>

              <div style={{ textAlign: 'center', marginBottom: 40 }}>
                <div style={{ fontSize: 9, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--gdim)', marginBottom: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                  <div className="live-dot" />Monitoring Plans
                </div>
                <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: 36, fontWeight: 800, color: 'var(--t0)', letterSpacing: '-0.04em', lineHeight: 1.1, marginBottom: 12 }}>
                  Never Miss an Important<br />Solana Event Again
                </h1>
                <p style={{ fontSize: 13, color: 'var(--t1)', lineHeight: 1.6, maxWidth: 480, margin: '0 auto' }}>
                  Monitor wallets, get real-time alerts, track smart money, governance, and treasury activity. Cancel anytime.
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 40 }}>
                {PLANS.map(plan => (
                  <div key={plan.key} style={{ padding: '24px 20px', borderRadius: 4, border: plan.highlight ? '1.5px solid rgba(0,255,135,0.40)' : '1px solid var(--b2)', background: plan.highlight ? 'linear-gradient(135deg, rgba(0,255,135,0.07), rgba(0,0,0,0))' : 'var(--s1)', position: 'relative', display: 'flex', flexDirection: 'column' }}>
                    {plan.badge && (
                      <div style={{ position: 'absolute', top: -10, left: '50%', transform: 'translateX(-50%)', fontSize: 8, fontWeight: 700, padding: '2px 10px', borderRadius: 999, letterSpacing: '0.08em', whiteSpace: 'nowrap', ...(plan.key === 'yearly' ? { background: 'linear-gradient(135deg, var(--green), #00e87a)', color: '#020508' } : plan.key === 'monthly' ? { background: 'rgba(153,69,255,0.22)', color: '#c4a8ff', border: '1px solid rgba(153,69,255,0.40)' } : { background: 'rgba(0,255,135,0.10)', color: 'var(--green)', border: '1px solid rgba(0,255,135,0.22)' }) }}>
                        {plan.badge}
                      </div>
                    )}
                    <div style={{ fontSize: 8, letterSpacing: '0.14em', textTransform: 'uppercase', color: plan.highlight ? 'var(--gdim)' : 'var(--t2)', marginBottom: 8 }}>{plan.name}</div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 4 }}>
                      <span style={{ fontFamily: 'Syne, sans-serif', fontSize: 32, fontWeight: 800, color: plan.highlight ? 'var(--green)' : 'var(--t0)', lineHeight: 1 }}>{plan.price}</span>
                      <span style={{ fontSize: 11, color: 'var(--t2)' }}>{plan.period}</span>
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--t1)', marginBottom: 20, lineHeight: 1.4 }}>{plan.description}</div>
                    <ul style={{ listStyle: 'none', flex: 1, marginBottom: 20, display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {plan.features.map(f => (
                        <li key={f.text} style={{ fontSize: 11, color: f.included ? 'var(--t1)' : 'var(--t3)', display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                          <span style={{ color: f.included ? 'var(--green)' : 'var(--t3)', flexShrink: 0, fontSize: 10 }}>{f.included ? '✓' : '–'}</span>
                          {f.text}
                        </li>
                      ))}
                    </ul>
                    <button onClick={() => openPlan(plan.key)} style={{ width: '100%', padding: '10px', fontFamily: 'Space Mono, monospace', fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer', transition: 'all 0.15s', ...plan.ctaStyle }}>
                      {plan.cta}
                    </button>
                  </div>
                ))}
              </div>

              <div style={{ borderTop: '1px solid var(--b1)', paddingTop: 32 }}>
                <div style={{ textAlign: 'center', marginBottom: 24, fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--t2)' }}>Common Questions</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, maxWidth: 700, margin: '0 auto' }}>
                  {[
                    { q: 'What counts as a monitored wallet?', a: "Any Solana wallet address you add to your watchlist. You'll receive alerts whenever it makes a significant move." },
                    { q: 'How fast are real-time alerts?', a: 'Paid plan alerts fire within seconds of an on-chain event being confirmed. Free plan alerts are delayed 60 minutes.' },
                    { q: 'Can I cancel anytime?', a: 'Yes. Cancel from your account at any time. Your access continues until the end of the billing period.' },
                    { q: 'What data sources do you use?', a: 'Helius RPC and Jupiter price feeds — industry-standard Solana infrastructure. All data is fully verifiable on-chain.' },
                  ].map(item => (
                    <div key={item.q} style={{ padding: '14px', background: 'var(--s1)', border: '1px solid var(--b1)' }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--t0)', marginBottom: 6 }}>{item.q}</div>
                      <div style={{ fontSize: 10, color: 'var(--t1)', lineHeight: 1.6 }}>{item.a}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ marginTop: 24, display: 'flex', justifyContent: 'center', gap: 24, flexWrap: 'wrap' }}>
                {['Stripe Secured', 'Cancel Anytime', 'No Hidden Fees', 'Helius-Powered'].map(t => (
                  <span key={t} style={{ fontSize: 9, color: 'var(--t2)', letterSpacing: '0.08em', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ color: 'var(--gdim)' }}>✓</span> {t}
                  </span>
                ))}
              </div>

            </div>
          </div>
        </div>
        <Statusbar />
      </div>
      <UpgradeModal open={upgradeOpen} onClose={() => setUpgradeOpen(false)} defaultPlan={defaultPlan} />
    </>
  )
}
