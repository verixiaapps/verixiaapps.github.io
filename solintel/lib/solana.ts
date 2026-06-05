// lib/solana.ts
// All RPC calls proxied through awake-integrity backend (Helius-backed)
// SOL price via Jupiter lite-api (public, no key needed)

const API = 'https://awake-integrity-production-faa0.up.railway.app'
const JUPITER_PRICE = 'https://lite-api.jup.ag/price/v3'
const SOL_MINT = 'So11111111111111111111111111111111111111112'

async function rpc(method: string, params: any[]): Promise<any> {
  const res = await fetch(`${API}/wallet/rpc`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
  })
  const data = await res.json()
  if (data?.error) throw new Error(data.error.message || 'RPC error')
  return data?.result
}

export async function getAccountInfo(address: string) {
  const result = await rpc('getAccountInfo', [address, { encoding: 'jsonParsed' }])
  return result?.value || null
}

export async function getBalance(address: string): Promise<number> {
  const result = await rpc('getBalance', [address])
  return (result?.value || 0) / 1e9
}

export async function getSignaturesForAddress(address: string, limit = 10) {
  const result = await rpc('getSignaturesForAddress', [address, { limit }])
  return result || []
}

export async function getTransaction(signature: string) {
  const result = await rpc('getTransaction', [
    signature,
    { encoding: 'jsonParsed', maxSupportedTransactionVersion: 0 },
  ])
  return result || null
}

export async function getWalletTokens(address: string) {
  try {
    const res = await fetch(`${API}/wallet/rpc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'getAssetsByOwner',
        params: {
          ownerAddress: address,
          page: 1,
          limit: 50,
          displayOptions: { showFungible: true, showNativeBalance: true },
        },
      }),
    })
    const data = await res.json()
    return data?.result?.items || []
  } catch {
    return []
  }
}

export async function getWalletTransactions(address: string, limit = 20) {
  try {
    return await getSignaturesForAddress(address, limit)
  } catch {
    return []
  }
}

export async function getSolPrice(): Promise<number> {
  try {
    const res = await fetch(`${JUPITER_PRICE}?ids=${SOL_MINT}`)
    const data = await res.json()
    return Number(data?.[SOL_MINT]?.usdPrice || 0)
  } catch {
    return 0
  }
}

export function isValidSolanaAddress(address: string): boolean {
  return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address.trim())
}

export function shortenAddress(address: string, chars = 4): string {
  return `${address.slice(0, chars)}...${address.slice(-chars)}`
}

export function classifyWallet(balance: number, txCount: number) {
  if (balance > 100000) return 'whale'
  if (balance > 10000) return 'large'
  if (txCount > 1000) return 'active'
  if (txCount > 100) return 'regular'
  return 'small'
}

export function computeRiskScore(data: {
  balance: number
  txCount: number
  tokenCount: number
  ageInDays: number
}): number {
  let score = 50
  if (data.ageInDays > 365) score += 15
  else if (data.ageInDays > 90) score += 8
  if (data.txCount > 500) score += 10
  else if (data.txCount > 100) score += 5
  if (data.balance > 1000) score += 10
  if (data.tokenCount > 10) score += 5
  return Math.min(100, Math.max(0, score))
}

export interface FeedEvent {
  id: string
  type: 'whale_buy' | 'whale_sell' | 'smart_entry' | 'smart_exit' | 'treasury' | 'governance'
  title: string
  detail: string
  amount?: string
  address?: string
  timestamp: number
  isNew?: boolean
}

export function generateFeedEvents(): FeedEvent[] {
  const now = Date.now()
  return [
    {
      id: '1',
      type: 'whale_buy',
      title: 'Whale accumulated 85,000 SOL',
      detail: 'Unknown wallet acquired $15.4M SOL across 3 transactions via Jupiter',
      amount: '$15.4M',
      address: '9aRK...3vNz',
      timestamp: now - 2 * 60 * 1000,
      isNew: true,
    },
    {
      id: '2',
      type: 'smart_entry',
      title: 'Smart wallet entered $840K JUP position',
      detail: 'Top-ranked wallet (71% win rate) accumulated 1.18M JUP via DCA over 90 min',
      amount: '$840K',
      address: '7xKX...gAs2',
      timestamp: now - 14 * 60 * 1000,
      isNew: true,
    },
    {
      id: '3',
      type: 'treasury',
      title: 'Solana Foundation moved $4.2M USDC',
      detail: 'Foundation treasury transferred to new 3-of-5 multisig created 4 days ago',
      amount: '$4.2M',
      address: 'SoLF...n7Ap',
      timestamp: now - 38 * 60 * 1000,
    },
    {
      id: '4',
      type: 'smart_exit',
      title: 'High-performance wallet fully exited BONK',
      detail: 'Wallet with 84% win rate sold entire $1.2M position — held since Q3 2023',
      amount: '$1.2M',
      address: 'BzWq...7dYc',
      timestamp: now - 3 * 60 * 60 * 1000,
    },
    {
      id: '5',
      type: 'whale_buy',
      title: 'Whale accumulated 42,000 SOL',
      detail: 'Largest single SOL purchase in 72 hours — new wallet, first transaction',
      amount: '$7.6M',
      address: 'D4kL...9mPq',
      timestamp: now - 5 * 60 * 60 * 1000,
    },
    {
      id: '6',
      type: 'whale_sell',
      title: 'Large SOL position exited',
      detail: '22,000 SOL moved to Binance — likely OTC or fiat off-ramp',
      amount: '$4.0M',
      address: 'Kp9M...2xRt',
      timestamp: now - 7 * 60 * 60 * 1000,
    },
  ]
}
