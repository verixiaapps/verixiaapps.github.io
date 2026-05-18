import os
import re
import sys
import json
from collections import Counter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from data.nexus_dex_clusters import CLUSTERS

KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "nexus_dex_generated_keywords.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "nexus-dex")
SITE = "https://verixiaapps.com"

MAX_LINKS_PER_HUB = 50
TOP_TOPICS_COUNT = 8
MAX_RELATED_TOPICS = 10
MAX_FAQS = 4
MAX_COMMON_SCENARIOS = 5
MAX_COMPARISON_POINTS = 4
MAX_PATTERN_EXAMPLES = 4
REPORT_PATH = os.path.join(OUTPUT_DIR, "_hub_build_report.json")

BRAND_CASE = {
    "nexus dex": "Nexus DEX",
    "hyperliquid": "Hyperliquid",
    "jupiter": "Jupiter",
    "raydium": "Raydium",
    "raydium launchlab": "Raydium LaunchLab",
    "orca": "Orca",
    "drift": "Drift",
    "kamino": "Kamino",
    "pump fun": "Pump Fun",
    "phantom": "Phantom",
    "backpack": "Backpack",
    "solflare": "Solflare",
    "metamask": "MetaMask",
    "coinbase": "Coinbase",
    "binance": "Binance",
    "robinhood": "Robinhood",
    "kraken": "Kraken",
    "bybit": "Bybit",
    "backed finance": "Backed Finance",
    "kalshi": "Kalshi",
    "solana": "Solana",
    "ethereum": "Ethereum",
    "bitcoin": "Bitcoin",
    "base": "Base",
    "bsc": "BSC",
    "arbitrum": "Arbitrum",
    "polygon": "Polygon",
    "avalanche": "Avalanche",
    "btc": "BTC",
    "eth": "ETH",
    "sol": "SOL",
    "usdc": "USDC",
    "usdt": "USDT",
    "bnb": "BNB",
    "bonk": "BONK",
    "wif": "WIF",
    "pepe": "PEPE",
    "doge": "DOGE",
    "shib": "SHIB",
    "trump": "TRUMP",
    "popcat": "POPCAT",
    "jup": "JUP",
    "ray": "RAY",
    "pyth": "PYTH",
    "jto": "JTO",
    "hype": "HYPE",
    "spx": "SPX",
    "ai16z": "ai16z",
    "fartcoin": "FARTCOIN",
    "moodeng": "MOODENG",
    "pnut": "PNUT",
    "goat": "GOAT",
    "griffain": "GRIFFAIN",
    "chillguy": "CHILLGUY",
    "zerebro": "ZEREBRO",
    "xstocks": "xStocks",
    "xstock": "xStock",
    "aaplx": "AAPLx",
    "tslax": "TSLAx",
    "nvdax": "NVDAx",
    "spyx": "SPYx",
    "qqqx": "QQQx",
    "metax": "METAx",
    "mstrx": "MSTRx",
    "msftx": "MSFTx",
    "googlx": "GOOGLx",
    "amznx": "AMZNx",
    "nflxx": "NFLXx",
    "crclx": "CRCLx",
    "aapl": "AAPL",
    "tsla": "TSLA",
    "nvda": "NVDA",
    "spy": "SPY",
    "qqq": "QQQ",
    "msft": "MSFT",
    "googl": "GOOGL",
    "amzn": "AMZN",
    "mstr": "MSTR",
    "nflx": "NFLX",
    "dex": "DEX",
    "cex": "CEX",
    "kyc": "KYC",
    "fdv": "FDV",
    "lp": "LP",
    "spl": "SPL",
    "nft": "NFT",
    "dao": "DAO",
    "evm": "EVM",
    "etf": "ETF",
    "rwa": "RWA",
    "spot etf": "Spot ETF",
    "bitcoin etf": "Bitcoin ETF",
    "ethereum etf": "Ethereum ETF",
    "fomc": "FOMC",
    "cpi": "CPI",
    "gdp": "GDP",
    "nfl": "NFL",
    "nba": "NBA",
    "ufc": "UFC",
    "elon musk": "Elon Musk",
    "super bowl": "Super Bowl",
    "world cup": "World Cup",
    "champions league": "Champions League",
    "premier league": "Premier League",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with"
}

STOPWORDS_FOR_VARIATIONS = {
    "is", "this", "a", "an", "the", "or", "and", "to", "for", "of", "in",
    "on", "by", "with", "from", "how", "what", "where", "best", "can", "i",
    "my", "your", "do", "does", "trade", "trading", "buy", "sell", "swap",
    "no", "kyc", "mobile", "app", "wallet", "only", "without", "verification",
    "signup", "account",
}

LOW_SIGNAL_VARIATION_WORDS = {
    "new", "top", "best", "low", "high", "trending", "viral", "cheapest",
}

HUB_INTROS = {
    "perps-trading": "Perps trading on Nexus DEX lets you long or short crypto with leverage directly from your own wallet. No KYC, no signup, no centralized account, no deposit. Connect a Solana wallet, pick a market, and open a perpetual futures position in seconds.",
    "bitcoin-perps": "Bitcoin perps on Nexus DEX let you long or short BTC with leverage directly from your wallet. Skip the centralized exchange account, the KYC process, and the deposit flow. Trade BTC perpetuals mobile-first from any Solana wallet.",
    "ethereum-perps": "Ethereum perps on Nexus DEX let you long or short ETH with leverage from your wallet. No off-chain account, no identity check, no MetaMask required. Open ETH perpetual positions directly from Phantom, Backpack, or Solflare.",
    "solana-perps": "SOL perps on Nexus DEX let you trade Solana with leverage natively from your wallet. No off-chain account, no friction. Go long or short on SOL from the same wallet you already use for swaps and tokens.",
    "altcoin-perps": "Altcoin and memecoin perps on Nexus DEX cover assets most centralized exchanges do not list. Trade WIF, BONK, PEPE, HYPE, and dozens of trending tokens with leverage directly from your wallet, mobile-first.",
    "hyperliquid-frontend": "Trade Hyperliquid markets directly from a Solana wallet without bridging to Arbitrum or installing MetaMask. Nexus DEX gives you mobile-first access to Hyperliquid perps using Phantom, Backpack, or Solflare.",
    "xstocks-trading": "Trade tokenized U.S. stocks on Nexus DEX directly from a Solana wallet. AAPLx, TSLAx, NVDAx, SPYx, QQQx, and other xStocks live as SPL tokens on Solana, backed 1:1 by real shares held in regulated custody by Backed Finance. No brokerage account, no KYC at the protocol level, 24/7 trading, and full DeFi composability from Phantom, Backpack, or Solflare.",
    "tokenized-stocks": "Tokenized stocks on Nexus DEX bring real U.S. equities on-chain as SPL tokens on Solana. Each token is backed 1:1 by the underlying share held in regulated custody, tradeable 24/7 from your wallet, and fully composable across Solana DeFi. Buy fractional Apple, Tesla, Nvidia, and S&P 500 exposure without a brokerage account.",
    "buy-stocks-onchain": "Buy Apple, Tesla, Nvidia, Microsoft, and dozens of other U.S. stocks on-chain from a Solana wallet. AAPLx, TSLAx, NVDAx, MSFTx, GOOGLx, AMZNx, METAx, MSTRx, SPYx, QQQx, and more trade as SPL tokens via Nexus DEX aggregation across Jupiter, Raydium, and Orca. No broker, no KYC at the protocol level.",
    "stocks-no-kyc": "Buy U.S. stocks without KYC, brokerage signup, or ID verification. Tokenized xStocks on Solana trade as SPL tokens from your wallet, so you skip the broker account, the identity check, and the deposit flow. Connect Phantom or Backpack and trade AAPLx, TSLAx, NVDAx, SPYx straight from your wallet.",
    "stocks-24-7": "Trade U.S. stocks 24/7 on Nexus DEX. Tokenized stocks on Solana never close — buy and sell AAPLx, TSLAx, NVDAx, SPYx, QQQx, and other xStocks on weekends, after hours, and through holidays directly from a Solana wallet. No market hours, no broker queue.",
    "global-stock-access": "Buy U.S. stocks from anywhere in the world via tokenized xStocks on Solana. Non-U.S. residents in Europe, Asia, India, Brazil, Africa, and LATAM can get Apple, Tesla, Nvidia, and S&P 500 exposure without a U.S. bank account, brokerage, or KYC. Just a Solana wallet funded with USDC.",
    "prediction-markets": "Prediction markets on Nexus DEX let you trade outcomes on crypto prices, politics, sports, and economic events directly from your wallet. No KYC, no signup, mobile-first, with markets resolving from minutes to months.",
    "solana-swap": "Swap any Solana token on Nexus DEX with best-price routing across Jupiter, Raydium, and Orca. Connect Phantom or Backpack, paste a token address, and trade SPL tokens with low slippage and no centralized account.",
    "buy-token": "Buy any Solana token directly from your wallet, memecoins, AI tokens, new listings, Pump Fun graduates. Nexus DEX aggregates liquidity across Jupiter, Raydium, and Orca so you get the best price without signup or KYC.",
    "no-kyc-trading": "No-KYC trading on Nexus DEX means no identity verification, no account creation, and no centralized custody. Connect a wallet, sign a transaction, and trade perps, spot, tokenized stocks, or prediction markets without ever sharing personal data.",
    "whale-tracking": "Track Solana whales, smart money, and memecoin insiders in real time. Nexus DEX surfaces top traders, early buyers, deployer clusters, and KOL wallets so you can see who is accumulating before the chart moves.",
    "token-launch": "Launch a Solana token from your wallet without code, KYC, or upfront fees. Deploy memecoins via bonding curve, graduate to Raydium liquidity, and reach buyers without going through Pump Fun or third-party launchpads.",
    "wallet-trading": "Trade fully self-custodial from Phantom, Backpack, or Solflare. Nexus DEX never holds your funds, never requires KYC, and never asks you to deposit. Your wallet is your account, and every trade settles on-chain.",
    "how-to-guides": "Step-by-step guides for trading perps, betting on prediction markets, launching tokens, and tracking whales using Nexus DEX. Built for Solana wallet users who want to skip centralized exchanges and KYC entirely.",
}

HUB_TITLES = {
    "perps-trading": "Perps Trading on Nexus DEX: Features, Leverage & How To Start",
    "bitcoin-perps": "Bitcoin Perps on Nexus DEX: Long, Short & Leverage From Your Wallet",
    "ethereum-perps": "Ethereum Perps on Nexus DEX: ETH Long, Short & Leverage Trading",
    "solana-perps": "SOL Perps on Nexus DEX: Solana Leverage Trading From Your Wallet",
    "altcoin-perps": "Altcoin & Memecoin Perps: WIF, BONK, PEPE Leverage Trading",
    "hyperliquid-frontend": "Trade Hyperliquid From Solana: Mobile, Wallet-Based, No MetaMask",
    "xstocks-trading": "xStocks on Nexus DEX: Trade AAPL, TSLA, NVDA Tokenized Stocks From Your Wallet",
    "tokenized-stocks": "Tokenized Stocks on Solana: Trade Apple, Tesla, Nvidia On-Chain",
    "buy-stocks-onchain": "Buy Apple, Tesla, Nvidia & More On Solana: xStocks From Your Wallet",
    "stocks-no-kyc": "Buy U.S. Stocks With No KYC: xStocks From a Solana Wallet",
    "stocks-24-7": "Trade Stocks 24/7 On-Chain: Weekends, After Hours, No Market Close",
    "global-stock-access": "Buy U.S. Stocks Globally: xStocks From Europe, Asia, India, LATAM",
    "prediction-markets": "Prediction Markets: Bet on BTC, ETH, Elections & Sports From Wallet",
    "solana-swap": "Solana DEX Aggregator: Best Price Swaps, No KYC, Mobile",
    "buy-token": "Buy Solana Tokens: Memecoins, New Launches & SPL Tokens From Wallet",
    "no-kyc-trading": "No KYC Trading: Perps, Swaps, Stocks & Prediction Markets From Wallet",
    "whale-tracking": "Solana Whale Tracking: Smart Money, Insiders & Early Buyers",
    "token-launch": "Launch a Solana Token: No KYC, From Your Wallet, Mobile",
    "wallet-trading": "Wallet-Based Trading: Self-Custodial Perps, Swaps & Prediction",
    "how-to-guides": "Nexus DEX How-To Guides: Trading, Launching, Whale Tracking",
}

