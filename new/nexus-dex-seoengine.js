import fetch from "node-fetch";
/*
// TOKEN RISK + DEX AGGREGATOR SEO ENGINE -- v12.0
//
// What changed from v11.0:
// 1. EXTERNAL APIS REMOVED: All CoinGecko and DexScreener calls eliminated.
//    Context is now built locally from intent-specific lookup tables --
//    same architecture as the scam check engine. Zero external HTTP calls.
//
// 2. LOCAL CONTEXT BUILDER: buildLocalCryptoContext() replaces fetchCryptoContext().
//    Returns rich, intent-specific structural details, mechanics examples,
//    and consequence patterns -- all deterministic, all in-process.
//
// 3. DETERMINISTIC PASS VARIATION: buildPassVariation() uses stableHash() +
//    passIndex to give each of the two passes a genuinely different structural
//    angle -- different entry point, different composition shape, different
//    reference anchors. Temperature variation alone wasn't enough.
//
// 4. TWO PASSES, BEST WINS: Both passes run in parallel. Only valid candidates
//    are eligible. Best valid score wins. Hard throw if neither pass is valid.
//    No fallback to invalid content. No generic content ever served.
*/

/* =========================
   CONFIG
   ========================= */

const OPENAI_MODEL = process.env.OPENAI_SEO_MODEL || "gpt-4.1-mini";
const OPENAI_API_URL =
  process.env.OPENAI_SEO_API_URL || "https://api.openai.com/v1/chat/completions";

const OPENAI_TIMEOUT_MS  = clampEnv("OPENAI_SEO_TIMEOUT_MS",  12000, 120000, 45000);
const OPENAI_MAX_RETRIES = clampEnv("OPENAI_SEO_MAX_RETRIES",      1,      5,     3);
const OPENAI_MAX_TOKENS  = clampEnv("OPENAI_SEO_MAX_TOKENS",     700,   2200,  1300);

const MIN_STRONG_SCORE = 72;

const INITIAL_TEMPERATURES = [0.45, 0.82];

// Third-pass gate -- same cost-saving pattern as the scam engine.
// REWRITE: valid but weak (72-79). Full rewrite beats sentence polish at this score range.
// POLISH:  both passes close (gap < 8) and neither excellent (< 88). Sentence-level fixes help.
// Otherwise: one pass dominated or both are excellent -- take the winner, no third call.
const REWRITE_SCORE_THRESHOLD = 80;
const POLISH_SCORE_CEILING    = 88;
const POLISH_GAP_THRESHOLD    = 8;

const DEFAULT_SUBHEAD_BY_INTENT = {
  token_risk:          "Risk Breakdown",
  token_profile:       "Token Breakdown",
  chain_ecosystem:     "Ecosystem Breakdown",
  market_context:      "Market Breakdown",
  category_theme:      "Category Breakdown",
  education_explainer: "Crypto Breakdown",
  comparison:          "Comparison Breakdown",
  general_crypto:      "Crypto Breakdown",
  dex_aggregator:      "Swap Breakdown",
};

/* =========================
   UTILS
   ========================= */

function clampEnv(key, min, max, defaultVal) {
  return Math.max(min, Math.min(max, Number(process.env[key] || defaultVal)));
}
function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }
function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
function unique(values) { return [...new Set((values || []).filter(Boolean))]; }

function normalizeSeoKeyword(value) {
  return String(value || "")
    .replace(/[\u2013\u2014]/g, "-")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}
function normalizeWhitespace(value) { return String(value || "").replace(/\s+/g, " ").trim(); }
function safeLower(value) { return normalizeWhitespace(value).toLowerCase(); }

function stableHash(input) {
  const clean = normalizeSeoKeyword(input);
  let hash = 0;
  for (let i = 0; i < clean.length; i++) { hash = (hash * 31 + clean.charCodeAt(i)) >>> 0; }
  return hash >>> 0;
}

function ensureOpenAiConfig() {
  if (!process.env.OPENAI_API_KEY)
    throw new Error("OPENAI_API_KEY is missing for Token Risk SEO generation");
}
function ensurePrompt(prompt, label) {
  const value = String(prompt || "").trim();
  if (!value) throw new Error(`${label} is empty for Token Risk SEO generation`);
  return value;
}

function tokenizeKeyword(keyword) {
  return unique(
    normalizeSeoKeyword(keyword).split(/[^a-zA-Z0-9]+/).map((t) => t.trim()).filter(Boolean)
  );
}

/* =========================
   TEXT PROCESSING
   ========================= */

function splitSeoParagraphs(text) {
  return String(text || "")
    .replace(/\r/g, "")
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);
}

function sanitizeSeoContent(text) {
  const cleaned = String(text || "")
    .replace(/\r/g, "")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^[*-]\s+/gm, "")
    .replace(/^["]+|["]+$/g, "")
    .replace(/^[`]+|[`]+$/g, "")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  return splitSeoParagraphs(cleaned)
    .map((p) =>
      p.replace(/\s+/g, " ")
        .replace(/\s+([,.!?;:])/g, "$1")
        .replace(/\b(can not)\b/gi, "cannot")
        .replace(/\butilise\b/gi, "use")
        .trim()
    )
    .join("\n\n")
    .trim();
}

