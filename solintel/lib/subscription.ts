// lib/subscription.ts
// Mirrors Verixia's localStorage subscription pattern + email restore

const API = 'https://awake-integrity-production-faa0.up.railway.app'

export const KEYS = {
  subscribed: 'solintel_subscribed',
  email: 'solintel_verified_email',
  plan: 'solintel_plan',
  monitored: 'solintel_monitored_wallets',
  watchlists: 'solintel_watchlists',
  alerts: 'solintel_alerts',
}

export const PLANS = {
  free: {
    name: 'Free',
    maxWallets: 3,
    maxWatchlists: 1,
    alertDelay: 60,
    realTimeAlerts: false,
    price: 0,
  },
  weekly: {
    name: 'Weekly',
    maxWallets: 999,
    maxWatchlists: 999,
    alertDelay: 0,
    realTimeAlerts: true,
    price: 3.99,
    priceId: 'price_1T8KOTJjMzyHDzeQDDg1A2TF',
  },
  monthly: {
    name: 'Monthly',
    maxWallets: 999,
    maxWatchlists: 999,
    alertDelay: 0,
    realTimeAlerts: true,
    price: 11.99,
    priceId: 'price_1T8KOUJjMzyHDzeQxaqPFOSB',
  },
  yearly: {
    name: 'Yearly',
    maxWallets: 999,
    maxWatchlists: 999,
    alertDelay: 0,
    realTimeAlerts: true,
    price: 39.99,
    priceId: 'price_1T8KOQJjMzyHDzeQfcU1C1MQ',
  },
}

export type PlanKey = keyof typeof PLANS

export function isSubscribed(): boolean {
  if (typeof window === 'undefined') return false
  return localStorage.getItem(KEYS.subscribed) === 'true'
}

export function getPlan(): PlanKey {
  if (typeof window === 'undefined') return 'free'
  if (!isSubscribed()) return 'free'
  return (localStorage.getItem(KEYS.plan) as PlanKey) || 'monthly'
}

export function getPlanLimits() {
  return PLANS[getPlan()]
}

export function markSubscribed(planKey: PlanKey = 'monthly') {
  localStorage.setItem(KEYS.subscribed, 'true')
  localStorage.setItem(KEYS.plan, planKey)
}

export function markUnsubscribed() {
  localStorage.removeItem(KEYS.subscribed)
  localStorage.removeItem(KEYS.plan)
}

export function getVerifiedEmail(): string {
  if (typeof window === 'undefined') return ''
  return localStorage.getItem(KEYS.email) || ''
}

export function setVerifiedEmail(email: string) {
  localStorage.setItem(KEYS.email, email.trim().toLowerCase())
}

export async function restoreByEmail(email: string): Promise<'active' | 'not_found' | 'error'> {
  if (!email) return 'error'
  const normalised = email.trim().toLowerCase()

  try {
    const res = await fetch(`${API}/analyze-token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        email: normalised,
        subscribed: false,
      }),
    })

    const data = await res.json()

    if (data?.subscriber === true) {
      markSubscribed('monthly')
      setVerifiedEmail(normalised)
      return 'active'
    }

    if (data?.limit === true) return 'not_found'
    if (data?.subscriber === false) return 'not_found'

    return 'error'
  } catch {
    return 'error'
  }
}

export function getMonitoredWallets(): string[] {
  if (typeof window === 'undefined') return []
  try {
    return JSON.parse(localStorage.getItem(KEYS.monitored) || '[]')
  } catch {
    return []
  }
}

export function addMonitoredWallet(address: string): boolean {
  const wallets = getMonitoredWallets()
  const limits = getPlanLimits()
  if (wallets.includes(address)) return true
  if (wallets.length >= limits.maxWallets) return false
  wallets.push(address)
  localStorage.setItem(KEYS.monitored, JSON.stringify(wallets))
  return true
}

export function removeMonitoredWallet(address: string) {
  const wallets = getMonitoredWallets().filter(w => w !== address)
  localStorage.setItem(KEYS.monitored, JSON.stringify(wallets))
}

export function isMonitored(address: string): boolean {
  return getMonitoredWallets().includes(address)
}

export interface Watchlist {
  id: string
  name: string
  wallets: string[]
  createdAt: number
}

export function getWatchlists(): Watchlist[] {
  if (typeof window === 'undefined') return []
  try {
    return JSON.parse(localStorage.getItem(KEYS.watchlists) || '[]')
  } catch {
    return []
  }
}

export function addWatchlist(name: string): Watchlist | null {
  const lists = getWatchlists()
  const limits = getPlanLimits()
  if (lists.length >= limits.maxWatchlists) return null
  const wl: Watchlist = {
    id: Date.now().toString(),
    name,
    wallets: [],
    createdAt: Date.now(),
  }
  lists.push(wl)
  localStorage.setItem(KEYS.watchlists, JSON.stringify(lists))
  return wl
}

export function addWalletToWatchlist(listId: string, address: string) {
  const lists = getWatchlists()
  const list = lists.find(l => l.id === listId)
  if (!list || list.wallets.includes(address)) return
  list.wallets.push(address)
  localStorage.setItem(KEYS.watchlists, JSON.stringify(lists))
}