HUB_META_DESCRIPTIONS = {
    "perps-trading": "Trade crypto perps with leverage on Nexus DEX. No KYC, no signup, no centralized account. Long or short BTC, ETH, SOL, and altcoins from your wallet.",
    "bitcoin-perps": "Long or short Bitcoin with leverage on Nexus DEX. Trade BTC perpetuals directly from your Solana wallet with no KYC, no account, and mobile-first access.",
    "ethereum-perps": "Long or short Ethereum with leverage on Nexus DEX. Trade ETH perpetuals from your Solana wallet with no MetaMask, no account, and no KYC requirements.",
    "solana-perps": "Long or short SOL with leverage on Nexus DEX. Trade Solana perpetuals natively from the same wallet you use for spot, with no off-chain account or KYC.",
    "altcoin-perps": "Trade altcoin and memecoin perps on Nexus DEX: WIF, BONK, PEPE, HYPE, and more. Leverage trading from your wallet with no KYC, no signup, and mobile-first access.",
    "hyperliquid-frontend": "Use Hyperliquid from a Solana wallet on Nexus DEX. Mobile-first, no MetaMask, no bridging to Arbitrum. Trade Hyperliquid perps directly from Phantom or Backpack.",
    "xstocks-trading": "Trade tokenized U.S. stocks on Nexus DEX from a Solana wallet. AAPLx, TSLAx, NVDAx, SPYx 24/7 with no brokerage account and no KYC at the protocol level.",
    "tokenized-stocks": "Trade tokenized stocks on Solana from your wallet. Apple, Tesla, Nvidia, S&P 500 as SPL tokens with 24/7 trading, fractional positions, and no brokerage account.",
    "buy-stocks-onchain": "Buy AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN, SPY, QQQ on Solana as xStocks. Wallet-based, 24/7, no broker, fractional positions, and DeFi composable.",
    "stocks-no-kyc": "Buy U.S. stocks with no KYC, no broker signup, and no ID check. xStocks on Solana trade as SPL tokens directly from Phantom, Backpack, or Solflare.",
    "stocks-24-7": "Trade tokenized U.S. stocks 24/7 on Solana. AAPLx, TSLAx, NVDAx, SPYx never close — buy and sell on weekends, after hours, and holidays from your wallet.",
    "global-stock-access": "Buy U.S. stocks from Europe, Asia, India, LATAM, and Africa via xStocks on Solana. No U.S. bank, no broker, no KYC at the protocol level. Just a wallet and USDC.",
    "prediction-markets": "Prediction markets on Nexus DEX let you bet on crypto prices, elections, sports, and Fed decisions from your wallet. No KYC, no signup, mobile-first access.",
    "solana-swap": "Swap any Solana token on Nexus DEX with best-price routing across Jupiter, Raydium, and Orca. No KYC, no account, mobile-first, low slippage.",
    "buy-token": "Buy Solana tokens, memecoins, and new launches directly from your wallet on Nexus DEX. Best-price routing across Jupiter, Raydium, and Orca with no signup or KYC.",
    "no-kyc-trading": "No-KYC trading on Nexus DEX covers perps, spot, tokenized stocks, and prediction markets. Connect a wallet, sign a transaction, and trade without sharing data.",
    "whale-tracking": "Track Solana whales, smart money, memecoin insiders, deployer clusters, and KOL wallets on Nexus DEX. See who is accumulating before the chart moves.",
    "token-launch": "Launch a Solana token from your wallet on Nexus DEX. No KYC, no code, no upfront fees. Deploy memecoins via bonding curve and graduate to Raydium liquidity.",
    "wallet-trading": "Self-custodial trading on Nexus DEX from Phantom, Backpack, or Solflare. Your wallet is your account. Every trade settles on-chain with no deposit and no KYC.",
    "how-to-guides": "Step-by-step Nexus DEX guides for perps trading, prediction markets, token launches, whale tracking, and swaps from a Solana wallet without KYC.",
}

HUB_KEY_FEATURES = {
    "perps-trading": [
        "Long or short BTC, ETH, SOL, and altcoin perpetual futures with up to 50x leverage",
        "No KYC, no signup, no centralized account, no deposit required",
        "Connect any Solana wallet (Phantom, Backpack, Solflare) and trade in seconds",
        "Mobile-first interface built for fast position entry and management",
    ],
    "bitcoin-perps": [
        "Long or short BTC with leverage directly from your Solana wallet",
        "No off-chain account, no KYC, no deposit flow to navigate",
        "Live funding rates, open interest, and live BTC perp price",
        "Mobile-first execution with isolated or cross margin",
    ],
    "ethereum-perps": [
        "Long or short ETH with leverage from a Solana wallet, no MetaMask required",
        "No off-chain account, no identity check, no bridging to Ethereum",
        "Live ETH funding rates, perp price, and open interest data",
        "Mobile-first execution from Phantom, Backpack, or Solflare",
    ],
    "solana-perps": [
        "Trade SOL with leverage natively from the same wallet you use for spot",
        "No off-chain account, no KYC, no deposit step",
        "Live SOL funding rates, open interest, and perp price",
        "Cross or isolated margin, mobile-first execution",
    ],
    "altcoin-perps": [
        "Perps on memecoins and altcoins most centralized exchanges do not list",
        "Coverage of WIF, BONK, PEPE, HYPE, POPCAT, and other trending tokens",
        "Leverage trading directly from your Solana wallet, no KYC required",
        "Mobile-first access to new listings the same day they go live",
    ],
    "hyperliquid-frontend": [
        "Trade Hyperliquid markets from a Solana wallet, no Arbitrum bridge needed",
        "No MetaMask, no second wallet, no centralized account",
        "Full Hyperliquid order book and depth from a mobile-first interface",
        "Use Phantom, Backpack, or Solflare with familiar Solana flows",
    ],
    "xstocks-trading": [
        "Trade 60+ tokenized U.S. stocks and ETFs (AAPLx, TSLAx, NVDAx, SPYx, QQQx) as SPL tokens",
        "Each xStock is backed 1:1 by the real underlying share in regulated Swiss custody",
        "24/7 trading from your wallet, no brokerage account and no market hours",
        "Composable across Solana DeFi: LP on Raydium, collateralize on Kamino, swap via Jupiter",
    ],
    "tokenized-stocks": [
        "Real U.S. equities on-chain as SPL tokens with 1:1 backing in regulated custody",
        "Fractional positions, so a few dollars of TSLA or NVDA is fine",
        "24/7 trading from a Solana wallet, no broker and no waiting for market open",
        "Composable in Solana DeFi: LP, lend, borrow, and route through DEX aggregators",
    ],
    "buy-stocks-onchain": [
        "Buy AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN, META, MSTR, COIN, NFLX, AMD, SPY, QQQ as xStocks",
        "Best-price routing across Jupiter, Raydium, and Orca for every stock-token trade",
        "Fractional buys from any amount, paid in USDC or SOL from your wallet",
        "Self-custodial — your stock tokens live in your Phantom or Backpack wallet",
    ],
    "stocks-no-kyc": [
        "No brokerage signup, no SSN, no ID upload at the protocol level",
        "Wallet-based access from Phantom, Backpack, or Solflare with USDC funding",
        "Same stocks the major brokers list (AAPL, TSLA, NVDA, SPY) as SPL tokens",
        "Self-custodial — funds and stock tokens stay in your wallet, not a broker account",
    ],
    "stocks-24-7": [
        "Tokenized stocks trade around the clock on Solana DEXes, even when Wall Street is closed",
        "Buy or sell on weekends, after hours, and during U.S. holidays",
        "Same SPL token flow as any other Solana asset — instant settlement to your wallet",
        "Useful for reacting to news and earnings without waiting for the next open",
    ],
    "global-stock-access": [
        "Non-U.S. residents can buy AAPL, TSLA, NVDA, SPY exposure without a U.S. bank account",
        "Works from Europe, Asia, India, LATAM, Africa — anywhere with internet and a wallet",
        "Fund with USDC from any source, no domestic broker required",
        "Self-custodial — no broker can geo-block, freeze, or close your account",
    ],
    "prediction-markets": [
        "Bet on BTC, ETH, SOL price levels with short and long resolution windows",
        "Markets on elections, Fed decisions, sports outcomes, and major events",
        "Self-custodial, wallet-based, no KYC and no signup required",
        "Mobile-first interface with live odds and quick position entry",
    ],
    "solana-swap": [
        "Best-price routing across Jupiter, Raydium, and Orca aggregators",
        "Swap any SPL token with low slippage and no centralized account",
        "Mobile-first interface from Phantom, Backpack, or Solflare",
        "Paste a contract address and trade in seconds without signup",
    ],
    "buy-token": [
        "Buy any Solana token from memecoins to AI tokens to new launches",
        "Best-price aggregation across Jupiter, Raydium, and Orca",
        "Direct wallet flow with no centralized exchange listing required",
        "Mobile-first execution from Phantom, Backpack, or Solflare",
    ],
    "no-kyc-trading": [
        "No identity verification, no account creation, no document uploads",
        "Self-custodial, wallet-based, with funds always under your control",
        "Covers perps, spot swaps, tokenized stocks, and prediction markets in one interface",
        "Mobile-first, accessible from any Solana wallet",
    ],
    "whale-tracking": [
        "Real-time tracking of top traders, early buyers, and deployer wallets",
        "Smart money flow analysis across memecoins and trending tokens",
        "Pre-pump buyer detection and sniper cluster identification",
        "KOL wallet monitoring and holder concentration breakdowns",
    ],
    "token-launch": [
        "Deploy a Solana token from your wallet with no code or KYC required",
        "Bonding curve launchpad with automatic Raydium graduation",
        "No upfront fees, no presale gatekeeping, no third-party platform",
        "Mobile-first launch flow accessible from Phantom or Backpack",
    ],
    "wallet-trading": [
        "Fully self-custodial across perps, swaps, stocks, and prediction markets",
        "Nexus DEX never holds funds, never custodies, never freezes accounts",
        "Every trade settles on-chain from your wallet signature",
        "Works with Phantom, Backpack, Solflare, and other Solana wallets",
    ],
    "how-to-guides": [
        "Step-by-step walkthroughs for perps, swaps, and prediction markets",
        "Wallet setup and first-trade guides for new Solana users",
        "Whale tracking and smart money analysis tutorials",
        "Token launch guides covering bonding curves and Raydium graduation",
    ],
}