function seoWordCount(text) { return String(text || "").trim().split(/\s+/).filter(Boolean).length; }
function paragraphWordCount(paragraph) { return String(paragraph || "").trim().split(/\s+/).filter(Boolean).length; }
function splitSentences(text) {
  return String(text || "").replace(/\s+/g, " ").match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [];
}
function countSentences(text) { return splitSentences(text).length; }
function hasListFormatting(text) { return /^[-*#]/m.test(String(text || "")); }
function hasHtmlFormatting(text) { return /<[a-z][\s\S]*>/i.test(String(text || "")); }
function hasOverlongSentence(text) {
  return splitSentences(text).some((s) => paragraphWordCount(s) > 38);
}

/* =========================
   INTENT DETECTION
   ========================= */

function detectSeoIntent(keyword) {
  const lower = normalizeSeoKeyword(keyword).toLowerCase();
  const hasAddress = /\b0x[a-fA-F0-9]{40}\b|\b[1-9A-HJ-NP-Za-km-z]{32,44}\b/.test(keyword);

  if (
    /safe|unsafe|legit|scam|rug pull|rug|honeypot|risk score|high risk|low risk|real or fake|should i buy|is this token safe|is token safe|token risk|contract risk|blacklist|freeze|renounced|mintable|holder concentration|lp lock|slippage/.test(lower)
  ) return "token_risk";

  if (/\bvs\b|versus|compare|comparison|better than|difference between/.test(lower) &&
      !/raydium\s+vs|orca\s+vs|jupiter\s+vs|vs\s+jupiter|vs\s+raydium|vs\s+orca/.test(lower))
    return "comparison";

  // DEX aggregator intent -- runs before education_explainer / chain_ecosystem / category_theme
  // so that "how to swap SOL", "cross-chain swap", "best dex Solana" route correctly.
  if (
    /\bdex[\s-]?aggregator\b|aggregator[\s-]?dex\b|best\s+dex\b|swap\s+aggregator|multi[\s-]?dex|dex\s+routing|best\s+execution/.test(lower) ||
    /cheapest\s+(swap|crypto|token|sol|solana)|best\s+(price|rate)\s+(to\s+)?swap|find\s+best\s+(dex|swap|price|rate)/.test(lower) ||
    /\bsol(ana)?\s+swap\b|swap\s+sol(ana)?\b|solana\s+dex\b|solana\s+exchange\b|spl\s+token\s+swap/.test(lower) ||
    /raydium\s+vs|orca\s+vs|jupiter\s+vs|vs\s+jupiter|vs\s+raydium|vs\s+orca|vs\s+meteora|meteora\s+vs/.test(lower) ||
    /cross[\s-]?chain\s+swap|bridge\s+sol(ana)?|solana\s+cross[\s-]?chain|sol\s+to\s+(eth|usdc|bnb|avax|matic|base|arb)\b|(eth|usdc|bnb)\s+to\s+sol/.test(lower) ||
    /no[\s-]?kyc\s+(swap|dex|crypto|solana)|swap\s+without\s+kyc|anonymous\s+(swap|dex)/.test(lower) ||
    (/\bswap\b/.test(lower) &&
     /\b(best|cheap|cheapest|fast|instant|price|rate|aggregat|compare|split|rout)\b/.test(lower) &&
     !/\b(scam|risk|safe|honeypot|rug|risky)\b/.test(lower))
  ) return "dex_aggregator";

  if (
    /\bwhat is\b|\bhow does\b|\bhow to\b|\bwhy\b|\bguide\b|\bexplained?\b|\bmeaning\b|\bbeginners?\b|\bintro\b|\boverview\b/.test(lower)
  ) return "education_explainer";

  if (
    /\becosystem\b|\bchain\b|\blayer[\s-]?1\b|\blayer[\s-]?2\b|\bl[12]\b|\bnetwork\b|\brollup\b|\bsidechain\b/.test(lower)
  ) return "chain_ecosystem";

  if (
    /\bai[\s-]?tokens?\b|\bdefi\b|\bdepin\b|\bgaming\b|\bplay[\s-]?to[\s-]?earn\b|\bp2e\b|\brwa\b|\breal[\s-]?world[\s-]?assets?\b|\bmeme[\s-]?coins?\b|\bstablecoins?\b|\bnft\b|\bsector\b|\bcategory\b|\bnarrative\b|\boracles?\b|\bperps?\b|\bperpetual\b|\byield\b|\bamm\b|\bdex\b|\bcex\b|\blaunchpad\b|\bstaking\b|\brestaking\b|\bliquid[\s-]?staking\b|\blst\b|\blrt\b|\bcross[\s-]?chain\b|\bbridge\b|\bmodular\b|\bdata[\s-]?availability\b|\bda[\s-]?layer\b|\binfrastructure\b|\binteroperability\b/.test(lower) &&
    !/\bswap\b/.test(lower)
  ) return "category_theme";

  if (
    /\bprice\b|\bmarket[\s-]?cap\b|\bvolume\b|\btrending\b|\bgainers?\b|\blosers?\b|\bbullish\b|\bbearish\b|\boutlook\b|\btechnical[\s-]?analysis\b|\bsupport\b|\bresistance\b|\ball[\s-]?time[\s-]?high\b|\bath\b|\bpump\b|\bdump\b/.test(lower) &&
    !/\bswap\b/.test(lower)
  ) return "market_context";

  if (hasAddress || /\btoken\b|\bcoin\b/.test(lower)) return "token_profile";
  return "general_crypto";
}

/* =========================
   LOCAL CONTEXT BUILDER
   -- replaces all external API calls.
   Each intent gets rich, structural detail arrays that serve as prompt
   texture. Same pattern as classify() in the scam check engine.
   ========================= */

const INTENT_CONTEXTS = {
  dex_aggregator: {
    mechanics: [
      "Raydium CLMM: liquidity concentrated in tick ranges around current price -- depth thins rapidly 2-3% away from quote, full price impact applies to any order that moves beyond the active range",
      "Orca Whirlpool: same CLMM architecture as Raydium but distinct LP positions -- different depth profile on the same pair, aggregation captures both pools simultaneously",
      "Meteora DLMM: dynamic liquidity market maker rebalances positions toward current price -- deep near the quote but position-dependent, changes between blocks",
      "A $10,000 SOL/USDC swap direct on Raydium: 0.22% price impact. Split 55/45 Raydium/Orca: 0.09% impact -- $13 saved on one trade, compounds across dozens",
      "At $50,000 trade size: single-pool impact reaches 1.1-1.8% on major pairs, split route holds 0.4-0.7% -- difference is $350-550 on the same tokens",
      "New SPL token with $200K pool: a $4,000 swap moves price 2% before slippage setting activates -- aggregator finds the deepest tick concentration or rejects the route",
      "Cross-chain SOL to ETH: bridge layer adds 0.05-0.15% overhead, offset when aggregator finds optimal destination DEX entry point vs manual two-step approach",
      "Quote versus fill divergence: quote reflects pool state before your transaction, fill reflects pool state after -- on Solana's 400ms blocks, difference matters on fast-moving pairs",
    ],
    entryPoints: [
      "open on the specific price difference between a direct swap and an aggregated route -- the number first, the mechanism second",
      "open on how concentrated liquidity clusters depth in a narrow tick range -- and what happens when a trade is larger than that range",
      "open on what the aggregator actually does in the time between quote and transaction -- the routing calculation across active pools",
      "open on the fill price gap: what the quote showed versus what the wallet received, and why those two numbers diverge",
    ],
    consequenceCues: [
      "direct Raydium swap on a $15,000 order received 0.8% less than the aggregated split route -- $120 left on the table in one transaction",
      "single-pool execution on a new token: 1% slippage tolerance accepted, actual fill 1.9% worse than quoted -- pool moved during the 400ms between quote and execution",
      "manual two-step cross-chain cost 0.38% more than the single aggregated route on the same pair the same day",
    ],
  },

  token_risk: {
    mechanics: [
      "honeypot transfer() function: require() evaluates false for non-whitelisted addresses -- buy transactions execute normally, sell transactions revert at gas cost with no receipt",
      "minting not renounced: owner address retains mint authority after launch -- new supply issuable without on-chain event visible in standard explorer views",
      "LP not locked: 100% of pool liquidity held in a single deployer wallet, removable in one transaction -- pool drains to zero in the same block, price collapses before any exit executes",
      "top 5 wallets hold 34%, 12%, 9%, 7%, 6% of supply -- combined 68%. Five coordinated exits move the full float faster than the pool absorbs at any realistic price",
      "pool depth $180,000, market cap $2.4M -- ratio 13:1. A $15,000 sell moves price 8.3% before slippage. Exit difficulty grows non-linearly with trade size",
      "dynamic tax function: sell tax coded as adjustable by owner -- can be raised from 5% to 99% post-launch without a logged transaction or front-end warning",
      "freeze authority not revoked: owner can pause all token transfers -- effectively a remote kill switch, executable without affecting the price chart before activation",
      "token age 11 days, holder count 847, volume/market cap ratio 0.34 -- low volume relative to age suggests limited organic demand or early holder accumulation phase",
    ],
    entryPoints: [
      "open on the specific contract function -- what it does and what it means for anyone holding the token",
      "open on the liquidity structure -- pool depth, who holds the LP tokens, what removal looks like on-chain",
      "open on the holder distribution -- top wallet percentages, what coordinated exit looks like in practice",
      "open on the token age and trading pattern -- what the on-chain history says about how this token has been used",
    ],
    consequenceCues: [
      "sell transaction reverted at gas cost -- token balance unchanged, no exit path available through any standard DEX interface",
      "liquidity removed in a single transaction -- token price fell 99.3% within the same block, no sell orders executed before the pool hit zero",
      "top holder exited 9.2% of supply across two transactions -- price dropped 34% before the second transaction confirmed",
    ],
  },

  token_profile: {
    mechanics: [
      "Solana 400ms block time: enables DEX trading speeds impossible on Ethereum L1 -- price discovery happens faster, arbitrage closes gaps within seconds",
      "SPL token standard: all transaction fees paid in SOL regardless of token -- wallet must hold SOL balance to execute any token activity",
      "concentrated liquidity pool: TVL number can overstate effective depth by 5-10x -- liquidity outside the active tick range does nothing for your trade",
      "liquid staking token: value accrues through validator rewards at the protocol level -- appreciation mechanism is deterministic, not market-driven",
      "wrapped bridged token: counterparty risk sits with the bridge custodian, not the smart contract -- liquidity fragmented across canonical and bridged versions of the same asset",
      "governance token with lock: on-chain votes require staked balance -- circulating float reduced during active governance periods, price impact per dollar increases",
      "vesting cliff: scheduled token unlock creates predictable sell pressure at the cliff date -- on-chain verifiable, often 10-25% of total supply releasing on a single date",
    ],
    entryPoints: [
      "open on what this token actually does -- the mechanism that creates or transfers value",
      "open on which chain it operates on and what that means for liquidity and exit conditions",
      "open on the supply schedule -- how tokens enter circulation, who holds the unlocking wallets",
      "open on the category mechanics -- what drives value in this sector and what undermines it",
    ],
    consequenceCues: [
      "bridge exploit froze canonical redemptions -- wrapped version traded at 40% discount with no guaranteed parity date",
      "governance lock reduced liquid float by 22% during proposal period -- thin liquidity amplified downward price moves",
      "cliff unlock released 18% of supply on a single date -- price declined 31% over the following nine days",
    ],
  },

  education_explainer: {
    mechanics: [
      "slippage tolerance: a ceiling, not a target -- setting 1% means any fill up to 1% worse than quoted is accepted, actual fill determined by pool state at execution time",
      "price impact versus slippage: price impact is deterministic (how much your order moves the pool), slippage is uncertainty between quote and execution -- both cost money, neither is visible on the chart",
      "MEV on Solana: validators can reorder transactions within a block -- sandwich attacks insert a buy before and a sell after large swaps, extracting the price gap from both sides",
      "concentrated liquidity: a pool with $1M TVL may have only $80K of effective depth within 1% of current price -- the rest is inactive until price reaches those ticks",
      "non-custodial swap: private key never leaves the wallet, no third party holds funds at any point -- counterparty risk is the smart contract code, not a company or intermediary",
      "LP impermanent loss: providing liquidity to a token that moves 50% against the pair results in 5.7% worse performance than holding -- calculable, permanent when position is withdrawn",
    ],
    entryPoints: [
      "open on the most common misread of this concept -- what people think it means versus what it actually controls",
      "open on the mechanism itself -- how it works on-chain before explaining why it matters",
      "open on the cost -- what happens when someone misunderstands this and acts on the wrong model",
      "open on the specific scenario where this concept becomes consequential and concrete",
    ],
    consequenceCues: [
      "1% slippage tolerance on a thin pool: actual fill 2.4% worse than quoted -- $240 additional cost on a $10,000 swap where the expected slippage showed $100",
      "LP withdrawn during high volatility: impermanent loss realized at 8.3%, worse than holding either asset through the same period",
      "price impact ignored on a $20,000 trade: moved the pool 3.4%, effectively paid a 3.4% hidden fee on top of the stated swap fee",
    ],
  },

  comparison: {
    mechanics: [
      "Raydium versus Orca: both CLMM, different LP position distributions -- Raydium typically deeper on SOL pairs, Orca tighter on USDC-denominated pairs, aggregator uses both",
      "CEX versus DEX: CEX matches orders off-chain with no on-chain price impact, settles on internal ledger -- DEX executes on-chain, pool state changes with every trade",
      "aggregator versus direct swap: aggregator adds 1-3 routing hops and 15-40ms latency, net improvement starts at around $2,000-3,000 trade size through split routing",
      "Ethereum versus Solana DEX: Ethereum gas makes swaps below $500 uneconomical, Solana $0.001 fee enables micro-swaps profitably -- liquidity distribution reflects this",
      "limit order versus market order: limit guarantees price, not fill -- market guarantees fill, not price. On thin Solana pools, a market order at the wrong size costs 2-5x the stated fee",
      "CEX order book versus AMM pool: order book matches counterparties, no price impact from queue depth -- AMM applies price impact to every trade based on pool reserves",
    ],
    entryPoints: [
      "open on the specific mechanical difference between the two -- not the feature list, the underlying architecture",
      "open on where the two approaches diverge in practice -- the specific condition that produces a different outcome",
      "open on the cost difference -- what each approach costs in a concrete scenario with specific numbers",
      "open on the condition where one clearly beats the other -- and why that condition is more or less common than most traders assume",
    ],
    consequenceCues: [
      "direct DEX swap versus aggregated: $8 difference on a $3,000 trade, $340 difference on a $100,000 trade -- same tokens, same day",
      "CEX limit order: filled at target price 4 minutes later -- DEX market order: filled immediately, 0.6% worse than the delayed CEX fill",
      "Raydium direct at $15,000: 0.31% price impact. Aggregated split: 0.12% -- routing overhead recovered 4x over in one trade",
    ],
  },

  chain_ecosystem: {
    mechanics: [
      "Solana throughput: 65,000 TPS theoretical, 3,000-4,000 sustained under normal load -- enables DEX matching speeds that would congest Ethereum L1 in seconds",
      "Solana validator set: 1,700+ active validators, stake-weighted consensus -- staking yield 6-8% annually drawn from inflation schedule, not fee revenue",
      "EVM incompatibility: Solana is not EVM-compatible -- Ethereum contracts, wallets, and tooling require full redevelopment for Solana, not porting",
      "Base (Ethereum L2): EVM-compatible, Coinbase-sequenced rollup, $0.001-0.01 per transaction -- Ethereum security model, 10x cheaper execution",
      "Arbitrum: optimistic rollup with 7-day challenge window for L1 withdrawals -- faster and cheaper than Ethereum mainnet, slower finality than Solana for cross-chain moves",
      "liquidity fragmentation: depth split across Ethereum, Arbitrum, Base, Solana, BNB Chain -- cross-chain aggregation reaches pools unavailable to single-chain routing",
    ],
    entryPoints: [
      "open on the chain's core technical constraint -- what it can and cannot do that determines where liquidity accumulates",
      "open on how liquidity is distributed on this chain -- where it concentrates, where it thins, and why",
      "open on the fee structure -- what it costs to trade and how that shapes who uses it and for what size",
      "open on this chain's relationship to Ethereum -- dependent, independent, or competing for the same liquidity base",
    ],
    consequenceCues: [
      "Solana network congestion during a high-volume event: transaction failure rates reached 40% -- priority fee market emerged, effective cost 100x the base fee within minutes",
      "EVM-to-Solana contract migration: six months of re-audit and redeployment -- identical logic does not compile to Solana BPF, no shortcut",
      "cross-chain bridge exploit period: funds frozen across connected chains for three days -- ecosystem-wide liquidity pause regardless of individual token exposure",
    ],
  },

  market_context: {
    mechanics: [
      "volume to market cap ratio above 0.5: suggests active trading relative to size -- below 0.05 suggests thin participation, wash trading, or early accumulation phase",
      "perpetual funding rate: positive rate means longs pay shorts -- sustained positive funding indicates leveraged long bias, mean-reverts when positions unwind or get liquidated",
      "open interest relative to market cap: OI above 15% of market cap creates fragile conditions -- cascading liquidations when price moves 5-8% against the dominant side",
      "bid-ask spread on spot: sub-0.1% on major pairs, 0.5-2% on mid-caps, 2-10% on new tokens -- spread is an invisible fee paid on every round trip, not shown on charts",
      "realized versus unrealized PnL: high unrealized profit concentrated in early wallets creates structural sell pressure when those holders decide to exit simultaneously",
      "order book depth at 2%: how much dollar volume sits within 2% of current price on both sides -- thin depth means small orders move price disproportionately",
    ],
    entryPoints: [
      "open on the specific market structure signal -- what the data shows before explaining what it means",
      "open on the liquidity condition -- how much depth exists and where it sits relative to current price",
      "open on the holder behavior pattern -- what on-chain activity reveals about who is buying and selling",
      "open on the price mechanics -- what is driving the current move and whether that driver is structural or temporary",
    ],
    consequenceCues: [
      "funding rate sustained at 0.08% per 8 hours for 11 days -- long liquidations cascaded when price dropped 12%, open interest fell 58% in four hours",
      "bid-ask spread widened from 0.2% to 3.1% as market makers pulled liquidity -- effective exit cost tripled before price moved another 8% lower",
      "top 3 wallets represented 31% of supply -- two exited within the same hour, price impact absorbed entirely by remaining pool depth",
    ],
  },

  category_theme: {
    mechanics: [
      "liquid staking token: redemption value accrues through validator rewards at the protocol level -- appreciation is deterministic, market price can trade at premium or discount to this floor",
      "real world assets on-chain: token backed by off-chain asset -- redemption depends on custodian relationship and legal structure, not smart contract execution",
      "perpetual DEX token: fee revenue accrues to stakers as protocol profit -- demand tied to trading volume, not price appreciation of the underlying platform",
      "launchpad governance token: value from allocation rights to new launches -- dependent on deal pipeline quality, vesting schedules on launched tokens create sustained sell pressure",
      "oracle network token: pays node operators for data feeds -- demand tied to DeFi protocol adoption, falls directly if major protocols deprecate the feed",
      "play-to-earn token: in-game supply inflates as players earn rewards -- without burn mechanisms, supply growth typically outpaces demand growth past early adoption phase",
    ],
    entryPoints: [
      "open on what this category actually is mechanically -- what creates or destroys value within it",
      "open on the risk native to this category -- the structural one that doesn't appear in other sectors",
      "open on how this category has behaved structurally -- not the price history, the underlying mechanism",
      "open on the single condition that would most change the outlook for everything in this category",
    ],
    consequenceCues: [
      "RWA custodian relationship terminated -- on-chain token retained no redemption backing, traded at 12% of face value with no recovery mechanism",
      "P2E token inflation: supply grew 340% in eight months, active user base grew 40% -- price followed supply growth downward regardless of gameplay activity",
      "oracle network: three major DeFi protocols deprecated the data feed -- fee revenue fell 71%, node operators began unstaking within the same quarter",
    ],
  },

  general_crypto: {
    mechanics: [
      "private key: 256-bit number controlling all assets at an address -- whoever holds the key controls the assets, no recovery without it regardless of platform policies",
      "smart contract immutability: deployed code cannot be changed unless a proxy upgrade pattern was included -- check whether the contract has an upgrade mechanism",
      "gas fee structure: Ethereum mainnet $2-50 per transaction based on network load -- makes sub-$500 swaps economically unviable against the fee",
      "multisig wallet: N-of-M key threshold required for transactions -- removes single point of failure, coordination overhead increases with M",
      "token vesting schedule: cliff and linear release -- on-chain verifiable at any time, creates predictable sell pressure windows visible before they arrive",
      "smart contract audit: external code review covering logic errors -- does not cover economic attack vectors or post-deployment proxy upgrades",
    ],
    entryPoints: [
      "open on how this works on-chain -- the mechanism before the explanation",
      "open on the cost -- what this concept costs in practice when misunderstood or ignored",
      "open on the common misread -- what most people think it does versus what it actually controls",
      "open on the specific structural question this concept lets you answer",
    ],
    consequenceCues: [
      "recovery phrase entered into a support form -- wallet drained across four transactions within eight minutes",
      "proxy upgrade mechanism exploited three months post-audit -- $4.2M drained through a function not present in the audited version",
      "vesting cliff: 18% of supply released on a single date -- price declined 31% over the following nine days as early holders exited",
    ],
  },
};

// Per-intent entry point pools -- replaces the 4 generic CRYPTO_ENTRY_STYLES.
// Each intent has 4 structurally distinct opening angles.
// buildPassVariation selects from the intent-specific pool via stableHash + passIndex,
// so the same keyword always gets the same two angles across both passes (deterministic),
// and both passes always open from structurally different positions.
const INTENT_ENTRY_POINTS = {
  dex_aggregator: [
    "Open on the routing gap -- what a direct single-pool swap returns versus what a split-route aggregated fill returns on the same pair. State the specific pool condition and trade-size relationship in the first sentence.",
    "Open on the concentrated liquidity architecture -- how CLMM and DLMM depth clusters in a narrow tick range and thins rapidly outside it. Name what that means for a specific trade size before explaining why.",
    "Open on the price impact mechanism -- what happens when a direct swap moves through the active tick range and starts filling against thinner liquidity. Use a concrete depth-to-trade-size relationship in the first sentence.",
    "Open on the execution delta -- the specific difference in tokens received between a direct DEX fill and a split-route aggregated fill on the same pair. State a dollar amount or percentage difference first.",
  ],
  token_risk: [
    "Open on the specific contract function that creates the structural risk -- name what it does on-chain and what it means for anyone holding the token. No framing: the function itself in the first sentence.",
    "Open on the liquidity pool structure -- the actual depth, who controls the LP tokens, and what removal looks like in a single block. State the condition directly, not a description of it.",
    "Open on the holder distribution -- the specific top wallet percentages and what coordinated exit from those positions looks like relative to the available pool depth.",
    "Open on the token's on-chain history -- age, trading pattern, and what those signals reveal about how the token has actually been used since launch.",
  ],
  token_profile: [
    "Open on where the market cap narrative diverges from on-chain reality -- specifically in pool depth, volume quality, or holder behavior. Name the divergence in the first sentence.",
    "Open on what the chain and category combination means for liquidity conditions -- the specific structural constraints this token operates within.",
    "Open on the supply schedule -- how tokens enter circulation, which wallets control unlock events, and what the cliff structure implies for sell pressure timing.",
    "Open on the protocol mechanism that creates or transfers value for this token -- how it actually works, not what category it belongs to.",
  ],
  education_explainer: [
    "Open on the most expensive misunderstanding of this concept -- what people assume it controls versus what it actually does on-chain or in market structure. Name the gap in the first sentence.",
    "Open on the mechanism itself -- how it operates. Not the definition, not the category: the operation, stated in the first sentence.",
    "Open on the specific scenario where this concept becomes consequential -- a trade size, a pool condition, a market state -- and the cost of misunderstanding it becomes concrete.",
    "Open on what most people get wrong about when this concept matters -- the conditions where its impact is measurable versus the conditions where it is not.",
  ],
  comparison: [
    "Open on what is genuinely stronger in one option -- stated clearly, as a real structural signal that holds under most conditions. No irony, no setup for the reversal.",
    "Open on the specific mechanism that makes these two options structurally different -- the operational difference, not the feature list.",
    "Open on the condition where one clearly beats the other -- and state how common or rare that condition is relative to how people typically encounter both options.",
    "Open on the cost structure -- what each option costs in a concrete scenario with specific numbers, trade sizes, or execution conditions named in the first sentence.",
  ],
  market_context: [
    "Open on a specific market signal -- a number, a ratio, or a directional condition. Not a description of the market: the signal itself stated directly.",
    "Open on what the current market structure implies for this token or category -- what the data shows about positioning, pressure, and what would need to change.",
    "Open on the liquidity condition -- how much depth exists, where it sits relative to current price, and what that means for execution at different trade sizes.",
    "Open on the holder behavior pattern -- what on-chain activity reveals about who is buying, selling, and positioning, and whether that pattern is structural or temporary.",
  ],
  chain_ecosystem: [
    "Open on the specific architectural characteristic that defines this chain's liquidity or execution behavior -- not the chain's name or marketing category: the actual mechanism.",
    "Open on how liquidity is distributed on this chain -- where it concentrates, where it thins, and the structural reason behind that distribution.",
    "Open on the fee structure -- what it costs to trade on this chain and how that shapes what the chain is used for, what trade sizes are economical, and where liquidity accumulates.",
    "Open on how this chain sits relative to its nearest architectural peer -- the specific operational or structural difference named in the first sentence.",
  ],
  category_theme: [
    "Open on what separates structurally stronger performers in this category from weaker ones -- the specific mechanism, not the narrative.",
    "Open on the risk native to this category -- the structural one that does not appear in other sectors and that the market periodically reprices.",
    "Open on how the category's value creation mechanism actually works -- what drives appreciation or depreciation within it, stated directly.",
    "Open on where the category narrative and on-chain reality diverge -- the specific signal that shows the gap between the story and the structure.",
  ],
  general_crypto: [
    "Open on the specific structural condition -- not the surface signal or category label. The condition that exists on-chain or in the market, stated in the first sentence.",
    "Open on the mechanism at the core of this topic -- how it operates, what it produces, what changes when it is present versus absent.",
    "Open on the cost -- what this concept costs in practice when misunderstood, ignored, or applied at the wrong scale. Use a specific number or ratio.",
    "Open on the most common misread of this topic -- what people assume it means versus what it actually controls or determines.",
  ],
};

// Composition shapes -- how the four paragraphs relate to each other.
// passIndex selects a different one per pass.
const CRYPTO_COMPOSITION_SHAPES = [
  "Each paragraph establishes a different dimension of the topic -- not four angles on the same observation, four genuinely different structural facts. They belong together but don't need to be bridged.",
  "The first paragraph is the most concrete. Each subsequent paragraph adds a layer the previous one didn't have. The fourth introduces something new -- not a restatement of paragraph one in consequence language.",
  "One paragraph covers the mechanism. One shows what it means in practice with numbers. One covers what changes the analysis. One lands on the structural outcome. They don't hand off to each other -- they each earn their place.",
];

/* =========================
   LOCAL CONTEXT + PASS VARIATION
   ========================= */

/**
 * buildLocalCryptoContext -- replaces fetchCryptoContext().
 * Synchronous. No external API calls. Returns rich intent-specific
 * structural detail for prompt injection.
 */
function buildLocalCryptoContext(keyword, intent) {
  const h = stableHash(keyword);
  const ctx = INTENT_CONTEXTS[intent] || INTENT_CONTEXTS.general_crypto;
  const mechanicsSlice = ctx.mechanics.slice(0, 5).join("\n");
  const consequence = ctx.consequenceCues[h % ctx.consequenceCues.length];

  const contextSummary =
    `Structural context for: "${keyword}"\n\n` +
    `Mechanics and reference patterns:\n${mechanicsSlice}\n\n` +
    `Specific outcome pattern: ${consequence}`;

  return { contextSummary, ctx, h, intent };
}

/**
 * buildPassVariation -- deterministic per-pass structural angle.
 * Different entry point, different composition shape, different
 * reference anchors. Same pattern as buildPassBrief() in the scam engine.
 */
function buildPassVariation(localCtx, passIndex) {
  const { ctx, h, intent } = localCtx;

  // Intent-specific entry point -- each intent has 4 structurally distinct opening angles.
  // Deterministic: same keyword always selects the same angle per pass index.
  const entryPool  = INTENT_ENTRY_POINTS[intent] || INTENT_ENTRY_POINTS.general_crypto;
  const entryStyle = entryPool[(h + passIndex * 2) % entryPool.length];
  const shape      = CRYPTO_COMPOSITION_SHAPES[passIndex % CRYPTO_COMPOSITION_SHAPES.length];

  const total = ctx.mechanics.length;
  const start = (passIndex * 3) % total;
  const anchors = [
    ctx.mechanics[start % total],
    ctx.mechanics[(start + 1) % total],
    ctx.mechanics[(start + 2) % total],
  ].filter(Boolean);

  const consequence = ctx.consequenceCues[(h + passIndex) % ctx.consequenceCues.length];

  return { entryStyle, shape, anchors, consequence };
}

/* =========================
   QUALITY DETECTION
   ========================= */

const GENERIC_PHRASES = [
  "in today's digital age", "it is important to", "users should", "many investors",
  "there are many factors", "one important factor", "in many cases",
  "at the end of the day", "it is worth noting", "one thing to remember",
  "do your own research", "always do your own research", "invest responsibly",
  "you should always", "in conclusion", "overall", "to sum up",
  "the crypto space", "the world of cryptocurrency", "before investing",
  "before making any investment", "helps investors make informed decisions",
  "can be a red flag", "is a red flag", "it may indicate", "it may suggest",
  "this means that", "this is because", "on the other hand", "in other words",
  "there are risks involved", "not financial advice",
];

const NARRATIVE_PHRASES = [
  "imagine", "picture this", "you land on", "you notice", "you see",
  "the page in front of you", "the browser tab", "a timer starts",
  "your wallet is empty", "screenshot", "picture a",
  "suppose you", "the site says", "a banner reads",
  "counting down", "noreply@", "email from",
];

function looksGenericSeo(text) {
  const t = String(text || "").toLowerCase();
  return GENERIC_PHRASES.some((p) => t.includes(p));
}
function hasNarrativeMarkers(text) {
  const t = String(text || "").toLowerCase();
  return NARRATIVE_PHRASES.some((p) => t.includes(p));
}

function countStructuralTerms(text) {
  const lower = String(text || "").toLowerCase();
  return [
    // Token risk terms
    "liquidity","slippage","exit","sell pressure","holders","holder concentration",
    "wallet concentration","distribution","ownership","top holders","whales",
    "contract","permissions","renounced","mint","freeze","blacklist","control",
    "volatility","momentum","market depth","trust","downside","fragile",
    "market cap","volume","utility","ecosystem","chain","rotation","trend",
    "pool","fdv","fully diluted","circulating supply","tokenomics","vesting",
    "unlock","lockup","protocol","yield","apy","apr","tvl","total value locked",
    // DEX aggregator + Solana terms
    "routing","split route","price impact","mev","sandwich","front-run",
    "aggregation","liquidity source","gas","slippage tolerance","best execution",
    "price improvement","dex liquidity","amm","multi-hop","protocol fee",
    "swap fee","non-custodial","permissionless","pool depth","price quote",
    "route optimizer","liquidity fragmentation","price discovery",
    "raydium","orca","jupiter","meteora","phoenix","spl","solana",
    "cross-chain","bridge","concentrated liquidity","clmm","dlmm","whirlpool",
    "execution quality","fill rate",
  ].filter((t) => lower.includes(t)).length;
}

function countInterpretationTerms(text) {
  const lower = String(text || "").toLowerCase();
  let count = 0;
  if (/\b(because|since|as a result|which means|this creates|this produces|this makes|when .{3,40}(means|creates|results|leaves|forces|raises|drives))\b/.test(lower)) count++;
  if (/\b(compound|amplif|interact|reinfor|combined with|simultane|stack|both .{3,30} and .{3,30}(creat|produc|result|mean))\w*/.test(lower)) count++;
  if (/\b(despite|regardless|even (if|when|though)|while .{3,35}(not|doesn|cannot|fail)|looks? (stable|thin|strong|weak|fragile)|appears? (stable|thin|strong|weak|inflated))\b/.test(lower)) count++;
  if (/\b(asymmetr|one.sided|uneven|absorb|inherit|bears? the|face the|late buyers|early wallets)\w*/.test(lower)) count++;
  if (/\b(mechanism|operat|functions? (as|through|like)|works? (against|through|like)|behav|trigger|activat|execut|enforc)\w*/.test(lower)) count++;
  if (/\b(until|threshold|break|collapse|exhaust|exceed|beyond|floor|ceiling|tipping point|breaking point)\w*/.test(lower)) count++;
  if (/\b(relative to|compared (to|with)|ratio|proportion|multiple of|\d+x|times (larger|smaller|more|deeper|thinner))\b/.test(lower)) count++;
  if (/\b(over time|progressively|slippage widens|depth (erodes|shrinks)|risk (accumulates|builds|increases)|pressure (builds|mounts|grows)|deteriorat|erode)\w*/.test(lower)) count++;
  return count;
}

function countConsequenceTerms(text) {
  const lower = String(text || "").toLowerCase();
  return [
    "losses","fast downside","rapid downside","exit difficulty","slippage",
    "sell pressure","price drops","sharp sell-offs","reversals","buyers trapped",
    "confidence breaks","volatility","downside","harder to exit","momentum fades",
    "pricing weakens","rotation leaves","cost basis","absorb","worst exit",
    "narrow exit","competitive exit","price impact","spread widens",
    "execution cost","fill price","worse than quoted","overpay","underfill",
    "missed route","higher cost","execution gap","pool moves","quote diverges",
  ].filter((t) => lower.includes(t)).length;
}

/* =========================
   UNIFIED VALIDATION
   ========================= */

function getValidationProfile(keyword, framingName) {
  const intent = detectSeoIntent(keyword);
  const maxSentencesPerParagraph = framingName === "compressed" ? 4 : 5;
  const base = {
    intent, minWords: 190, maxWords: 420,
    minStructuralTerms: 5, minInterpretationTerms: 2, minConsequenceTerms: 2,
    minWordsPerParagraph: 28, maxWordsPerParagraph: 105, maxSentencesPerParagraph,
  };
  if (intent === "token_risk")
    return { ...base, minWords: 200, maxWords: 430, minStructuralTerms: 6, minInterpretationTerms: 3, minConsequenceTerms: 3 };
  if (intent === "token_profile")
    return { ...base, minWords: 185, maxWords: 415, minStructuralTerms: 5, minConsequenceTerms: 1 };
  if (intent === "dex_aggregator")
    return {
      ...base,
      minWords: 185, maxWords: 415,
      minStructuralTerms: 4, minInterpretationTerms: 2, minConsequenceTerms: 1,
    };
  return base;
}

function validateSeoContent(text, keyword = "", framingName = "") {
  const content = sanitizeSeoContent(text);
  const profile = getValidationProfile(keyword, framingName);
  const paragraphs = splitSeoParagraphs(content);
  const lower = content.toLowerCase();
  const reasons = [];
  let score = 100;

  if (!content) return { valid: false, score: 0, reasons: ["empty content"], content, paragraphs };
  if (paragraphs.length !== 4) return { valid: false, score: 0, reasons: [`paragraph count ${paragraphs.length} != 4`], content, paragraphs };
  if (hasListFormatting(content)) return { valid: false, score: 0, reasons: ["list formatting"], content, paragraphs };
  if (hasHtmlFormatting(content)) return { valid: false, score: 0, reasons: ["html formatting"], content, paragraphs };
  if (hasNarrativeMarkers(content)) return { valid: false, score: 0, reasons: ["narrative markers"], content, paragraphs };
  if (looksGenericSeo(content)) return { valid: false, score: 0, reasons: ["generic seo phrases"], content, paragraphs };

  const totalWords = seoWordCount(content);
  if (totalWords < profile.minWords) return { valid: false, score: 0, reasons: [`too short: ${totalWords} words`], content, paragraphs };
  if (totalWords > profile.maxWords) { score -= 10; reasons.push("slightly long"); }

  for (let i = 0; i < paragraphs.length; i++) {
    const p = paragraphs[i];
    const words = paragraphWordCount(p);
    const sentences = countSentences(p);
    if (words < profile.minWordsPerParagraph) return { valid: false, score: 0, reasons: [`p${i + 1} too short: ${words}w`], content, paragraphs };
    if (words > profile.maxWordsPerParagraph) { score -= 8; reasons.push(`p${i + 1} long`); }
    if (sentences < 2) return { valid: false, score: 0, reasons: [`p${i + 1} has only ${sentences} sentence`], content, paragraphs };
    if (sentences > profile.maxSentencesPerParagraph) return { valid: false, score: 0, reasons: [`p${i + 1} exceeds ${profile.maxSentencesPerParagraph}-sentence max (${sentences})`], content, paragraphs };
    if (hasOverlongSentence(p)) { score -= 8; reasons.push(`p${i + 1} overlong sentence`); }
  }

  const starts = new Set();
  for (const p of paragraphs) {
    const fp = p.toLowerCase().replace(/[^a-z0-9\s]/g, "").trim().slice(0, 60);
    if (starts.has(fp)) { score -= 12; reasons.push("duplicate paragraph start"); break; }
    starts.add(fp);
  }

  const structural     = countStructuralTerms(content);
  const interpretation = countInterpretationTerms(content);
  const consequence    = countConsequenceTerms(content);

  if (structural < profile.minStructuralTerms) { score -= 18; reasons.push(`low structural: ${structural}`); }
  else if (structural >= profile.minStructuralTerms + 4) score += 8;
  if (interpretation < profile.minInterpretationTerms) { score -= 11; reasons.push(`low interpretation: ${interpretation}`); }
  else if (interpretation >= profile.minInterpretationTerms + 2) score += 6;
  if (consequence < profile.minConsequenceTerms) { score -= 12; reasons.push(`low consequence: ${consequence}`); }
  else if (consequence >= profile.minConsequenceTerms + 2) score += 5;

  const kw = normalizeSeoKeyword(keyword).toLowerCase();
  if (kw && lower.includes(kw)) score += 3;
  if (/you should|do your own research|not financial advice|nfa/i.test(lower)) { score -= 16; reasons.push("disclaimer"); }

  if (!/risk|token|trust|structure|fragile|downside|market|liquidity|ecosystem|chain|difference|price|pool|routing|execution|aggregat|solana|swap/.test(paragraphs[0].toLowerCase())) {
    score -= 12; reasons.push("p1 not grounded");
  }
  if (!/loss|downside|exit|slippage|reversal|confidence|volatility|difficulty|risk|pressure|fragile|break|cost|impact|narrow|worst|absorb|without|unless|until|requires|depends|reduces|changes|locked|renounced|distributed|condition|threshold|ratio|floor|execution cost|fill price|overpay|quote diverges|pool moves/.test(paragraphs[3].toLowerCase())) {
    score -= 10; reasons.push("p4 lacks consequence");
  }

  const dominantNouns = [
    "liquidity","holders","contract","slippage","exit","momentum",
    "distribution","ownership","volatility","pool","supply","trust",
    "routing","execution","aggregat",
  ];
  for (const noun of dominantNouns) {
    if (paragraphs.filter((p) => p.toLowerCase().includes(noun)).length >= 4) {
      score -= 10; reasons.push(`noun overuse: "${noun}" in all 4 paragraphs`);
    }
  }

  const openingWords = paragraphs.map((p) => p.trim().split(/\s+/)[0]?.toLowerCase() || "");
  if (new Set(openingWords).size < paragraphs.length) { score -= 10; reasons.push("paragraphs share opening word"); }

  const p1Vocab  = new Set(paragraphs[0].toLowerCase().replace(/[^a-z\s]/g, "").split(/\s+/).filter((w) => w.length >= 6));
  const p4Tokens = paragraphs[3].toLowerCase().replace(/[^a-z\s]/g, "").split(/\s+/).filter((w) => w.length >= 6);
  const p1p4Overlap = p4Tokens.filter((w) => p1Vocab.has(w)).length;
  if (p1p4Overlap >= 13) { score -= 8; reasons.push(`p1/p4 vocab overlap: ${p1p4Overlap} shared words`); }

  const finalScore = clamp(score, 0, 100);
  return { valid: finalScore >= MIN_STRONG_SCORE, score: finalScore, reasons, content, paragraphs };
}

/* =========================
   PROMPT SYSTEM
   ========================= */

function buildHardRules(framingName) {
  const maxSentences = framingName === "compressed" ? 4 : 5;
  return `Write like a senior crypto analyst who has read the on-chain data and is explaining what it means to someone making a real decision. Be specific, be direct, and be honest about uncertainty. Every sentence should add something the previous one did not.

Output rules - follow exactly:
- Exactly 4 paragraphs separated by a blank line
- No headings, bullets, numbered lists, bold text, or HTML tags
- 190-420 words total; 28-105 words per paragraph; maximum ${maxSentences} sentences per paragraph
- No single sentence longer than 35 words
- Never write: "do your own research", "in conclusion", "it is important to", "investors should", "red flag", "overall", "in other words", "not financial advice", "it is worth noting", "for example"
- Do not invent numbers, wallet counts, liquidity figures, or holder data unless drawn from the reference examples below
- No story-mode writing, fake scenarios, or second-person walkthroughs
- Each paragraph must open with a different word - no two paragraphs may start with the same word
- Do not repeat the same dominant noun across more than two paragraphs
- Paragraph 4 must introduce new information, not restate paragraph 1 in consequence language
- In each paragraph, at least one sentence should be noticeably shorter than the others (under 12 words)`;
}

function buildAnalystExample(intent) {
  if (intent === "dex_aggregator") {
    return `Example of the precision this requires (one integrated passage, not a list):

A direct Raydium swap executes at the current CLMM pool price with full price impact applied to your trade size. An aggregator runs the same trade simultaneously across Raydium, Orca, and Meteora, then routes the order through the deepest active tick range or splits it across pools to reduce impact. On Solana's concentrated liquidity architecture, where depth clusters tightly around the current price, moving 5% of a pool's active liquidity costs significantly more than the quoted slippage suggests. That difference compounds on larger trades and on tokens with fragmented liquidity across multiple venues.

Find the equivalent precision for this keyword and write toward it.`;
  }

  return `Example of the precision this requires (one integrated passage, not a list):

The chart says one thing; the pool says another. Price above a thin pool is not stability -- it is selling pressure that has not arrived yet. When volume drops and holders start looking for exits, the spread widens before the chart moves, and buyers who entered near the top find the exit costs more than entry implied. Concentration makes this worse. Early wallets do not exit after price falls; they exit into price, which is why retail absorbs the tail. The structure is not failing -- it is working exactly as designed, just not in buyers' favor.

Find the equivalent precision for this keyword and write toward it.`;
}

const PROMPT_FRAMINGS = {

  analyst: (keyword, intent, localCtx, variation) => ({
    system: `You write 4-paragraph crypto analysis for an intelligence product.

Your job: expose the gap between how an asset or mechanism looks on the surface and how it actually behaves under real conditions.

Do NOT explain mechanics step by step. Do NOT open with a definition. Open on the gap itself -- the thing the surface reading misses -- and let the mechanics emerge from why the gap exists.

${buildAnalystExample(intent)}

${buildHardRules("analyst")}`,
    user: `Analysis for: "${normalizeSeoKeyword(keyword)}"
Intent: ${intent}

${localCtx.contextSummary}

Pass direction: ${variation.entryStyle}
Composition: ${variation.shape}

Reference examples for this pass:
${variation.anchors.map((a) => `- ${a}`).join("\n")}

Specific outcome pattern: ${variation.consequence}

Write four paragraphs answering these questions in order -- do not use the questions as headings:

1. What specific mismatch exists between what the surface signal shows and what the structure actually is?
2. Which single factor carries the most weight here, and what is the precise mechanism that makes it matter?
3. How do two signals from the reference examples interact to create a condition that neither would produce alone?
4. What does the current structure mean in concrete terms -- stated as a specific cost, ratio, or outcome, not as a general warning?`,
  }),

  mechanics: (keyword, intent, localCtx, variation) => ({
    system: `You write crypto structure analysis for an intelligence product. Your focus is mechanics -- how each condition actually operates, not what label to give it.

Do NOT open with a surface-vs-structure framing. Open directly on the mechanism itself -- how it works on-chain or in the market -- with the precision of someone who has read the actual data.

${buildHardRules("mechanics")}`,
    user: `Mechanical analysis of: "${normalizeSeoKeyword(keyword)}"
Intent: ${intent}

${localCtx.contextSummary}

Pass direction: ${variation.entryStyle}
Composition: ${variation.shape}

Reference examples for this pass:
${variation.anchors.map((a) => `- ${a}`).join("\n")}

Specific outcome pattern: ${variation.consequence}

Write four paragraphs answering these questions in order -- do not use questions as headings:

1. What is the primary mechanism here, how does it operate, and what does it measure that price does not?
2. What weakens or becomes more expensive as a secondary effect when this mechanism is active?
3. Why does this condition not appear on standard charts or scans, and what would you need to look at instead?
4. What is the one data point that would most change this analysis if it changed -- and in which direction?`,
  }),

  contrarian: (keyword, intent, localCtx, variation) => ({
    system: `You write crypto analysis that opens with what is genuinely strong before undercutting it with structural reality. This is not reflexive skepticism -- it is precision. Separate what is actually strong from what only looks strong.

Do NOT open with risk language, warnings, or caveats. Paragraph 1 must open on something genuinely positive -- a real signal, not a setup for the undercut.

${buildHardRules("contrarian")}`,
    user: `Contrarian structural analysis of: "${normalizeSeoKeyword(keyword)}"
Intent: ${intent}

${localCtx.contextSummary}

Pass direction: ${variation.entryStyle}
Composition: ${variation.shape}

Reference examples for this pass:
${variation.anchors.map((a) => `- ${a}`).join("\n")}

Specific outcome pattern: ${variation.consequence}

Write four paragraphs answering these questions in order -- do not use questions as headings:

1. What is genuinely strong about this setup -- stated clearly and without irony?
2. What specific structural question does that strength leave completely unanswered?
3. At what exact condition do the optimistic reading and the structural reality diverge?
4. Which position ends up absorbing the worst outcome when that divergence closes -- and why that position specifically?`,
  }),

  compressed: (keyword, intent, localCtx, variation) => ({
    system: `You write compressed crypto analysis. Every sentence carries weight. Short sentences land harder than long ones.

Do NOT use transitions like "however", "therefore", "as a result", or "which means". Each sentence stands alone. Facts first. Implication second. Nothing between them. Maximum 4 sentences per paragraph.

${buildHardRules("compressed")}`,
    user: `Compressed analysis for: "${normalizeSeoKeyword(keyword)}"
Intent: ${intent}

${localCtx.contextSummary}

Pass direction: ${variation.entryStyle}
Composition: ${variation.shape}

Reference examples for this pass:
${variation.anchors.map((a) => `- ${a}`).join("\n")}

Specific outcome pattern: ${variation.consequence}

Write four paragraphs answering these questions in order -- do not use questions as headings:

1. What is the structural condition stated as directly as possible in two or three sentences?
2. What is the single causal chain -- one input, one mechanism, one output -- nothing else?
3. What is one observable signal that would confirm or deny the condition before it becomes obvious in price?
4. What does the cost look like expressed as a ratio, percentage, or direct comparison rather than a general statement?`,
  }),

  profile: (keyword, intent, localCtx, variation) => ({
    system: `You write crypto asset and mechanism profiles for an intelligence product. You have a view. You use data to support it.

${buildHardRules("profile")}`,
    user: `Profile for: "${normalizeSeoKeyword(keyword)}"
Intent: ${intent}

${localCtx.contextSummary}

Pass direction: ${variation.entryStyle}
Composition: ${variation.shape}

Reference examples for this pass:
${variation.anchors.map((a) => `- ${a}`).join("\n")}

Specific outcome pattern: ${variation.consequence}

Write four paragraphs answering these questions in order -- do not use questions as headings:

1. What category does this sit in, which chain does it operate on, and what does that combination mean for liquidity conditions?
2. Where does the surface reading diverge from the structural reality -- specifically in volume quality, pool depth, or supply mechanics?
3. What does this do that its nearest category peers do not, and is that difference structural or primarily in how it's presented?
4. If the relevant condition reversed sharply, which part of this structure would hold and which would not -- and why?`,
  }),

  explainer: (keyword, intent, localCtx, variation) => ({
    system: `You write expert crypto explainers for an intelligence product. Your job is not to educate -- it is to prevent expensive misunderstandings. Every concept you explain has a common misread that costs money.

${buildHardRules("explainer")}`,
    user: `Expert explainer for: "${normalizeSeoKeyword(keyword)}"
Intent: ${intent}

${localCtx.contextSummary}

Pass direction: ${variation.entryStyle}
Composition: ${variation.shape}

Reference examples for this pass:
${variation.anchors.map((a) => `- ${a}`).join("\n")}

Specific outcome pattern: ${variation.consequence}

Write four paragraphs answering these questions in order -- do not use questions as headings:

1. What is this concept in one precise sentence, and what goes wrong structurally when it is absent or misread?
2. How does it actually operate on-chain or in the market -- mechanics only, no analogies or textbook framing?
3. What do most people think this concept controls versus what it actually controls?
4. What is the one specific question this concept lets you answer that you could not answer without understanding it?`,
  }),

  aggregator_value: (keyword, intent, localCtx, variation) => ({
    system: `You write sharp technical copy for a DEX aggregator that routes swaps across Solana and EVM chains.
Your job: explain why routing across multiple Solana liquidity venues produces better execution than going to any single DEX directly -- and make that argument from mechanism, not marketing.

Do NOT write promotional copy. Do NOT use "best platform", "industry-leading", or similar. Every claim must come from how the mechanism actually works.

The precision required:

WEAK: "A DEX aggregator finds the best price by comparing multiple exchanges."

STRONG: "A direct Raydium swap executes at the current CLMM pool price with full price impact on your trade size. An aggregator runs the same trade simultaneously across Raydium, Orca, and Meteora, then either routes the full order through the deepest pool or splits it across pools to reduce price impact. On Solana's concentrated liquidity architecture, that routing difference is the gap between a 0.3% and a 1.8% execution cost on the same trade."

Write at the STRONG level throughout.

${buildHardRules("aggregator_value")}`,
    user: `DEX aggregator analysis for: "${normalizeSeoKeyword(keyword)}"
Intent: ${intent}

${localCtx.contextSummary}

Pass direction: ${variation.entryStyle}
Composition: ${variation.shape}

Reference examples for this pass:
${variation.anchors.map((a) => `- ${a}`).join("\n")}

Specific outcome pattern: ${variation.consequence}

Write four paragraphs answering these questions in order -- do not use questions as headings:

1. What specific routing problem does a DEX aggregator solve that a direct Solana swap ignores -- and what is the on-chain mechanism that makes it expensive when missed?
2. When does Solana's liquidity fragmentation across multiple venues matter most -- at what trade size or pool configuration does the aggregator advantage become measurable?
3. What does price impact actually cost on a direct pool swap versus a split route -- expressed as a concrete comparison using numbers from the reference examples?
4. What is the one condition where a direct single-DEX swap outperforms aggregation on Solana -- and why is that condition rarer than most traders assume?`,
  }),

  swap_guide: (keyword, intent, localCtx, variation) => ({
    system: `You write precise swap execution analysis for Solana traders who already understand DeFi. Your job is not to explain what a DEX is -- it is to explain what determines swap quality on Solana and how to read the signals before confirming a trade.

Do NOT open with a definition. Open directly on what most traders misread when executing swaps on Solana.

The precision required:

WEAK: "Make sure to check slippage tolerance before swapping."

STRONG: "Slippage tolerance is a ceiling, not a target. Setting 1% means you accept any fill up to 1% worse than the quoted rate -- but on a thin Raydium CLMM pool, the transaction fills at the worst acceptable price, not the quote. The quote reflects pool state before your order changes it. On a $200K pool with a $15K swap, you are moving 7.5% of active liquidity, and the actual fill diverges from the quote by more than the slippage setting shows before execution."

Write at that level of precision throughout.

${buildHardRules("swap_guide")}`,
    user: `Swap execution analysis for: "${normalizeSeoKeyword(keyword)}"
Intent: ${intent}

${localCtx.contextSummary}

Pass direction: ${variation.entryStyle}
Composition: ${variation.shape}

Reference examples for this pass:
${variation.anchors.map((a) => `- ${a}`).join("\n")}

Specific outcome pattern: ${variation.consequence}

Write four paragraphs answering these questions in order -- do not use questions as headings:

1. What is the most common execution mistake on Solana for this type of swap -- and what is the on-chain mechanism that makes it expensive?
2. What does a swap quote on Solana actually measure, and what does it leave out that determines the real fill price?
3. How does pool depth relative to trade size translate into a specific execution cost -- stated as a ratio or percentage, not a general warning?
4. What is the one thing to check before confirming a Solana swap that catches the most common execution problems -- stated in concrete terms?`,
  }),

};

function selectPromptFraming(keyword, passIndex) {
  const intent = detectSeoIntent(keyword);
  const framingOrder = {
    token_risk:          ["analyst",         "compressed",       "contrarian",       "mechanics",        "analyst",         "compressed"],
    token_profile:       ["profile",         "contrarian",       "analyst",          "mechanics",        "profile",         "compressed"],
    market_context:      ["analyst",         "profile",          "contrarian",       "compressed",       "mechanics",       "analyst"],
    chain_ecosystem:     ["profile",         "explainer",        "analyst",          "contrarian",       "mechanics",       "profile"],
    category_theme:      ["analyst",         "contrarian",       "profile",          "explainer",        "compressed",      "analyst"],
    education_explainer: ["explainer",       "mechanics",        "analyst",          "contrarian",       "explainer",       "compressed"],
    comparison:          ["contrarian",      "analyst",          "compressed",       "mechanics",        "profile",         "contrarian"],
    general_crypto:      ["analyst",         "mechanics",        "contrarian",       "compressed",       "profile",         "explainer"],
    dex_aggregator:      ["aggregator_value","swap_guide",       "contrarian",       "compressed",       "aggregator_value","swap_guide"],
  };
  const order = framingOrder[intent] || framingOrder.general_crypto;
  const framingName = order[passIndex % order.length];
  return { framingFn: PROMPT_FRAMINGS[framingName], framingName };
}

/* =========================
   OPENAI CALL
   ========================= */

function shouldRetryStatus(status) {
  return status === 408 || status === 409 || status === 425 || status === 429 || status >= 500;
}

async function fetchWithTimeout(url, options, timeoutMs) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try { return await fetch(url, { ...options, signal: controller.signal }); }
  finally { clearTimeout(id); }
}

async function requestSeoContent({ systemPrompt, userPrompt, temperature }) {
  ensureOpenAiConfig();
  const sys = ensurePrompt(systemPrompt, "System prompt");
  const usr = ensurePrompt(userPrompt, "User prompt");
  let attempt = 0;
  let lastError = null;

  while (attempt < OPENAI_MAX_RETRIES) {
    try {
      const response = await fetchWithTimeout(
        OPENAI_API_URL,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
          body: JSON.stringify({
            model: OPENAI_MODEL, temperature, max_tokens: OPENAI_MAX_TOKENS,
            messages: [{ role: "system", content: sys }, { role: "user", content: usr }],
          }),
        },
        OPENAI_TIMEOUT_MS
      );

      const rawText = await response.text();
      let data = {};
      try { data = rawText ? JSON.parse(rawText) : {}; }
      catch { throw new Error(`OpenAI response invalid JSON: ${rawText.slice(0, 400)}`); }

      if (!response.ok) {
        const err = new Error(data?.error?.message || `OpenAI status ${response.status}`);
        err.retryable = shouldRetryStatus(response.status);
        throw err;
      }

      return sanitizeSeoContent(data?.choices?.[0]?.message?.content || "");
    } catch (error) {
      lastError = error;
      attempt++;
      const aborted   = error?.name === "AbortError";
      const retryable = aborted || error?.retryable === true;
      if (!retryable || attempt >= OPENAI_MAX_RETRIES) {
        if (aborted) throw new Error(`OpenAI timed out after ${OPENAI_TIMEOUT_MS}ms`);
        throw error;
      }
      await sleep(700 * attempt);
    }
  }

  throw lastError || new Error("OpenAI request failed");
}

