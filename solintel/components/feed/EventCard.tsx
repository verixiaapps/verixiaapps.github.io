'use client'

import type { FeedEvent } from '../../lib/solana'

const TYPE_CONFIG = {
  whale_buy:    { label: 'Whale Buy',            chip: 'etc-g', stripe: 'var(--green)', icon: '🐋', cta: 'Track Wallet' },
  whale_sell:   { label: 'Whale Sell',           chip: 'etc-r', stripe: 'var(--red)',   icon: '⚠️', cta: 'Track Wallet' },
  smart_entry:  { label: 'Smart Money Entry',    chip: 'etc-g', stripe: 'var(--green)', icon: '💡', cta: 'Follow Wallet' },
  smart_exit:   { label: 'Smart Money Exit',     chip: 'etc-r', stripe: 'var(--red)',   icon: '⚠️', cta: 'Track Wallet' },
  treasury:     { label: 'Treasury Movement',    chip: 'etc-b', stripe: 'var(--blu)',   icon: '🏦', cta: 'Watch Treasury' },
  governance:   { label: 'Governance',           chip: 'etc-y', stripe: 'var(--yel)',   icon: '🏛', cta: 'Follow Proposal' },
}

const CHIP_COLORS: Record<string, { bg: string; color: string; border: string }> = {
  'etc-g': { bg: 'var(--gfaint2)', color: 'var(--green)', border: 'rgba(0,255,135,0.2)' },
  'etc-r': { bg: 'var(--rfaint)',  color: 'var(--red)',   border: 'rgba(255,61,85,0.2)' },
  'etc-y': { bg: 'var(--yfaint)',  color: 'var(--yel)',   border: 'rgba(240,191,48,0.2)' },
  'etc-b': { bg: 'var(--bfaint)',  color: 'var(--blu)',   border: 'rgba(61,159,255,0.2)' },
  'etc-o': { bg: 'var(--ofaint)',  color: 'var(--ora)',   border: 'rgba(255,112,48,0.2)' },
}

function timeAgo(ts: number): string {
  const diff = Date.now() - ts
  const min = Math.floor(diff / 60000)
  const hr = Math.floor(diff / 3600000)
  if (min < 1) return 'just now'
  if (min < 60) return `${min} min ago`
  return `${hr} hr ago`
}

interface Props {
  event: FeedEvent
  delay?: number
  onTrack?: (address: string) => void
}

export default function EventCard({ event, delay = 0, onTrack }: Props) {
  const cfg = TYPE_CONFIG[event.type]
  const chipCfg = CHIP_COLORS[cfg.chip]

  return (
    <div
      className="animate-slidein"
      style={{ display: 'grid', gridTemplateColumns: '4px 1fr', borderBottom: '1px solid var(--b1)', cursor: 'pointer', background: event.isNew ? 'var(--gfaint)' : 'transparent', animationDelay: `${delay}s`, transition: 'background 0.1s' }}
      onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'var(--s2)' }}
      onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = event.isNew ? 'var(--gfaint)' : 'transparent' }}
    >
      <div style={{ background: cfg.stripe, flexShrink: 0 }} />

      <div style={{ display: 'grid', gridTemplateColumns: '52px 1fr auto', padding: 0 }}>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '16px 0 16px 14px' }}>
          <div style={{ width: 36, height: 36, borderRadius: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, background: chipCfg.bg, boxShadow: event.isNew ? `0 0 16px ${chipCfg.color}22` : 'none' }}>
            {cfg.icon}
          </div>
        </div>

        <div style={{ padding: '14px 14px 14px 10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
            <span style={{ fontSize: 8, letterSpacing: '0.14em', textTransform: 'uppercase', padding: '2px 7px', fontWeight: 700, borderRadius: 1, background: chipCfg.bg, color: chipCfg.color, border: `1px solid ${chipCfg.border}` }}>
              {cfg.label}
            </span>
            {event.isNew && (
              <span style={{ fontSize: 8, fontWeight: 700, letterSpacing: '0.08em', background: 'var(--green)', color: '#000', padding: '2px 6px', animation: 'flash 1.5s ease 3' }}>
                New
              </span>
            )}
          </div>

          <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 14, fontWeight: 700, color: 'var(--t0)', lineHeight: 1.3, marginBottom: 6 }}>
            {event.title}
          </div>

          {event.amount && (
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 5, margin: '8px 0 6px' }}>
              <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 20, fontWeight: 800, lineHeight: 1, color: event.type.includes('sell') || event.type === 'smart_exit' ? 'var(--red)' : 'var(--green)', textShadow: event.type.includes('sell') ? '0 0 20px rgba(255,61,85,0.2)' : '0 0 20px rgba(0,255,135,0.3)' }}>
                {event.amount}
              </div>
              {event.address && (
                <div style={{ fontSize: 10, color: 'var(--t1)' }}>· {event.address}</div>
              )}
            </div>
          )}

          <div style={{ fontSize: 10, color: 'var(--t1)', lineHeight: 1.6 }}>{event.detail}</div>
        </div>

        <div style={{ padding: '14px 14px 14px 0', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'space-between', minWidth: 90 }}>
          <div style={{ fontSize: 9, color: 'var(--t2)' }}>{timeAgo(event.timestamp)}</div>
          <button
            onClick={() => event.address && onTrack?.(event.address)}
            style={{ fontSize: 8, letterSpacing: '0.09em', textTransform: 'uppercase', border: '1px solid var(--b2)', padding: '4px 9px', color: 'var(--t2)', background: 'transparent', cursor: 'pointer', fontFamily: 'Space Mono, monospace', transition: 'all 0.1s' }}
            onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--green)'; (e.currentTarget as HTMLElement).style.color = 'var(--green)' }}
            onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--b2)'; (e.currentTarget as HTMLElement).style.color = 'var(--t2)' }}
          >
            {cfg.cta}
          </button>
        </div>
      </div>
    </div>
  )
}