HUB_FAQS = {
    "perps-trading": [
        ("Do I need to sign up or complete KYC?", "No. Nexus DEX perps trading requires only a connected Solana wallet. There is no account creation, no identity verification, and no document upload."),
        ("Which wallets can I use?", "Phantom, Backpack, Solflare, and other major Solana wallets are supported. You sign each trade from your wallet and funds stay in your wallet between positions."),
    ],
    "bitcoin-perps": [
        ("Can I trade BTC perps without KYC?", "Yes. BTC perps on Nexus DEX are accessible from a connected Solana wallet without any identity verification or account creation."),
        ("What leverage is available?", "Leverage tiers depend on market conditions, but BTC perps typically support up to 50x with both isolated and cross margin modes."),
    ],
    "ethereum-perps": [
        ("Do I need MetaMask to trade ETH perps?", "No. ETH perps on Nexus DEX work from a Solana wallet like Phantom or Backpack. There is no need to install MetaMask or hold ETH on Ethereum mainnet."),
        ("Can I short ETH on mobile?", "Yes. The entire perps interface is mobile-first, including position entry, leverage selection, and order management."),
    ],
    "solana-perps": [
        ("Can I trade SOL perps from the same wallet I use for swaps?", "Yes. SOL perps work from any standard Solana wallet, so you can trade leverage and spot tokens from the same Phantom or Backpack wallet."),
        ("What is the funding rate?", "Funding rates are displayed live on the SOL perp market page. They update on a fixed interval and apply to open positions."),
    ],
    "altcoin-perps": [
        ("Which altcoins have perp markets?", "Coverage includes WIF, BONK, PEPE, HYPE, POPCAT, and other trending Solana and major-chain tokens. New listings are added as liquidity supports them."),
        ("How quickly do new perp markets get listed?", "New perp markets typically launch within days of meaningful liquidity forming, often the same day on trending tokens."),
    ],
    "hyperliquid-frontend": [
        ("Do I need a separate Hyperliquid account?", "No. Nexus DEX routes to Hyperliquid markets from your existing Solana wallet, so there is no separate signup or Arbitrum wallet required."),
        ("Is this the official Hyperliquid app?", "No. Nexus DEX is a wallet-based frontend that connects Solana wallets to Hyperliquid liquidity without requiring MetaMask or an Arbitrum bridge."),
    ],
    "xstocks-trading": [
        ("What are xStocks?", "xStocks are tokenized 1:1 representations of real U.S. stocks and ETFs (like AAPLx for Apple, TSLAx for Tesla, NVDAx for Nvidia) issued by Backed Finance, a Swiss-regulated entity acquired by Kraken in December 2025. Each token is backed by the underlying share held in regulated custody, and they live on Solana as SPL tokens."),
        ("Do I need a brokerage account or KYC?", "No. xStocks trade as SPL tokens, so there is no brokerage signup at the protocol level. Connect a Solana wallet, fund it with USDC or SOL, and trade. Note that availability and tax treatment depend on your jurisdiction, so check local rules before trading."),
        ("Do I get dividends and voting rights?", "Dividends are passed on automatically through a rebasing multiplier, so your xStock balance increases when the underlying pays a dividend. xStocks do not carry shareholder voting rights or a direct legal claim to the underlying company shares."),
        ("Can I use xStocks in DeFi?", "Yes. xStocks are composable SPL tokens. You can LP them on Raydium or Orca, use them as collateral on Kamino, and route swaps through Jupiter just like any other Solana asset."),
    ],
    "prediction-markets": [
        ("What kinds of markets are available?", "Crypto price levels (BTC, ETH, SOL), elections, Fed rate decisions, sports outcomes, and major event predictions. Resolution windows range from minutes to months."),
        ("How do markets resolve?", "Each market has a defined resolution source and timestamp. After the event resolves, winning positions can be redeemed for the payout from your wallet."),
    ],
    "solana-swap": [
        ("How is Nexus DEX different from Jupiter directly?", "Nexus DEX aggregates Jupiter, Raydium, and Orca to find the best price across all three. You get the same liquidity with mobile-first UX and integrated perps and prediction markets."),
        ("Do I need to switch wallets?", "No. The same Solana wallet handles swaps, perps, and prediction markets across the entire Nexus DEX interface."),
    ],
    "buy-token": [
        ("How do I buy a token I cannot find on Coinbase?", "Paste the token contract address into Nexus DEX. The aggregator finds the best route across Jupiter, Raydium, and Orca and executes the swap from your wallet."),
        ("Can I buy new memecoins right after launch?", "Yes, as soon as liquidity exists on a supported DEX. Nexus DEX picks up new pairs automatically and routes through them."),
    ],
    "no-kyc-trading": [
        ("Is no-KYC trading legal?", "Self-custodial wallet trading is legal in most jurisdictions, but tax and reporting obligations may still apply. Nexus DEX does not provide tax or legal advice."),
        ("What if I lose access to my wallet?", "Because Nexus DEX is non-custodial, your wallet's seed phrase is the only recovery method. Back it up securely. Nexus DEX cannot recover funds for you."),
    ],
    "whale-tracking": [
        ("What counts as smart money?", "Wallets with consistent profitable trades, early entries on tokens that pumped, and deployer clusters with track records. Nexus DEX surfaces these wallets and their current positions."),
        ("Can I follow specific wallets?", "Yes. The whale tracker lets you follow individual wallets and get alerts when they buy, sell, or accumulate."),
    ],
    "token-launch": [
        ("Do I need to write code to launch a token?", "No. The launchpad is no-code. You name the token, set basic parameters, and deploy from your wallet."),
        ("How does Raydium graduation work?", "Once a token's bonding curve hits the graduation threshold, liquidity is automatically migrated to a Raydium pool. From there it trades as a standard SPL token."),
    ],
    "wallet-trading": [
        ("Does Nexus DEX ever hold my funds?", "No. Funds stay in your wallet between trades. Each trade is signed from your wallet and settles on-chain."),
        ("What happens if Nexus DEX goes offline?", "Your funds remain in your wallet because Nexus DEX never custodies them. You retain full control regardless of the platform's status."),
    ],
    "how-to-guides": [
        ("Where should I start if I am new to Solana wallets?", "Start with the wallet setup guide. It covers creating a Phantom or Backpack wallet, funding it with SOL, and connecting to Nexus DEX for your first trade."),
        ("Do the guides cover mobile?", "Yes. Every guide is written mobile-first because the entire Nexus DEX interface is designed for mobile execution."),
    ],
}

GENERIC_FAQS = [
    ("Do I need an account or KYC to use Nexus DEX?", "No. Nexus DEX is fully self-custodial. Connect a Solana wallet, sign a transaction, and trade. There is no signup, no KYC, and no centralized account."),
    ("Which wallets are supported?", "Phantom, Backpack, Solflare, and other major Solana wallets work with Nexus DEX. You sign each trade from your wallet and funds stay in your wallet between trades."),
]

HUB_GET_STARTED_STEPS = {
    "perps-trading": [
        "Install Phantom, Backpack, or Solflare and fund it with SOL or USDC.",
        "Connect your wallet to Nexus DEX and open the perps interface.",
        "Pick a market (BTC, ETH, SOL, or altcoin), set leverage, and sign the position from your wallet.",
    ],
    "bitcoin-perps": [
        "Connect a Solana wallet with SOL or USDC for margin.",
        "Open the BTC perp market and pick long or short with your chosen leverage.",
        "Sign the position from your wallet. Manage stops and take-profits from the same screen.",
    ],
    "ethereum-perps": [
        "Connect a Solana wallet (Phantom, Backpack, or Solflare) and fund it with USDC.",
        "Open the ETH perp market and pick direction and leverage.",
        "Sign the position from your wallet. No MetaMask, no Ethereum gas required.",
    ],
    "solana-perps": [
        "Connect the same Solana wallet you use for swaps.",
        "Open the SOL perp market and choose long, short, or hedging configuration.",
        "Sign the position from your wallet and monitor live funding rates.",
    ],
    "altcoin-perps": [
        "Connect a Solana wallet with USDC for margin.",
        "Browse listed altcoin perps (WIF, BONK, PEPE, HYPE, etc.) and pick a market.",
        "Set leverage, pick direction, and sign the position from your wallet.",
    ],
    "hyperliquid-frontend": [
        "Connect a Solana wallet (Phantom, Backpack, Solflare). No MetaMask needed.",
        "Open the Hyperliquid markets section inside Nexus DEX.",
        "Pick a market, set leverage and direction, and sign from your wallet.",
    ],
    "xstocks-trading": [
        "Connect a Solana wallet (Phantom, Backpack, or Solflare) funded with USDC or SOL.",
        "Search for a ticker like AAPLx, TSLAx, NVDAx, SPYx, or QQQx inside Nexus DEX.",
        "Review the best-price route across Jupiter, Raydium, and Orca, then sign the swap from your wallet.",
    ],
    "prediction-markets": [
        "Connect a Solana wallet with USDC for position collateral.",
        "Browse prediction markets by category (crypto, politics, sports, economics).",
        "Pick a market, take a yes or no side, and sign the position from your wallet.",
    ],
    "solana-swap": [
        "Connect a Solana wallet funded with SOL or USDC.",
        "Paste a token contract address or pick a token from the list.",
        "Review the route and price, then sign the swap from your wallet.",
    ],
    "buy-token": [
        "Connect a Solana wallet funded with SOL or USDC.",
        "Search by token symbol or paste the contract address.",
        "Review best-price route across Jupiter, Raydium, and Orca, then sign the swap.",
    ],
    "no-kyc-trading": [
        "Install a Solana wallet (Phantom, Backpack, or Solflare).",
        "Fund the wallet with SOL or USDC from any source you control.",
        "Connect to Nexus DEX and trade perps, spot, stocks, or prediction markets. No identity check required.",
    ],
    "whale-tracking": [
        "Open the whale tracker section inside Nexus DEX.",
        "Browse top traders, early buyers, or deployer wallets by category.",
        "Follow individual wallets or set alerts for accumulation patterns.",
    ],
    "token-launch": [
        "Connect a Solana wallet funded with a small amount of SOL for the deployment.",
        "Open the launchpad, set token name, ticker, and supply.",
        "Sign the deployment transaction from your wallet. The bonding curve goes live immediately.",
    ],
    "wallet-trading": [
        "Install a Solana wallet and back up your seed phrase securely.",
        "Fund the wallet with SOL or USDC from any source you control.",
        "Connect to Nexus DEX. Every trade is signed from your wallet and settles on-chain.",
    ],
    "how-to-guides": [
        "Start with the wallet setup guide if you are new to Solana.",
        "Pick the trading guide matching your goal (perps, prediction, swap, launch).",
        "Follow the step-by-step walkthrough using a small test amount first.",
    ],
}

HUB_HOW_IT_WORKS = {
    "perps-trading": "Nexus DEX perps route through on-chain perpetual futures markets. Your wallet posts USDC margin, opens a leveraged position, and settles the PnL on-chain. There is no centralized order book holding your funds.",
    "bitcoin-perps": "BTC perp positions on Nexus DEX are collateralized by USDC in your wallet. The position opens against an on-chain market, tracks the BTC perp price live, and settles directly from your wallet signature.",
    "ethereum-perps": "ETH perp positions use USDC collateral from your Solana wallet. The position tracks an on-chain ETH perp market without requiring you to hold ETH on Ethereum mainnet or pay Ethereum gas.",
    "solana-perps": "SOL perp positions use USDC collateral. The market tracks the SOL perp price live, applies funding rates on a fixed interval, and settles PnL from your wallet signature.",
    "altcoin-perps": "Altcoin perps work the same way as BTC, ETH, and SOL perps. Your wallet posts USDC margin, opens leverage against a listed altcoin market, and settles PnL on-chain.",
    "hyperliquid-frontend": "Nexus DEX provides a wallet-based interface to Hyperliquid markets. Your Solana wallet signs trades that route through to Hyperliquid liquidity without requiring you to bridge to Arbitrum or use MetaMask.",
    "xstocks-trading": "xStocks are issued by Backed Finance as SPL tokens on Solana, with each token backed 1:1 by the underlying U.S. share held in regulated Swiss custody. Trades route through Solana DEXes like Raydium and Orca via Jupiter's aggregation and settle directly to your wallet. Dividends are passed on automatically through a rebasing multiplier that updates your token balance, and corporate actions like stock splits adjust the same way. You can hold xStocks in your Solana wallet, LP them, or use them as collateral in Kamino just like any other SPL token.",
    "prediction-markets": "Each prediction market is an outcome contract with a defined resolution source. You take a yes or no side, the position is collateralized from your wallet, and the contract pays winners automatically at resolution.",
    "solana-swap": "Nexus DEX queries Jupiter, Raydium, and Orca for the best price on your swap. The selected route is executed in a single transaction signed from your wallet.",
    "buy-token": "When you buy a token, Nexus DEX finds the best price across Jupiter, Raydium, and Orca, including aggregator hops if they reduce slippage. Your wallet signs one transaction and the trade settles instantly.",
    "no-kyc-trading": "Every trade type on Nexus DEX, whether perp, spot, xStocks, or prediction, settles from your wallet signature. There is no off-chain account, no identity check, and no custodial wrapper between you and the market.",
    "whale-tracking": "The whale tracker indexes on-chain trading activity across Solana, ranks wallets by profitability and timing, and surfaces patterns like accumulation, deployer clusters, and sniper behavior.",
    "token-launch": "The launchpad deploys an SPL token, attaches a bonding curve for early trading, and automatically migrates liquidity to Raydium once the graduation threshold is hit. Everything is signed from your wallet.",
    "wallet-trading": "Nexus DEX is fully non-custodial. Your wallet holds the funds, signs the transactions, and receives the proceeds. The platform never takes custody and cannot freeze, pause, or reverse your trades.",
    "how-to-guides": "Each guide walks through one specific Nexus DEX workflow end-to-end. Steps cover wallet setup, funding, the action itself, and what to expect at each stage.",
}