/* =========================
   CANDIDATE PIPELINE
   ========================= */

async function buildCandidate({ systemPrompt, userPrompt, temperature, keyword, localCtx, framingName }) {
  const raw = await requestSeoContent({ systemPrompt, userPrompt, temperature });
  if (!raw) return null;
  const v = validateSeoContent(raw, keyword, framingName || "");
  return {
    content: v.content || raw,
    score: v.score,
    valid: v.valid,
    temperature,
    framingName: framingName || "",
    contextSummary: localCtx?.contextSummary || "",
  };
}

function computeInsightDensityBonus(content) {
  if (!content) return 0;
  let bonus = 0;

  const sentences = splitSentences(content);
  if (sentences.length >= 6) {
    const lengths = sentences.map((s) => paragraphWordCount(s));
    const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
    const variance = lengths.reduce((a, b) => a + (b - mean) ** 2, 0) / lengths.length;
    const cv = mean > 0 ? Math.sqrt(variance) / mean : 0;
    if (cv >= 0.55) bonus += 3;
    else if (cv >= 0.40) bonus += 1;
  }

  const words = content.toLowerCase().replace(/[^a-z\s]/g, "").split(/\s+/).filter(Boolean);
  if (words.length >= 80) {
    const ttr = new Set(words).size / words.length;
    if (ttr >= 0.74) bonus += 3;
    else if (ttr >= 0.66) bonus += 1;
  }

  const paras = splitSeoParagraphs(content);
  if (paras.length === 4) {
    const grounded = paras.filter((p) =>
      /liquidity|holder|contract|pool|slippage|exit|supply|ownership|distribution|routing|execution|aggregat|solana/.test(p.toLowerCase())
    ).length;
    if (grounded >= 4) bonus += 2;
  }

  return Math.min(bonus, 8);
}