HUB_TARGETING = {
    "perps-trading": "This is for traders who want leverage without a centralized exchange account. Common users include Solana-native traders, mobile-first users, and people exiting Binance, Coinbase, or other CEXes after KYC or geography issues.",
    "bitcoin-perps": "BTC perp users typically want directional exposure with leverage but do not want to KYC or hold funds on a centralized exchange. Many are Solana-native and want to keep collateral in their existing wallet.",
    "ethereum-perps": "ETH perp users typically want leverage on ETH without bridging back to Ethereum mainnet, paying Ethereum gas, or maintaining a separate MetaMask wallet.",
    "solana-perps": "SOL perp users are usually already active on Solana for swaps and tokens. They want leverage on SOL from the same wallet without moving funds to a centralized exchange.",
    "altcoin-perps": "Altcoin perp users are typically memecoin traders, low-cap speculators, and people looking for leverage on assets centralized exchanges do not list.",
    "hyperliquid-frontend": "This is for Solana-native traders who want Hyperliquid liquidity but do not want to install MetaMask, bridge to Arbitrum, or maintain a second wallet.",
    "xstocks-trading": "xStocks users include non-U.S. residents who want easier access to U.S. equities without a traditional brokerage account, crypto-native investors who want stock exposure that lives inside DeFi, and retail traders who want fractional positions, 24/7 access, and self-custody instead of relying on a broker.",
    "prediction-markets": "Prediction market users include crypto price speculators, political and election bettors, sports outcome traders, and macro-focused users tracking Fed decisions and economic data.",
    "solana-swap": "This is for anyone swapping SPL tokens who wants best-price routing without juggling Jupiter, Raydium, and Orca interfaces separately, or who prefers a mobile-first interface.",
    "buy-token": "Buy-token users include memecoin traders, new-launch speculators, AI token buyers, and anyone trying to acquire a Solana token that is not listed on a centralized exchange.",
    "no-kyc-trading": "No-KYC users include privacy-focused traders, users in jurisdictions with limited centralized exchange access, and crypto-native users who prefer self-custody as a default.",
    "whale-tracking": "Whale tracking users are typically memecoin traders, smart-money followers, and analysts who want to see accumulation, deployer behavior, or early-buyer patterns before public visibility.",
    "token-launch": "Token launch users include memecoin creators, community founders, and people testing token ideas without paying upfront launchpad fees or going through KYC gatekeeping.",
    "wallet-trading": "Wallet-trading users include anyone burned by centralized exchange custody issues, privacy-focused traders, and Solana-native users who want everything to settle from their own wallet.",
    "how-to-guides": "Guide readers include new Solana wallet users, traders migrating from centralized exchanges, and existing users learning a specific Nexus DEX feature for the first time.",
}

INTRO_FALLBACK = (
    "This hub groups together related Nexus DEX pages so you can review features, compare use cases, and quickly navigate to the most relevant trading topics in this category."
)

META_FALLBACK = (
    "Explore Nexus DEX features, compare related trading topics, and learn how each workflow plays out from a self-custodial Solana wallet."
)

GENERIC_ENTITY_WORDS = {
    "perps", "perp", "trade", "trading", "trader", "swap", "swaps", "buy", "sell",
    "leverage", "leveraged", "mobile", "app", "wallet", "wallets", "account",
    "no", "kyc", "signup", "without", "verification", "from", "to", "with",
    "for", "on", "in", "is", "a", "an", "the", "this", "what", "how", "where",
    "why", "can", "should", "do", "does", "best", "new", "top", "low", "high",
    "trending", "viral", "cheapest", "live", "price", "open", "interest",
    "funding", "rate", "long", "short", "hedge", "amplify", "bet", "betting",
    "yes", "no",
}

CHANNEL_HINTS = {
    "mobile": "mobile-first",
    "app": "mobile-first",
    "wallet": "wallet-based",
    "phantom": "wallet-based",
    "backpack": "wallet-based",
    "solflare": "wallet-based",
    "metamask": "wallet-based",
    "solana": "Solana-native",
    "spl": "Solana-native",
    "ethereum": "Ethereum-native",
    "eth": "Ethereum-native",
    "arbitrum": "Arbitrum-native",
    "polygon": "Polygon-native",
    "bsc": "BSC-native",
    "base": "Base-native",
}

INTENT_HINTS = {
    "kyc": "no-KYC access",
    "signup": "no-signup access",
    "account": "no-account access",
    "verification": "no-verification access",
    "leverage": "leveraged exposure",
    "perp": "perpetual futures",
    "perps": "perpetual futures",
    "perpetual": "perpetual futures",
    "swap": "spot swaps",
    "buy": "spot buys",
    "bet": "prediction market bets",
    "prediction": "prediction market positions",
    "hyperliquid": "Hyperliquid liquidity",
    "whale": "whale and smart-money tracking",
    "smart": "whale and smart-money tracking",
    "launch": "token launching",
    "launchpad": "token launching",
    "hedge": "hedging strategies",
    "xstocks": "tokenized stock exposure",
    "xstock": "tokenized stock exposure",
    "stocks": "tokenized stock exposure",
    "stock": "tokenized stock exposure",
    "equity": "tokenized equity exposure",
    "equities": "tokenized equity exposure",
    "tokenized": "tokenized asset exposure",
}

GENERIC_COMPARISON_POINTS = [
    (
        "Nexus DEX is self-custodial and wallet-based. Funds stay in your wallet between trades.",
        "Centralized exchanges custody your funds and can freeze, pause, or restrict withdrawals."
    ),
    (
        "Nexus DEX requires no signup, no KYC, and no document upload. You connect a wallet and trade.",
        "Centralized exchanges require account creation, identity verification, and often geographic eligibility."
    ),
    (
        "Nexus DEX settles every trade on-chain from your wallet signature.",
        "Centralized exchanges settle internally on an off-chain ledger you cannot independently verify."
    ),
]

HUB_COMPARISON_POINTS = {
    "perps-trading": [
        (
            "Open a perp position by signing one transaction from your Solana wallet. Margin stays in your wallet between positions.",
            "Open a CEX perp position by depositing funds to the exchange first, then opening leverage on their internal ledger."
        ),
        (
            "No KYC, no document upload, no geographic gating to start trading.",
            "Centralized perp venues require KYC, identity documents, and often block users by geography."
        ),
    ],
    "bitcoin-perps": [
        (
            "Trade BTC perps from a Solana wallet with USDC margin, no off-chain account required.",
            "Trade BTC perps on a CEX after KYC, deposit, and account setup specific to that platform."
        ),
        (
            "Funds remain in your wallet between trades and cannot be frozen by the platform.",
            "CEX BTC positions sit on the exchange's books and depend on the platform's solvency and policies."
        ),
    ],
    "ethereum-perps": [
        (
            "Trade ETH perps from a Solana wallet without holding ETH on Ethereum mainnet or paying Ethereum gas.",
            "Most centralized ETH perp venues require ETH on Ethereum or USDT on the venue's chain."
        ),
        (
            "No MetaMask, no second wallet, no bridge required.",
            "Bridging or using a separate MetaMask wallet adds friction, gas, and security considerations."
        ),
    ],
    "solana-perps": [
        (
            "SOL perp positions use the same Solana wallet you already use for spot trades.",
            "Centralized SOL perp venues require depositing SOL or USDC into the exchange first."
        ),
        (
            "Funding rates, position state, and PnL settle on-chain transparently.",
            "Centralized venues settle internally on a closed ledger you cannot independently verify."
        ),
    ],
    "altcoin-perps": [
        (
            "Altcoin and memecoin perp markets often go live the same day as a token gains liquidity.",
            "Centralized exchanges typically wait weeks or months to list new memecoin perps, if at all."
        ),
        (
            "No KYC means access regardless of geography or document availability.",
            "Centralized altcoin perp access depends on exchange listing decisions and user eligibility."
        ),
    ],
    "hyperliquid-frontend": [
        (
            "Trade Hyperliquid markets from Phantom or Backpack without installing MetaMask or bridging to Arbitrum.",
            "The default Hyperliquid flow requires a MetaMask or EVM-compatible wallet and funds on Arbitrum."
        ),
        (
            "Mobile-first interface designed for Solana wallet users.",
            "Default Hyperliquid mobile experience requires MetaMask Mobile or WalletConnect setup."
        ),
    ],
    "xstocks-trading": [
        (
            "Trade AAPLx, TSLAx, NVDAx, and SPYx 24/7 from a Solana wallet using SPL token flows you already know.",
            "Traditional brokerages only trade during U.S. market hours and require account approval and identity verification."
        ),
        (
            "xStocks are composable in DeFi. LP them on Raydium, borrow against them on Kamino, route through Jupiter.",
            "Stocks held at Robinhood, Schwab, or Fidelity sit in a brokerage account and cannot be moved into DeFi protocols."
        ),
        (
            "Self-custody: your xStocks live in your wallet, not in a broker's account that can be frozen or restricted.",
            "Brokerage accounts are subject to account holds, T+1 settlement, and platform policies you do not control."
        ),
    ],
    "prediction-markets": [
        (
            "Nexus DEX prediction markets settle from your wallet without KYC or off-chain custody.",
            "Traditional sportsbooks and prediction venues require accounts, deposits, and often KYC."
        ),
        (
            "Resolution sources and contract logic are on-chain and inspectable.",
            "Centralized prediction venues settle internally and the user has to trust their resolution process."
        ),
    ],
    "solana-swap": [
        (
            "Best price aggregated across Jupiter, Raydium, and Orca in one transaction.",
            "Centralized exchange swap pricing depends on their internal order book and pair availability."
        ),
        (
            "No KYC, no signup, instant settlement to your wallet.",
            "Centralized exchange swaps require account creation and may restrict withdrawals."
        ),
    ],
    "buy-token": [
        (
            "Buy any Solana token from your wallet using best-price aggregation across Jupiter, Raydium, and Orca.",
            "Centralized exchanges only list tokens they choose to list and often skip memecoins and new launches."
        ),
        (
            "Trade settles instantly to your wallet without deposit, withdrawal, or KYC friction.",
            "Centralized buys require depositing fiat or crypto first and going through verification."
        ),
    ],
    "no-kyc-trading": [
        (
            "Nexus DEX trades from your wallet without identity verification or document upload.",
            "Centralized exchanges require KYC at signup and often re-KYC for higher limits or specific products."
        ),
        (
            "Your wallet remains the only source of account access, and no personal data is stored.",
            "Centralized exchange access depends on their account systems and stored identity records."
        ),
    ],
    "whale-tracking": [
        (
            "Real-time on-chain whale and smart-money tracking based on indexed Solana activity.",
            "CEX whale tracking is impossible because their order books are off-chain and opaque."
        ),
        (
            "Follow specific wallets, deployer clusters, or sniper patterns from the same interface you trade in.",
            "Most third-party trackers require subscriptions and live separately from the trading interface."
        ),
    ],
    "token-launch": [
        (
            "Launch a token from your wallet with no code, no KYC, and no upfront fees.",
            "Centralized exchange listings require legal review, fees, and weeks or months of process."
        ),
        (
            "Bonding curve launchpad auto-graduates to Raydium liquidity once the threshold is reached.",
            "Third-party launchpads often gate access, require fees, or take a meaningful percentage of supply."
        ),
    ],
    "wallet-trading": [
        (
            "Funds stay in your wallet between trades. Nexus DEX never custodies or holds them.",
            "Centralized exchanges custody your funds and can freeze, restrict, or pause access."
        ),
        (
            "Every trade settles on-chain from your wallet signature, fully transparent.",
            "Centralized trades settle on an internal ledger you cannot independently verify."
        ),
    ],
    "how-to-guides": [
        (
            "Each guide walks through a specific Nexus DEX workflow from wallet setup through trade execution.",
            "Most centralized exchange tutorials assume you have already completed KYC and funded an account."
        ),
        (
            "Guides are mobile-first because the entire interface is designed for mobile execution.",
            "Centralized exchange guides often default to desktop UIs that differ from their mobile apps."
        ),
    ],
}

GENERIC_SCENARIO_EXAMPLES = [
    "A trader wants leverage without going through KYC or funding a centralized exchange account.",
    "A user wants to swap a Solana token that no centralized exchange lists.",
    "A trader wants to keep funds in their own wallet between positions instead of trusting a custodian.",
    "A mobile-first user wants the same interface for perps, spot, and prediction markets.",
]

HUB_SCENARIO_EXAMPLES = {
    "perps-trading": [
        "A trader wants 10x BTC leverage from a Solana wallet without a centralized exchange account.",
        "A user wants to short ETH for a few hours without bridging or opening a new wallet.",
        "A trader wants to manage multiple perp positions from a phone without juggling multiple apps.",
    ],
    "bitcoin-perps": [
        "A trader wants to long BTC with 25x leverage but does not want to KYC.",
        "A user wants to short BTC briefly during a news event without funding a centralized account first.",
        "A Solana-native trader wants BTC exposure without holding BTC on a centralized exchange.",
    ],
    "ethereum-perps": [
        "A trader wants ETH leverage but does not want to bridge USDC back to Ethereum mainnet.",
        "A user wants to short ETH without installing MetaMask or paying Ethereum gas.",
        "A Solana-native user wants ETH exposure without juggling two wallets.",
    ],
    "solana-perps": [
        "A trader holds SOL in Phantom and wants to add leverage exposure from the same wallet.",
        "A user wants to hedge a SOL spot position without moving funds to a centralized exchange.",
        "A trader wants to scalp SOL perps from mobile during a volatile session.",
    ],
    "altcoin-perps": [
        "A memecoin trader wants leverage on WIF or BONK that centralized exchanges do not offer.",
        "A user wants to short a low-cap token during a euphoric pump without an off-chain account.",
        "A trader wants exposure to a brand-new perp listing the same day liquidity goes live.",
    ],
    "hyperliquid-frontend": [
        "A Solana-native trader wants Hyperliquid liquidity without installing MetaMask.",
        "A mobile user wants to access Hyperliquid from Phantom on iOS.",
        "A user wants to keep Hyperliquid exposure inside their existing Solana wallet workflow.",
    ],
    "xstocks-trading": [
        "A non-U.S. user wants Apple and Nvidia exposure without opening a U.S. brokerage account.",
        "A crypto-native investor wants to hold TSLAx and SPYx in their Solana wallet alongside SOL and USDC.",
        "A DeFi user wants to LP NVDAx/USDC on Raydium or use AAPLx as collateral on Kamino.",
        "A weekend trader wants to buy stock exposure outside U.S. market hours without waiting for Monday open.",
    ],
    "prediction-markets": [
        "A trader wants to bet on the next FOMC rate decision from a Solana wallet.",
        "A sports fan wants to take a side on an NFL game without signing up at a sportsbook.",
        "A crypto user wants to bet on BTC reaching a specific price level by a deadline.",
    ],
    "solana-swap": [
        "A user wants the best price on a USDC-to-SOL swap without checking three aggregators manually.",
        "A trader wants to swap into a freshly listed SPL token without leaving the Nexus DEX interface.",
        "A mobile user wants low-slippage swaps with one-tap execution.",
    ],
    "buy-token": [
        "A buyer wants the lowest price on BONK without manually checking Jupiter and Raydium.",
        "A user wants to buy a new memecoin within minutes of its launch.",
        "A trader wants to acquire an SPL token that is not listed on Coinbase or Binance.",
    ],
    "no-kyc-trading": [
        "A user in a jurisdiction with limited CEX access wants to trade without KYC.",
        "A privacy-focused trader wants to swap, perp-trade, hold tokenized stocks, and bet without sharing identity documents.",
        "A user burned by past KYC leaks wants to keep personal data out of the trading flow entirely.",
    ],
    "whale-tracking": [
        "A memecoin trader wants to see which wallets bought BONK before its last pump.",
        "An analyst wants to track deployer clusters launching new tokens this week.",
        "A trader wants alerts when known smart-money wallets accumulate a specific token.",
    ],
    "token-launch": [
        "A creator wants to deploy a memecoin without paying a third-party launchpad.",
        "A community wants to launch a token from a single wallet without code or KYC.",
        "A user wants to test a token concept with a small bonding-curve launch first.",
    ],
    "wallet-trading": [
        "A user wants all trading activity to settle from their wallet without centralized custody.",
        "A privacy-focused trader wants every trade to be inspectable on-chain.",
        "A user who lost funds in past exchange failures wants self-custody as the default.",
    ],
    "how-to-guides": [
        "A new Solana user wants to walk through their first swap step by step.",
        "A CEX-native trader wants a clear guide to opening their first wallet-based perp position.",
        "A token creator wants a guide to launching and graduating to Raydium.",
    ],
}