function computeContextUsageBonus(candidate) {
  if (!candidate?.contextSummary || !candidate?.content) return 0;
  // Reward candidates that use specific terms from local context
  const lower = candidate.content.toLowerCase();
  const contextLower = candidate.contextSummary.toLowerCase();
  const specificTerms = (contextLower.match(/\b(raydium|orca|meteora|jupiter|clmm|dlmm|solana|spl|whirlpool|honeypot|renounced|freeze|mint|vesting|tvl|fdv|slippage|price impact|mev|sandwich)\b/g) || []);
  if (!specificTerms.length) return 0;
  const used = unique(specificTerms).filter((t) => lower.includes(t)).length;
  if (used >= 6) return 14;
  if (used >= 4) return 8;
  if (used >= 2) return 4;
  return 0;
}

function scoreCandidateForSort(candidate, keyword) {
  if (!candidate?.content) return -1;
  const v = validateSeoContent(candidate.content, keyword, candidate.framingName || "");
  if (!v.valid) return v.score;
  let s = v.score;
  s += computeInsightDensityBonus(candidate.content);
  s += computeContextUsageBonus(candidate);
  return s;
}

/* =========================
   PASS INPUTS
   ========================= */

function getInitialPassInputs(cleanKeyword, localCtx) {
  const intent = detectSeoIntent(cleanKeyword);
  return INITIAL_TEMPERATURES.map((temperature, i) => {
    const { framingFn, framingName } = selectPromptFraming(cleanKeyword, i);
    const variation = buildPassVariation(localCtx, i);
    const { system, user } = framingFn(cleanKeyword, intent, localCtx, variation);
    return { systemPrompt: system, userPrompt: user, temperature, keyword: cleanKeyword, localCtx, framingName };
  });
}