def compact_spaces(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def normalize_keyword(text):
    return compact_spaces(str(text).lower())


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", normalize_keyword(text)).strip("-")


def keyword_tokens(text):
    return set(normalize_keyword(text).replace("-", " ").split())


def normalize_term_tokens(text):
    return set(normalize_keyword(text).replace("-", " ").split())


def apply_brand_case(text):
    result = f" {str(text)} "
    for raw, proper in sorted(BRAND_CASE.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(raw) + r"(?![a-z0-9])"
        result = re.sub(pattern, proper, result, flags=re.IGNORECASE)
    return compact_spaces(result)


def title_case(text):
    words = normalize_keyword(text).split()
    titled_words = []

    for i, word in enumerate(words):
        if i > 0 and word in SMALL_WORDS:
            titled_words.append(word)
        else:
            titled_words.append(word.capitalize())

    return apply_brand_case(" ".join(titled_words))


def escape_html(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def trim_meta_description(text, minimum=110, maximum=165):
    text = compact_spaces(text)
    if len(text) <= maximum:
        return text

    truncated = text[: maximum + 1]
    cut_points = [
        truncated.rfind(". "),
        truncated.rfind("; "),
        truncated.rfind(", "),
        truncated.rfind(" "),
    ]
    valid_cuts = [point for point in cut_points if point > minimum]

    if valid_cuts:
        cut = max(valid_cuts)
        text = truncated[:cut].rstrip(" ,;.")
    else:
        text = truncated[:maximum].rstrip(" ,;.")

    return text + "."


def build_canonical(slug):
    return f"{SITE}/nexus-dex/{slug}/"


def page_path(slug):
    return os.path.join(OUTPUT_DIR, slug, "index.html")


def page_exists(slug):
    return os.path.exists(page_path(slug))


def iter_match_terms(match_terms):
    if isinstance(match_terms, str):
        return [match_terms]
    if isinstance(match_terms, dict):
        values = []
        for value in match_terms.values():
            if isinstance(value, (list, tuple, set)):
                values.extend(str(v) for v in value if str(v).strip())
            elif str(value).strip():
                values.append(str(value))
        return values
    if isinstance(match_terms, (list, tuple, set)):
        return [str(term) for term in match_terms if str(term).strip()]
    return [str(match_terms)] if str(match_terms).strip() else []


def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        return []

    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return list(dict.fromkeys(normalize_keyword(line) for line in f if line.strip()))


def matches_cluster(keyword, match_terms):
    kw_norm = normalize_keyword(keyword)
    kw_tokens = keyword_tokens(keyword)
    kw_joined = f" {kw_norm.replace('-', ' ')} "

    for term in iter_match_terms(match_terms):
        term_norm = normalize_keyword(term)
        term_tokens = normalize_term_tokens(term)
        term_joined = f" {term_norm.replace('-', ' ')} "

        if term_tokens and term_tokens.issubset(kw_tokens):
            return True
        if term_joined.strip() and term_joined in kw_joined:
            return True

    return False


def score_keyword(keyword, hub_terms):
    kw = normalize_keyword(keyword)
    kw_tokens = keyword_tokens(kw)
    score = 0

    for term in iter_match_terms(hub_terms):
        term_tokens = normalize_term_tokens(term)
        if term_tokens and term_tokens.issubset(kw_tokens):
            score += 5

    if "perps" in kw_tokens or "perp" in kw_tokens:
        score += 4
    if "leverage" in kw_tokens or "leveraged" in kw_tokens:
        score += 3
    if "no" in kw_tokens and "kyc" in kw_tokens:
        score += 3
    if "wallet" in kw_tokens or "mobile" in kw_tokens:
        score += 2
    if {"buy", "swap", "trade"} & kw_tokens:
        score += 2
    if "xstocks" in kw_tokens or "xstock" in kw_tokens or "tokenized" in kw_tokens:
        score += 3
    if kw.startswith("how to ") or kw.startswith("where to "):
        score += 1

    return (-score, len(kw), kw)


def dedupe_cluster_keywords(cluster_keywords):
    deduped = []
    seen_slugs = set()

    for keyword in cluster_keywords:
        slug = slugify(keyword)
        if slug and slug not in seen_slugs:
            deduped.append(keyword)
            seen_slugs.add(slug)

    return deduped


def clean_display_keyword(keyword):
    cleaned = normalize_keyword(keyword)
    cleaned = re.sub(r"^\s*how\s+to\s+", "", cleaned)
    cleaned = re.sub(r"^\s*where\s+to\s+", "", cleaned)
    cleaned = re.sub(r"^\s*can\s+i\s+", "", cleaned)
    cleaned = re.sub(r"^\s*best\s+place\s+to\s+", "", cleaned)
    cleaned = re.sub(r"\s+no\s+kyc$", "", cleaned)
    cleaned = re.sub(r"\s+mobile$", "", cleaned)
    cleaned = re.sub(r"\s+app$", "", cleaned)
    cleaned = compact_spaces(cleaned)
    return title_case(cleaned)


def build_related_link_items(cluster_keywords):
    items = []
    seen = set()

    for keyword in cluster_keywords:
        slug = slugify(keyword)
        if not slug or slug in seen or not page_exists(slug):
            continue

        seen.add(slug)
        label = clean_display_keyword(keyword)
        items.append({
            "slug": slug,
            "title": label,
            "href": f"/nexus-dex/{slug}/",
            "anchor": label,
        })

    return items


def build_related_links_html(link_items):
    return "\n".join(
        f'<li><a href="{escape_html(item["href"])}">{escape_html(item["anchor"])}</a></li>'
        for item in link_items
    )


def extract_variation_label(keyword, hub_terms):
    cleaned = normalize_keyword(keyword).replace("-", " ")
    cleaned = re.sub(r"^\s*how\s+to\s+", "", cleaned)
    cleaned = re.sub(r"^\s*where\s+to\s+", "", cleaned)
    cleaned = re.sub(r"^\s*can\s+i\s+", "", cleaned)
    cleaned = compact_spaces(cleaned)

    removable_terms = sorted(
        [normalize_keyword(term).replace("-", " ") for term in iter_match_terms(hub_terms) if normalize_keyword(term)],
        key=len,
        reverse=True,
    )

    for term in removable_terms:
        cleaned = re.sub(rf"\b{re.escape(term)}\b", " ", cleaned)

    original_words = cleaned.split()
    words = []

    for word in original_words:
        if word in STOPWORDS_FOR_VARIATIONS:
            continue
        if word in LOW_SIGNAL_VARIATION_WORDS and len(original_words) == 1:
            continue
        words.append(word)

    cleaned = compact_spaces(" ".join(words))

    if not cleaned or len(cleaned) < 3:
        return ""

    return title_case(cleaned)


def build_top_topics_html(cluster_keywords, hub_terms):
    counter = Counter()

    for keyword in cluster_keywords:
        label = extract_variation_label(keyword, hub_terms)
        if label:
            counter[label] += 1

    top_items = [label for label, _ in counter.most_common(TOP_TOPICS_COUNT)]
    if not top_items:
        return ""

    items_html = "\n".join(f"<li>{escape_html(item)}</li>" for item in top_items)

    return f"""
<section aria-labelledby="variations-heading">
<h2 id="variations-heading">Popular Topics In This Category</h2>
<p>These are the most common trading themes and repeated search patterns across the related pages in this hub.</p>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_key_features_html(hub_slug):
    bullets = HUB_KEY_FEATURES.get(hub_slug, [
        "Self-custodial trading from your Solana wallet, no centralized account required",
        "No KYC, no signup, no document upload, no geographic gating",
        "Mobile-first interface designed for fast execution",
        "Best-price routing and on-chain settlement for every trade",
    ])
    return "\n".join(f"<li>{escape_html(bullet)}</li>" for bullet in bullets)


def build_related_topics_html(match_terms):
    cleaned_terms = []
    seen = set()

    for term in iter_match_terms(match_terms):
        label = title_case(str(term).replace("-", " "))
        key = normalize_keyword(label)
        if key and key not in seen:
            seen.add(key)
            cleaned_terms.append(label)

    if not cleaned_terms:
        return ""

    items_html = "\n".join(
        f"<li>{escape_html(item)}</li>"
        for item in cleaned_terms[:MAX_RELATED_TOPICS]
    )

    return f"""
<section aria-labelledby="related-topics-heading">
<h2 id="related-topics-heading">Related Topics In This Hub</h2>
<p>These terms define the category and show the types of markets, assets, and trading angles this hub is built around.</p>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_get_started_html(hub_slug):
    steps = HUB_GET_STARTED_STEPS.get(hub_slug, [
        "Install a Solana wallet (Phantom, Backpack, or Solflare) and back up the seed phrase.",
        "Fund the wallet with SOL or USDC from any source you control.",
        "Connect to Nexus DEX and start trading. No signup, no KYC, no deposit required.",
    ])

    items_html = "\n".join(f"<li>{escape_html(step)}</li>" for step in steps)

    return f"""
<section aria-labelledby="get-started-heading">
<h2 id="get-started-heading">How To Get Started</h2>
<p>These are the steps to start trading in this category from a Solana wallet.</p>
<ol>
{items_html}
</ol>
</section>
""".strip()


def build_how_it_works_html(hub_slug):
    text = HUB_HOW_IT_WORKS.get(
        hub_slug,
        "Nexus DEX settles every trade on-chain from your wallet signature. Your funds remain in your wallet, the platform never takes custody, and all positions are visible and verifiable on-chain."
    )
    return f"""
<section aria-labelledby="how-it-works-heading">
<h2 id="how-it-works-heading">How This Works</h2>
<p>{escape_html(text)}</p>
</section>
""".strip()


def build_who_targeted_html(hub_slug):
    text = HUB_TARGETING.get(
        hub_slug,
        "This hub is useful for Solana-native traders, mobile-first users, and anyone who wants to trade without going through a centralized exchange or completing KYC."
    )
    return f"""
<section aria-labelledby="targeting-heading">
<h2 id="targeting-heading">Who This Is For</h2>
<p>{escape_html(text)}</p>
</section>
""".strip()


def get_faqs_for_hub(hub_slug):
    faqs = list(HUB_FAQS.get(hub_slug, []))
    if len(faqs) < 2:
        faqs.extend(GENERIC_FAQS[: max(0, 2 - len(faqs))])
    return faqs[:MAX_FAQS]


def build_faq_html(hub_slug):
    blocks = []

    for question, answer in get_faqs_for_hub(hub_slug):
        blocks.append(
            f'<div class="faq-item"><h3>{escape_html(question)}</h3><p>{escape_html(answer)}</p></div>'
        )

    return f"""
<section aria-labelledby="faq-heading">
<h2 id="faq-heading">Frequently Asked Questions</h2>
{''.join(blocks)}
</section>
""".strip()


def build_link_summary_html(link_items, hub_title):
    count = len(link_items)
    if count == 0:
        return (
            f"<p>This hub is active, but it does not have related Nexus DEX pages linked yet. "
            f"As more pages are generated in the {escape_html(hub_title)} category, they should be linked here automatically.</p>"
        )

    return (
        f"<p>This hub currently links to {count} related Nexus DEX pages so you can explore "
        f"specific markets, workflows, and use cases inside the {escape_html(hub_title)} category.</p>"
    )


def tokenize_for_analysis(text):
    return re.findall(r"[a-z0-9]+", normalize_keyword(text))


def natural_list(items, max_items=4):
    cleaned = [compact_spaces(str(x)) for x in items if compact_spaces(str(x))]
    cleaned = cleaned[:max_items]

    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"

    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def get_hub_keyword_insights(matched_keywords, hub_terms):
    channel_counter = Counter()
    intent_counter = Counter()
    entity_counter = Counter()

    hub_term_tokens = set()
    for term in iter_match_terms(hub_terms):
        hub_term_tokens |= normalize_term_tokens(term)

    for keyword in matched_keywords:
        tokens = tokenize_for_analysis(keyword)

        for token in tokens:
            if token in CHANNEL_HINTS:
                channel_counter[CHANNEL_HINTS[token]] += 1

            if token in INTENT_HINTS:
                intent_counter[INTENT_HINTS[token]] += 1

            if (
                token not in GENERIC_ENTITY_WORDS
                and token not in hub_term_tokens
                and len(token) > 2
                and not token.isdigit()
            ):
                entity_counter[token] += 1

    top_entities = [title_case(x) for x, _ in entity_counter.most_common(8)]
    top_channels = [x for x, _ in channel_counter.most_common(6)]
    top_intents = [x for x, _ in intent_counter.most_common(6)]

    return {
        "top_entities": top_entities,
        "top_channels": top_channels,
        "top_intents": top_intents,
    }


def detect_hub_context(hub_slug, hub_terms):
    combined = f"{hub_slug} {' '.join(iter_match_terms(hub_terms))}".lower()

    if any(x in combined for x in ["perps", "perp", "leverage", "futures"]):
        return "perps"
    if any(x in combined for x in ["xstocks", "xstock", "tokenized stock", "tokenized equity", "aaplx", "tslax", "nvdax", "spyx", "qqqx"]):
        return "xstocks"
    if any(x in combined for x in ["prediction", "bet on", "outcome", "odds"]):
        return "prediction"
    if any(x in combined for x in ["swap", "buy", "spl token", "aggregator"]):
        return "swap"
    if any(x in combined for x in ["whale", "smart money", "insider", "deployer", "sniper"]):
        return "whale"
    if any(x in combined for x in ["launch", "launchpad", "bonding curve", "deploy"]):
        return "launch"
    if any(x in combined for x in ["wallet", "self custodial", "non custodial", "phantom", "backpack"]):
        return "wallet"
    if "how to" in combined:
        return "guide"
    return "general"


COMMON_SCENARIO_TEMPLATES = {
    "perps": [
        "A trader wants leverage exposure without funding a centralized exchange account first.",
        "A user wants to long or short a specific asset from a Solana wallet without bridging.",
        "A mobile-first trader wants fast position entry and exit without juggling apps.",
    ],
    "prediction": [
        "A user wants to take a position on an outcome without signing up at a sportsbook or prediction venue.",
        "A trader wants to hedge an event-driven exposure from the same wallet they use for spot.",
        "A mobile user wants prediction market access without bridging USDC to another chain.",
    ],
    "xstocks": [
        "A non-U.S. user wants Apple, Tesla, or Nvidia exposure without opening a U.S. brokerage account.",
        "A crypto-native investor wants to hold tokenized stocks alongside SOL and USDC in the same wallet.",
        "A DeFi user wants to LP a stock token against USDC or use it as collateral on Kamino.",
        "A weekend trader wants stock exposure outside U.S. market hours without waiting for the next open.",
    ],
    "swap": [
        "A user wants the best price on a token swap without checking three aggregators manually.",
        "A trader wants to swap into a new memecoin within minutes of liquidity going live.",
        "A mobile user wants low-slippage swaps without leaving their wallet flow.",
    ],
    "whale": [
        "A trader wants to see which wallets bought a token before its last pump.",
        "An analyst wants to track deployer wallets and identify clustered launches.",
        "A user wants alerts when known smart money accumulates a specific asset.",
    ],
    "launch": [
        "A creator wants to deploy a token without paying a third-party launchpad.",
        "A community wants to launch a memecoin with a bonding curve and graduate to Raydium.",
        "A user wants to test a token concept without going through KYC or upfront fees.",
    ],
    "wallet": [
        "A user wants every trade to settle from their wallet without custodial wrappers.",
        "A privacy-focused trader wants to keep all trading activity on-chain and inspectable.",
        "A user burned by centralized exchange failures wants self-custody as the default.",
    ],
    "guide": [
        "A new user needs a step-by-step walkthrough for their first wallet-based trade.",
        "A CEX-native trader wants a clear path from account-based trading to wallet-based trading.",
        "A creator wants a guide to deploying and graduating their first Solana token.",
    ],
    "general": [
        "A user wants to skip KYC and trade directly from a wallet they already control.",
        "A trader wants spot, perps, and prediction markets in one mobile-first interface.",
        "A self-custody-focused user wants every trade to settle on-chain.",
    ],
}


def build_dynamic_keyword_summary_html(matched_keywords, hub_terms):
    if not matched_keywords:
        fallback = (
            "This hub is active based on the cluster mapping for this category. "
            "As generated pages accumulate here, this section will reflect the most common assets, wallet types, and trading patterns people are searching for."
        )
        return f"""
<section aria-labelledby="keyword-patterns-heading">
<h2 id="keyword-patterns-heading">What People Are Searching For</h2>
<p>{escape_html(fallback)}</p>
</section>
""".strip()

    insights = get_hub_keyword_insights(matched_keywords, hub_terms)

    entities = natural_list(insights["top_entities"], 5)
    channels = natural_list([title_case(x) for x in insights["top_channels"]], 4)
    intents = natural_list(insights["top_intents"], 4)

    paragraphs = []

    if entities:
        paragraphs.append(
            f"Across the related pages in this hub, people frequently search about {escape_html(entities)}. "
            f"That suggests this category often overlaps with specific assets, brands, or trading contexts users want to access from a Solana wallet."
        )

    if channels:
        paragraphs.append(
            f"The keyword patterns also show that these workflows often run through {escape_html(channels)}. "
            f"That matters because the access channel usually shapes the user experience, the wallet flow, and the assets available."
        )

    if intents:
        paragraphs.append(
            f"Another strong pattern across the matched searches is {escape_html(intents)}. "
            f"That kind of intent is common among users moving away from centralized exchanges toward self-custodial, mobile-first trading."
        )

    if not paragraphs:
        paragraphs.append(
            "The matched searches in this hub show repeated intent around self-custodial trading, mobile-first access, and skipping centralized exchange friction."
        )

    body = "\n".join(f"<p>{paragraph}</p>" for paragraph in paragraphs)

    return f"""
<section aria-labelledby="keyword-patterns-heading">
<h2 id="keyword-patterns-heading">What People Are Searching For</h2>
{body}
</section>
""".strip()


def build_dynamic_entity_focus_html(matched_keywords, hub_terms):
    if not matched_keywords:
        return ""

    insights = get_hub_keyword_insights(matched_keywords, hub_terms)
    entities = insights["top_entities"][:8]

    if not entities:
        return ""

    items_html = "\n".join(f"<li>{escape_html(item)}</li>" for item in entities)

    return f"""
<section aria-labelledby="entity-focus-heading">
<h2 id="entity-focus-heading">Common Tokens, Platforms & Brands</h2>
<p>These are the assets, platforms, and recognizable names that show up most often in related search patterns across this hub.</p>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_cluster_specific_intro_html(intro, matched_keywords, hub_terms):
    if not matched_keywords:
        return f"""
<section aria-labelledby="hub-intro-heading">
<h2 id="hub-intro-heading" style="position:absolute;left:-9999px;">Hub Introduction</h2>
<p>{escape_html(intro)}</p>
<p>This hub is being maintained from the cluster definitions, even if the related pages are not all present yet.</p>
</section>
""".strip()

    insights = get_hub_keyword_insights(matched_keywords, hub_terms)

    top_channels = natural_list([title_case(x) for x in insights["top_channels"]], 3)
    top_intents = natural_list(insights["top_intents"], 3)

    supporting = []

    if top_channels:
        supporting.append(
            f"In this category, activity often shows up through {escape_html(top_channels)}."
        )

    if top_intents:
        supporting.append(
            f"Repeated search patterns also suggest that {escape_html(top_intents)} shows up often in these variations."
        )

    supporting_html = "\n".join(f"<p>{sentence}</p>" for sentence in supporting)

    return f"""
<section aria-labelledby="hub-intro-heading">
<h2 id="hub-intro-heading" style="position:absolute;left:-9999px;">Hub Introduction</h2>
<p>{escape_html(intro)}</p>
{supporting_html}
</section>
""".strip()


def build_meta_keyword_support_text(matched_keywords, hub_terms):
    if not matched_keywords:
        return "self-custodial trading, no-KYC access, and wallet-based DEX workflows"

    insights = get_hub_keyword_insights(matched_keywords, hub_terms)
    parts = []

    if insights["top_entities"]:
        parts.append(f"assets like {natural_list(insights['top_entities'], 4)}")
    if insights["top_channels"]:
        parts.append(f"channels like {natural_list([title_case(x) for x in insights['top_channels']], 4)}")
    if insights["top_intents"]:
        parts.append(f"intents like {natural_list(insights['top_intents'], 4)}")

    if not parts:
        return "self-custodial trading and wallet-based DEX workflows"

    return "; ".join(parts)


def build_common_scenarios_html(hub_slug, matched_keywords, hub_terms):
    context = detect_hub_context(hub_slug, hub_terms)
    base_points = list(COMMON_SCENARIO_TEMPLATES.get(context, COMMON_SCENARIO_TEMPLATES["general"]))
    examples = HUB_SCENARIO_EXAMPLES.get(hub_slug, [])
    combined = dedupe_preserve_order(base_points + examples)

    if not combined:
        return ""

    items_html = "\n".join(
        f"<li>{escape_html(item)}</li>"
        for item in combined[:MAX_COMMON_SCENARIOS]
    )

    return f"""
<section aria-labelledby="common-scenarios-heading">
<h2 id="common-scenarios-heading">Common Trading Scenarios</h2>
<p>These are recurring use cases and trading scenarios that show up across the related pages in this hub.</p>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_comparison_html(hub_slug):
    pairs = HUB_COMPARISON_POINTS.get(hub_slug, GENERIC_COMPARISON_POINTS)
    if not pairs:
        return ""

    blocks = []
    for nexus_side, cex_side in pairs[:MAX_COMPARISON_POINTS]:
        blocks.append(
            f"""
<div class="comparison-item">
  <div class="comparison-col nexus">
    <h3>Nexus DEX</h3>
    <p>{escape_html(nexus_side)}</p>
  </div>
  <div class="comparison-col cex">
    <h3>Centralized Exchange</h3>
    <p>{escape_html(cex_side)}</p>
  </div>
</div>
""".strip()
        )

    return f"""
<section aria-labelledby="comparison-heading">
<h2 id="comparison-heading">Nexus DEX vs Centralized Exchanges</h2>
<p>The structural differences between self-custodial wallet trading and centralized exchange trading shape how each workflow feels in practice.</p>
{''.join(blocks)}
</section>
""".strip()


def build_schema(hub_slug, hub_title, description, intro, link_items, matched_keywords, hub_terms):
    canonical = build_canonical(hub_slug)
    faq_entities = [
        {
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": answer,
            },
        }
        for question, answer in get_faqs_for_hub(hub_slug)
    ]

    keyword_support = build_meta_keyword_support_text(matched_keywords, hub_terms)

    schema_objects = [
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": hub_title,
            "description": description,
            "url": canonical,
            "about": intro,
            "keywords": keyword_support,
            "mainEntity": {
                "@type": "ItemList",
                "name": f"{hub_title} Related Pages",
                "numberOfItems": len(link_items),
            },
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": "Nexus DEX", "item": f"{SITE}/nexus-dex/"},
                {"@type": "ListItem", "position": 3, "name": hub_title, "item": canonical},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"{hub_title} Related Pages",
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "numberOfItems": len(link_items),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index + 1,
                    "url": f"{SITE}{item['href']}",
                    "name": item["anchor"],
                }
                for index, item in enumerate(link_items)
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_entities,
        },
    ]

    return json.dumps(schema_objects, ensure_ascii=False, separators=(",", ":"))