/* =========================
   OUTPUT GATE
   ========================= */

function applyOutputGate(content, keyword, contextSummary = "") {
  if (!content) throw new Error(`SEO generation produced no content for "${keyword}"`);

  const stripped = content
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<h[1-6][^>]*>[\s\S]*?<\/h[1-6]>/gi, "\n\n")
    .replace(/<li[^>]*>/gi, "\n")
    .replace(/<\/li>/gi, ".\n")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/p>/gi, "\n\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  const sanitized = sanitizeSeoContent(stripped);
  const paragraphs = splitSeoParagraphs(sanitized);

  if (paragraphs.length !== 4) {
    throw new Error(`SEO output had ${paragraphs.length} paragraphs (expected 4) for "${keyword}"`);
  }

  const gated = paragraphs.map((p) => {
    const sentences = splitSentences(p);
    if (sentences.length <= 5) return p;
    const trimmed = sentences.slice(0, 5).join(" ").trim();
    return paragraphWordCount(trimmed) >= 22 ? trimmed : p;
  });

  return gated.join("\n\n").trim();
}

/* =========================
   THIRD-PASS PROMPTS
   ========================= */

// Minimal system for 3rd pass -- detailed structural instructions live in the user prompt.
const THIRD_PASS_SYSTEM =
  "You refine existing crypto analysis. Preserve all specific details -- protocol names, " +
  "numbers, pool references, chain names, DEX names, percentages, dollar amounts. " +
  "Output exactly 4 paragraphs. Plain text. No headings, bullets, or bold. " +
  "No financial advice language.";