def validate_hub_output(hub_slug, hub_title, description, canonical, matched_keywords, link_items, html):
    errors = []

    if not hub_slug:
        errors.append("empty hub slug")
    if not hub_title.strip():
        errors.append("empty title")
    if len(description) < 110 or len(description) > 165:
        errors.append("description length out of target range")
    if not canonical.endswith(f"/{hub_slug}/"):
        errors.append("canonical mismatch")
    if html.count("<h2") < 8:
        errors.append("insufficient section depth")
    if len(html) < 8000:
        errors.append("page html too thin")
    if "<main" not in html:
        errors.append("missing main landmark")
    if "application/ld+json" not in html:
        errors.append("missing schema")
    if "og:title" not in html or "twitter:title" not in html:
        errors.append("missing social metadata")
    if not link_items:
        errors.append("no linked child pages")
    if matched_keywords and len(link_items) == 0:
        errors.append("matched keywords exist but no child pages were found on disk")

    return errors


def dedupe_preserve_order(items):
    seen = set()
    output = []

    for item in items:
        key = compact_spaces(str(item).lower())
        if key and key not in seen:
            seen.add(key)
            output.append(item)

    return output


def build_hub_html(
    hub_slug,
    hub_title,
    description,
    intro,
    link_items,
    top_topics_html,
    key_features_html,
    related_topics_html,
    faq_html,
    matched_keywords,
    hub_terms,
):
    canonical = build_canonical(hub_slug)
    links_html = build_related_links_html(link_items)
    schema_json = build_schema(hub_slug, hub_title, description, intro, link_items, matched_keywords, hub_terms)
    how_it_works_html = build_how_it_works_html(hub_slug)
    who_targeted_html = build_who_targeted_html(hub_slug)
    get_started_html = build_get_started_html(hub_slug)
    link_summary_html = build_link_summary_html(link_items, hub_title)
    dynamic_keyword_summary_html = build_dynamic_keyword_summary_html(matched_keywords, hub_terms)
    dynamic_entity_focus_html = build_dynamic_entity_focus_html(matched_keywords, hub_terms)
    cluster_specific_intro_html = build_cluster_specific_intro_html(intro, matched_keywords, hub_terms)
    common_scenarios_html = build_common_scenarios_html(hub_slug, matched_keywords, hub_terms)
    comparison_html = build_comparison_html(hub_slug)

    jump_links = []
    sections = []

    if top_topics_html:
        jump_links.append('<a href="#variations-heading">Topics</a>')
        sections.append(f"""
<div class="section-card">
{top_topics_html}
</div>
""".strip())

    if common_scenarios_html:
        jump_links.append('<a href="#common-scenarios-heading">Scenarios</a>')
        sections.append(f"""
<div class="section-card">
{common_scenarios_html}
</div>
""".strip())

    jump_links.append('<a href="#keyword-patterns-heading">What People Search</a>')
    sections.append(f"""
<div class="section-card">
{dynamic_keyword_summary_html}
</div>
""".strip())

    if comparison_html:
        jump_links.append('<a href="#comparison-heading">vs CEX</a>')
        sections.append(f"""
<div class="section-card">
{comparison_html}
</div>
""".strip())

    jump_links.append('<a href="#how-it-works-heading">How It Works</a>')
    sections.append(f"""
<div class="section-card">
{how_it_works_html}
</div>
""".strip())

    jump_links.append('<a href="#targeting-heading">Who It Is For</a>')
    sections.append(f"""
<div class="section-card">
{who_targeted_html}
</div>
""".strip())

    if dynamic_entity_focus_html:
        jump_links.append('<a href="#entity-focus-heading">Tokens & Platforms</a>')
        sections.append(f"""
<div class="section-card">
{dynamic_entity_focus_html}
</div>
""".strip())

    if related_topics_html:
        jump_links.append('<a href="#related-topics-heading">Related Topics</a>')
        sections.append(f"""
<div class="section-card">
{related_topics_html}
</div>
""".strip())

    jump_links.append('<a href="#key-features-heading">Key Features</a>')
    sections.append(f"""
<section class="section-card warning-surface" aria-labelledby="key-features-heading">
<h2 id="key-features-heading">Key Features</h2>
<p>These are the features that define this category on Nexus DEX.</p>
<ul>
{key_features_html}
</ul>
</section>
""".strip())

    jump_links.append('<a href="#get-started-heading">Get Started</a>')
    sections.append(f"""
<div class="section-card verify-surface">
{get_started_html}
</div>
""".strip())

    jump_links.append('<a href="#related-checks-heading">Related Pages</a>')
    sections.append(f"""
<section class="section-card link-surface" aria-labelledby="related-checks-heading">
<h2 id="related-checks-heading">Related Pages</h2>
{link_summary_html}
<div class="link-box">
{"<ul>" + links_html + "</ul>" if link_items else "<p>No linked pages are available yet for this hub.</p>"}
</div>
</section>
""".strip())

    sections.append("""
<section class="section-card closing-surface" aria-labelledby="what-to-do-heading">
<h2 id="what-to-do-heading">What To Do Next</h2>
<p>If this category matches what you are trying to do, the fastest path is to connect a Solana wallet and try a small first trade. Every workflow on Nexus DEX is wallet-based, so there is no signup to complete before testing.</p>
<p>If you are still researching, use the related pages above to compare specific markets, assets, or workflows. Each page covers a focused use case inside this category.</p>
</section>
""".strip())

    jump_links.append('<a href="#faq-heading">FAQ</a>')
    sections.append(f"""
<div class="section-card faq-surface">
{faq_html}
</div>
""".strip())

    sections_html = "\n\n<div class=\"section-divider\"></div>\n\n".join(sections)
    jump_links_html = "\n  ".join(jump_links)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape_html(hub_title)}</title>
<meta name="description" content="{escape_html(description)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{escape_html(canonical)}">
<meta property="og:title" content="{escape_html(hub_title)}">
<meta property="og:description" content="{escape_html(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{escape_html(canonical)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape_html(hub_title)}">
<meta name="twitter:description" content="{escape_html(description)}">
<script type="application/ld+json">{schema_json}</script>
<style>
:root{{
--bg:#07111f;
--bg-2:#0c1728;
--bg-3:#12203a;
--surface:rgba(255,255,255,.06);
--surface-2:rgba(255,255,255,.08);
--surface-3:rgba(255,255,255,.04);
--card:#101c33;
--card-2:#162541;
--ink:#e8f0ff;
--ink-strong:#ffffff;
--ink-dark:#132033;
--muted:#9eb0cf;
--muted-2:#7e93b5;
--line:rgba(148,163,184,.20);
--line-2:rgba(255,255,255,.10);
--cyan:#22d3ee;
--cyan-2:#06b6d4;
--blue:#3b82f6;
--blue-2:#2563eb;
--violet:#8b5cf6;
--violet-2:#7c3aed;
--emerald:#10b981;
--emerald-2:#059669;
--amber:#f59e0b;
--red:#ef4444;
--green-soft:rgba(16,185,129,.12);
--green-line:rgba(16,185,129,.26);
--red-soft:rgba(239,68,68,.10);
--red-line:rgba(239,68,68,.22);
--shadow-xl:0 32px 90px rgba(2,6,23,.42);
--shadow-lg:0 20px 54px rgba(2,6,23,.30);
--shadow-md:0 12px 30px rgba(2,6,23,.22);
--shadow-sm:0 8px 20px rgba(2,6,23,.16);
}}

*{{
box-sizing:border-box;
}}

html{{
-webkit-text-size-adjust:100%;
scroll-behavior:smooth;
}}

body{{
font-family:Inter,system-ui,-apple-system,Arial,sans-serif;
margin:0;
padding-top:90px;
color:var(--ink);
line-height:1.7;
background:
radial-gradient(circle at 14% 8%, rgba(34,211,238,.16), transparent 22%),
radial-gradient(circle at 84% 0%, rgba(139,92,246,.20), transparent 28%),
radial-gradient(circle at 50% 100%, rgba(16,185,129,.08), transparent 24%),
linear-gradient(180deg,#06101b 0%, #0a1324 34%, #0e1830 100%);
}}

a{{
color:#8be9ff;
text-decoration:none;
}}

a:hover{{
text-decoration:underline;
}}

@supports (padding:max(0px)) {{
  body{{
    padding-left:max(0px, env(safe-area-inset-left));
    padding-right:max(0px, env(safe-area-inset-right));
  }}
}}

.top-bar{{
position:fixed;
top:0;
left:0;
width:100%;
display:flex;
justify-content:space-between;
align-items:center;
padding:10px 16px;
z-index:1000;
pointer-events:none;
}}

.top-actions{{
pointer-events:auto;
display:flex;
align-items:center;
gap:10px;
margin-right:20px;
}}

.logo{{
pointer-events:auto;
display:inline-flex;
align-items:center;
gap:10px;
font-size:14px;
font-weight:900;
color:#eef6ff;
margin-left:8px;
padding:11px 15px;
border-radius:999px;
letter-spacing:-.01em;
background:rgba(10,18,35,.68);
border:1px solid rgba(255,255,255,.10);
backdrop-filter:blur(14px);
box-shadow:var(--shadow-sm);
text-decoration:none;
}}

.logo:hover{{
text-decoration:none;
}}

.logo-dot{{
width:10px;
height:10px;
border-radius:50%;
background:linear-gradient(180deg,var(--cyan) 0%,var(--violet) 100%);
box-shadow:0 0 0 4px rgba(139,92,246,.14);
flex:0 0 10px;
}}

.app-top{{
display:inline-flex;
align-items:center;
justify-content:center;
padding:11px 14px;
font-size:14px;
border-radius:16px;
font-weight:900;
color:#fff;
border:1px solid rgba(255,255,255,.12);
white-space:nowrap;
background:linear-gradient(180deg,rgba(255,255,255,.14) 0%,rgba(255,255,255,.08) 100%);
backdrop-filter:blur(10px);
box-shadow:var(--shadow-sm);
}}

.app-top:hover{{
text-decoration:none;
}}

.checker-top{{
pointer-events:auto;
padding:11px 15px;
font-size:14px;
border-radius:16px;
font-weight:900;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
white-space:nowrap;
box-shadow:0 16px 34px rgba(34,211,238,.16);
}}

.checker-top:hover{{
text-decoration:none;
}}

.page-shell{{
max-width:980px;
margin:0 auto;
padding:0 14px 40px;
}}

.hero{{
position:relative;
padding:18px 8px 22px;
max-width:980px;
margin:0 auto 14px;
text-align:center;
}}

.hero-badge-row{{
display:flex;
flex-wrap:wrap;
justify-content:center;
gap:10px;
margin-bottom:14px;
}}

.hero-badge{{
display:inline-flex;
align-items:center;
justify-content:center;
gap:8px;
padding:9px 13px;
border-radius:999px;
font-size:13px;
font-weight:900;
color:#dbeafe;
background:rgba(255,255,255,.08);
border:1px solid rgba(255,255,255,.10);
backdrop-filter:blur(10px);
}}

.hero h1{{
margin:0;
font-size:48px;
line-height:1.02;
letter-spacing:-.05em;
font-weight:950;
color:var(--ink-strong);
text-wrap:balance;
}}

.hero p{{
margin:14px auto 0;
max-width:780px;
font-size:19px;
color:#c7d5eb;
text-wrap:balance;
}}

.hero-trust{{
margin-top:18px;
display:flex;
flex-wrap:wrap;
justify-content:center;
gap:10px;
}}

.hero-trust-chip{{
display:inline-flex;
align-items:center;
justify-content:center;
padding:10px 14px;
border-radius:999px;
font-size:13px;
font-weight:900;
color:#dce8fb;
background:rgba(255,255,255,.06);
border:1px solid rgba(255,255,255,.10);
box-shadow:var(--shadow-sm);
}}

.content-section{{
max-width:860px;
margin:auto;
padding:22px;
border-radius:30px;
position:relative;
overflow:hidden;
border:1px solid rgba(255,255,255,.10);
background:
linear-gradient(180deg, rgba(17,28,51,.94) 0%, rgba(11,19,36,.98) 100%);
box-shadow:var(--shadow-xl);
}}

.content-section::before{{
content:"";
position:absolute;
top:-120px;
right:-90px;
width:260px;
height:260px;
border-radius:50%;
background:radial-gradient(circle, rgba(34,211,238,.14), transparent 65%);
pointer-events:none;
}}

.content-section > *{{
position:relative;
z-index:1;
}}

.breadcrumbs{{
margin:0 0 16px;
font-size:13px;
font-weight:900;
color:#98adcf;
line-height:1.6;
}}

.breadcrumbs a{{
color:#9fdcf4;
font-weight:900;
}}

.info-box,
.hero-panel,
.tool-cta-card,
.section-card,
.meta-strip{{
background:linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
border:1px solid rgba(255,255,255,.10);
border-radius:24px;
box-shadow:var(--shadow-md);
}}

.hero-panel{{
padding:22px;
margin:0 0 18px;
background:
linear-gradient(135deg, rgba(34,211,238,.12) 0%, rgba(139,92,246,.12) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.05) 100%);
}}