function buildRewritePrompt(keyword, content) {
  const intent = detectSeoIntent(normalizeSeoKeyword(keyword));
  const isDex  = intent === "dex_aggregator";
  return `Rewrite this crypto analysis for: "${normalizeSeoKeyword(keyword)}"

Keep every specific detail already in the piece -- protocol names, numbers, pool references, DEX names, percentages, dollar amounts. Those are the best material in the piece.

Read it once. Find where it loses precision. The most likely problems: an opening that describes rather than states the core condition, two paragraphs covering the same signal in different language, or a closing that implies consequence instead of stating it. Fix only what you find. Everything else stays.

${isDex
  ? "Do not open with a definition or a comparison setup. Open on the routing mechanism or execution condition -- the specific gap between direct and aggregated execution."
  : "Do not open with a surface-vs-structure setup or a definition. Open on the structural condition or mechanism directly."}

Paragraph 4 must introduce information not in paragraph 1. Not a consequence restatement -- genuinely new structural or mechanical detail.

4 paragraphs. Plain text. No headings, bullets, or bold. No financial advice language.
Output only the 4 paragraphs.

Original:
${content}`;
}

function buildPolishPrompt(keyword, content) {
  return `Polish this crypto analysis for: "${normalizeSeoKeyword(keyword)}"
Sentence-level changes only. Do not move or merge paragraphs.

One read-through. Find the sentence that sounds most generic -- the one that could appear in any crypto article. Replace it with a more specific structural or mechanical observation drawn from the same paragraph.

Check the first sentence. If it reads as setup or context rather than the core condition stated directly, rewrite it to open on the mechanism itself.

Check the last sentence. If it hedges, warns, or uses advisory language, rewrite it to state the actual consequence. Specific. Present or past tense. No softening.

If two paragraphs open with the same word, change one.

Keep every specific term, number, protocol name, and pool reference already in the piece. Plain text, no formatting.
Output only the 4 paragraphs.

Content:
${content}`;
}