.hero-panel-kicker{{
font-size:12px;
font-weight:900;
letter-spacing:.08em;
text-transform:uppercase;
color:#8be9ff;
margin-bottom:8px;
}}

.hero-panel h2{{
margin:0 0 8px;
font-size:30px;
line-height:1.08;
letter-spacing:-.03em;
color:#fff;
}}

.hero-panel p{{
margin:10px 0 0;
font-size:15px;
font-weight:800;
color:#d8e5f8;
line-height:1.75;
}}

.info-box{{
margin:0 0 20px;
padding:18px;
font-size:15px;
color:#d6e3f7;
font-weight:800;
line-height:1.7;
}}

h1,h2,h3{{
margin:0 0 14px;
color:#fff;
line-height:1.08;
letter-spacing:-.035em;
font-weight:900;
text-wrap:balance;
}}

h1{{font-size:42px;}}
h2{{font-size:30px;margin-top:0;}}
h3{{font-size:22px;margin-top:0;}}

p, li{{
font-size:17px;
color:#d7e4f8;
}}

p{{
margin:0 0 16px;
}}

ul,ol{{
margin:0;
padding-left:22px;
}}

li{{
margin-bottom:10px;
}}

li::marker{{
color:#8be9ff;
}}

.jump-links{{
display:flex;
flex-wrap:wrap;
gap:10px;
margin:0 0 22px;
}}

.jump-links a{{
display:inline-flex;
align-items:center;
justify-content:center;
padding:10px 13px;
border-radius:999px;
font-size:13px;
font-weight:900;
color:#dbeafe;
background:rgba(255,255,255,.06);
border:1px solid rgba(255,255,255,.10);
box-shadow:var(--shadow-sm);
}}

.jump-links a:hover{{
text-decoration:none;
transform:translateY(-1px);
}}

.tool-cta-card{{
margin:0 0 24px;
padding:24px;
text-align:center;
background:
linear-gradient(135deg, rgba(34,211,238,.10) 0%, rgba(139,92,246,.10) 100%),
linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.04) 100%);
}}

.tool-cta-card h3{{
margin:0 0 8px;
font-size:28px;
}}

.tool-cta-card p{{
margin:0 auto 14px;
max-width:620px;
font-size:15px;
line-height:1.7;
color:#c8d6ec;
font-weight:700;
}}

.tool-cta-button{{
display:block;
width:100%;
text-decoration:none;
text-align:center;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
font-weight:900;
padding:16px;
border-radius:18px;
box-shadow:0 18px 40px rgba(34,211,238,.20);
font-size:17px;
letter-spacing:.2px;
}}

.tool-cta-button:hover{{
text-decoration:none;
transform:translateY(-1px);
box-shadow:0 22px 44px rgba(34,211,238,.24);
}}

.tool-cta-note{{
margin-top:12px;
font-size:13px;
color:#9fb0cc;
font-weight:900;
}}

.section-card{{
padding:20px;
}}

.section-card p:last-child,
.section-card ul:last-child,
.section-card ol:last-child{{
margin-bottom:0;
}}

.warning-surface{{
background:
linear-gradient(135deg, rgba(34,211,238,.10) 0%, rgba(139,92,246,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.verify-surface{{
background:
linear-gradient(135deg, rgba(16,185,129,.10) 0%, rgba(34,211,238,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.link-surface{{
background:
linear-gradient(135deg, rgba(59,130,246,.10) 0%, rgba(139,92,246,.10) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.closing-surface{{
background:
linear-gradient(135deg, rgba(16,185,129,.08) 0%, rgba(139,92,246,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.faq-surface{{
background:
linear-gradient(135deg, rgba(139,92,246,.10) 0%, rgba(34,211,238,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.link-box{{
margin-top:16px;
padding:18px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
}}

.link-box ul{{
padding-left:20px;
}}

.link-box li{{
margin-bottom:12px;
}}

.link-box a{{
color:#8be9ff;
font-weight:900;
}}

.meta-strip{{
margin:22px 0 0;
padding:16px 18px;
font-size:14px;
font-weight:900;
color:#d8e5f8;
line-height:1.7;
}}

.section-divider{{
height:1px;
background:linear-gradient(90deg, transparent, rgba(139,92,246,.45), rgba(34,211,238,.45), transparent);
margin:28px 0;
}}

.faq-item + .faq-item{{
margin-top:12px;
padding-top:12px;
border-top:1px solid rgba(255,255,255,.10);
}}

.faq-item h3{{
font-size:20px;
margin-bottom:8px;
}}

.comparison-item{{
display:grid;
grid-template-columns:1fr 1fr;
gap:14px;
margin-top:14px;
}}

.comparison-col{{
padding:16px;
border-radius:18px;
border:1px solid rgba(255,255,255,.10);
background:rgba(255,255,255,.04);
}}

.comparison-col.nexus{{
background:var(--green-soft);
border-color:var(--green-line);
}}

.comparison-col.cex{{
background:var(--red-soft);
border-color:var(--red-line);
}}

.comparison-col h3{{
font-size:18px;
margin-bottom:8px;
}}

.comparison-col p:last-child{{
margin-bottom:0;
}}

@media (max-width:640px){{
body{{padding-top:84px;}}
.top-bar{{padding:10px 10px;}}
.top-actions{{gap:8px;margin-right:0;}}
.logo{{font-size:13px;margin-left:2px;padding:9px 12px;}}
.app-top{{font-size:13px;padding:8px 10px;}}
.checker-top{{font-size:13px;padding:8px 10px;margin-right:0;}}
.page-shell{{padding:0 12px 34px;}}
.hero{{padding:14px 6px 18px;}}
.hero h1{{font-size:34px;}}
.hero p{{margin-top:10px;font-size:17px;}}
.content-section{{padding:18px;border-radius:24px;}}
.hero-panel h2{{font-size:24px;}}
h1{{font-size:32px;}}
h2{{font-size:24px;}}
h3{{font-size:20px;}}
p,li{{font-size:16px;}}
.jump-links{{gap:8px;}}
.jump-links a{{font-size:13px;padding:9px 11px;}}
.comparison-item{{grid-template-columns:1fr;}}
}}
</style>
</head>
<body>

<div class="top-bar">
  <a class="logo" href="{SITE}/nexus-dex/">
    <span class="logo-dot"></span>
    <span>Nexus DEX</span>
  </a>
  <div class="top-actions">
    <a class="app-top" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">Get App</a>
    <a class="checker-top" href="{SITE}/nexus-dex/">Open Nexus DEX</a>
  </div>
</div>

<div class="page-shell">

  <div class="hero">
    <div class="hero-badge-row">
      <div class="hero-badge">Self-custodial</div>
      <div class="hero-badge">No KYC</div>
      <div class="hero-badge">Mobile-first</div>
    </div>

    <h1>{escape_html(hub_title)}</h1>
    <p>Explore features, compare workflows, and learn how this category works from a self-custodial Solana wallet.</p>

    <div class="hero-trust">
      <div class="hero-trust-chip">Wallet-based</div>
      <div class="hero-trust-chip">No signup</div>
      <div class="hero-trust-chip">On-chain settlement</div>
    </div>
  </div>

  <main class="content-section">
    <div class="breadcrumbs">
      <a href="{SITE}/">Home</a> / <a href="{SITE}/nexus-dex/">Nexus DEX</a> / <span>{escape_html(hub_title)}</span>
    </div>

    <div class="hero-panel">
      <div class="hero-panel-kicker">Category hub</div>
      <h2>Compare workflows faster</h2>
      <p>This hub groups together related Nexus DEX pages so you can review features, compare workflows, and quickly navigate to the most relevant pages in this category.</p>
    </div>

    <div class="info-box">
      Every workflow on Nexus DEX is self-custodial and wallet-based. Funds stay in your wallet between trades, there is no signup or KYC, and every position settles on-chain. The platform never holds your funds.
    </div>

    {cluster_specific_intro_html}
    <p>Use the related pages below to explore specific markets, assets, and workflows inside this category.</p>

    <nav class="jump-links" aria-label="Page sections">
      {jump_links_html}
    </nav>

    <div class="tool-cta-card">
      <h3>Ready to try it?</h3>
      <p>Connect a Solana wallet and start trading from your phone. No signup, no KYC, no centralized account, and one transaction signature per trade.</p>
      <a class="tool-cta-button" href="{SITE}/nexus-dex/">Open Nexus DEX</a>
      <div class="tool-cta-note">Self-custodial | No signup | Works on mobile</div>
    </div>

    {sections_html}

    <div class="meta-strip">
      Explore Nexus DEX features, compare workflows, and use the linked pages above to investigate specific markets and use cases inside this category.
    </div>
  </main>
</div>
</body>
</html>
"""


def save_hub(slug, html):
    folder = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "index.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def save_report(report):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    keywords = load_keywords()

    validation_warning_count = 0
    built_count = 0
    validation_details = []

    for hub_slug, raw_match_terms in CLUSTERS.items():
        match_terms = iter_match_terms(raw_match_terms)
        matched = [kw for kw in keywords if matches_cluster(kw, match_terms)] if keywords else []

        matched = dedupe_cluster_keywords(matched)
        matched = sorted(matched, key=lambda k: score_keyword(k, match_terms))[:MAX_LINKS_PER_HUB]

        link_items = build_related_link_items(matched)

        hub_title = HUB_TITLES.get(hub_slug, title_case(hub_slug.replace("-", " ")))
        intro = HUB_INTROS.get(hub_slug, INTRO_FALLBACK)
        description = trim_meta_description(HUB_META_DESCRIPTIONS.get(hub_slug, META_FALLBACK))
        canonical = build_canonical(hub_slug)

        top_topics_html = build_top_topics_html(matched, match_terms)
        key_features_html = build_key_features_html(hub_slug)
        related_topics_html = build_related_topics_html(match_terms)
        faq_html = build_faq_html(hub_slug)

        html = build_hub_html(
            hub_slug=hub_slug,
            hub_title=hub_title,
            description=description,
            intro=intro,
            link_items=link_items,
            top_topics_html=top_topics_html,
            key_features_html=key_features_html,
            related_topics_html=related_topics_html,
            faq_html=faq_html,
            matched_keywords=matched,
            hub_terms=match_terms,
        )

        validation_errors = validate_hub_output(
            hub_slug=hub_slug,
            hub_title=hub_title,
            description=description,
            canonical=canonical,
            matched_keywords=matched,
            link_items=link_items,
            html=html,
        )

        if validation_errors:
            validation_warning_count += 1
            validation_details.append({
                "hub_slug": hub_slug,
                "matched_keywords": len(matched),
                "linked_pages": len(link_items),
                "errors": validation_errors,
            })
            print(f"Validation warning for {hub_slug}: {'; '.join(validation_errors)}")

        save_hub(hub_slug, html)
        built_count += 1
        print(f"Built hub: {hub_slug} (matched keywords: {len(matched)}, linked pages: {len(link_items)})")

    report = {
        "keywords_loaded": len(keywords),
        "hubs_built": built_count,
        "validation_warnings": validation_warning_count,
        "validation_details": validation_details,
    }
    save_report(report)

    print("\n--- HUB BUILD REPORT ---")
    print(f"Keywords loaded: {len(keywords)}")
    print(f"Hubs built: {built_count}")
    print(f"Validation warnings: {validation_warning_count}")
    print(f"Saved report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