/* =========================
   GENERATION ENTRY
   ========================= */

async function generateSeoBestPass(keyword) {
  const cleanKeyword = normalizeSeoKeyword(keyword);
  if (!cleanKeyword) throw new Error("Keyword is required for SEO generation");

  const intent   = detectSeoIntent(cleanKeyword);
  const localCtx = buildLocalCryptoContext(cleanKeyword, intent);
  const inputs   = getInitialPassInputs(cleanKeyword, localCtx);

  // Both passes run in parallel. Only valid candidates eligible. Hard throw if neither passes.
  const results = await Promise.allSettled(
    inputs.map((input) => buildCandidate(input))
  );

  const candidates = results
    .filter((r) => r.status === "fulfilled" && r.value)
    .map((r) => r.value);

  if (!candidates.length) {
    throw new Error(`Both SEO passes failed for "${cleanKeyword}" -- no content generated`);
  }

  const valid = candidates
    .filter((c) => c.valid)
    .sort((a, b) => scoreCandidateForSort(b, cleanKeyword) - scoreCandidateForSort(a, cleanKeyword));

  if (!valid.length) {
    throw new Error(
      `Both SEO passes produced invalid content for "${cleanKeyword}" -- scores: ${candidates.map((c) => `${c.framingName}:${c.score}`).join(", ")}`
    );
  }

  let best        = valid[0];
  const gap       = best.score - (valid[1]?.score ?? 0);
  const bestScore = best.score;

  // Rewrite: valid but weak -- full structural rewrite beats sentence polish at this score range.
  if (bestScore < REWRITE_SCORE_THRESHOLD) {
    try {
      const rewritten = await requestSeoContent({
        systemPrompt: THIRD_PASS_SYSTEM,
        userPrompt:   buildRewritePrompt(cleanKeyword, best.content),
        temperature:  0.55,
      });
      if (rewritten) {
        const v = validateSeoContent(rewritten, cleanKeyword);
        if (v.valid && v.score >= bestScore - 2) {
          best = { ...best, content: v.content, score: v.score };
        }
      }
    } catch (err) {
      console.error(`[SEO] Rewrite failed for "${cleanKeyword}": ${err.message}`);
    }
  }
  // Polish: both passes close and neither excellent -- sentence-level fixes likely to help.
  // When one pass clearly dominated (gap >= threshold) or both excellent (>= ceiling),
  // take the winner -- no third call.
  else if (bestScore < POLISH_SCORE_CEILING && gap < POLISH_GAP_THRESHOLD) {
    try {
      const polished = await requestSeoContent({
        systemPrompt: THIRD_PASS_SYSTEM,
        userPrompt:   buildPolishPrompt(cleanKeyword, best.content),
        temperature:  0.44,
      });
      if (polished) {
        const v = validateSeoContent(polished, cleanKeyword);
        if (v.valid && v.score >= bestScore - 2) {
          best = { ...best, content: v.content, score: v.score };
        }
      }
    } catch (err) {
      console.error(`[SEO] Polish failed for "${cleanKeyword}": ${err.message}`);
    }
  }

  return applyOutputGate(best.content, cleanKeyword, localCtx.contextSummary);
}

/* =========================
   TEMPLATE OUTPUT
   ========================= */

function buildSeoTemplateFieldsFromContent(content, keyword = "") {
  const paragraphs = splitSeoParagraphs(content);
  const intent     = detectSeoIntent(keyword);
  const subhead    = DEFAULT_SUBHEAD_BY_INTENT[intent] || "Breakdown";
  return {
    AI_HOOK:    paragraphs[0] || "",
    AI_BODY_1:  paragraphs[1] || "",
    AI_BODY_2:  "",
    AI_SUBHEAD: subhead,
    AI_BODY_3:  paragraphs[2] || "",
    AI_LIST:    "",
    AI_CLOSE:   paragraphs[3] || "",
  };
}

async function generateSeoTemplateFields(keyword) {
  const content = await generateSeoBestPass(keyword);
  return buildSeoTemplateFieldsFromContent(content, keyword);
}

/**
 * getTemplateType -- routes a keyword to the correct HTML template.
 * Returns "dex" for DEX aggregator / swap keywords.
 * Returns "risk" for everything else.
 */
function getTemplateType(keyword) {
  const intent = detectSeoIntent(normalizeSeoKeyword(keyword));
  return intent === "dex_aggregator" ? "dex" : "risk";
}

/* =========================
   EXPORTS
   ========================= */

export {
  normalizeSeoKeyword, sanitizeSeoContent, splitSeoParagraphs,
  seoWordCount, paragraphWordCount, splitSentences, countSentences, stableHash,
  detectSeoIntent, buildLocalCryptoContext,
  buildSeoTemplateFieldsFromContent, looksGenericSeo, hasNarrativeMarkers,
  validateSeoContent, generateSeoBestPass, generateSeoTemplateFields,
  applyOutputGate, getTemplateType,
};

// Legacy named exports -- preserved for callers on older import paths
export const buildSeoVariationHint         = () => ({});
export const classifySeoKeyword            = (kw) => ({ intent: detectSeoIntent(kw), contextLabel: detectSeoIntent(kw) });
export const hasSeoFormattingProblems      = (text, kw) => !validateSeoContent(text, kw).valid;
export const finalizeSeoCandidate          = (text, kw) => { const v = validateSeoContent(text, kw); return v.valid ? v.content : null; };
export const scoreSeoContent               = (text, kw) => validateSeoContent(text, kw).score;
export const isUsableSeoCandidate          = (text, kw) => validateSeoContent(text, kw).valid;
export const buildSeoSystemPrompt          = (kw, ctx) => { const intent = detectSeoIntent(kw); const localCtx = buildLocalCryptoContext(kw, intent); const variation = buildPassVariation(localCtx, 0); const { framingFn } = selectPromptFraming(kw, 0); return framingFn(kw, intent, localCtx, variation).system; };
export const buildSeoUserPrompt            = (kw, ctx) => { const intent = detectSeoIntent(kw); const localCtx = buildLocalCryptoContext(kw, intent); const variation = buildPassVariation(localCtx, 0); const { framingFn } = selectPromptFraming(kw, 0); return framingFn(kw, intent, localCtx, variation).user; };
export const buildSeoRewritePrompt         = () => "";
export const polishSeoContentV105          = applyOutputGate;
export const generateSeoBestPassV105       = generateSeoBestPass;
export const generateSeoTemplateFieldsV105 = generateSeoTemplateFields;
export const forceCardSafeSeoContentV106   = applyOutputGate;
export const generateSeoBestPassV106       = generateSeoBestPass;
export const generateSeoTemplateFieldsV106 = generateSeoTemplateFields;

