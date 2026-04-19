# clusters_map.py (Token Risk)

CLUSTERS = {

    "meme-token-risk": [

        "meme coin",

        "memecoin",

        "meme token",

        "microcap",

        "low cap",

        "moonshot",

        "pump",

        "degen",

        "viral token",

        "trending token",

    ],

    "buy-intent-risk": [

        "should i buy",

        "worth buying",

        "good investment",

        "safe to buy",

        "buy now",

        "entry",

        "exit",

        "hold or sell",

    ],

    "token-safety-check": [

        "safe",

        "legit",

        "risky",

        "scam",

        "real or fake",

        "trust",

        "dangerous",

    ],

    "token-metrics-risk": [

        "liquidity",

        "low liquidity",

        "high liquidity",

        "volume",

        "low volume",

        "fake volume",

        "pair age",

        "new pair",

        "fdv",

        "market cap",

        "price action",

        "slippage",

        "pool depth",

        "buyers",

        "sellers",

    ],

    "holder-risk": [

        "holders",

        "holder distribution",

        "wallet concentration",

        "whales",

        "top holders",

        "ownership",

    ],

    "contract-risk": [

        "contract",

        "smart contract",

        "mint function",

        "blacklist function",

        "owner control",

        "proxy contract",

        "upgradeable",

        "permissions",

    ],

    "honeypot-risk": [

        "honeypot",

        "cannot sell",

        "unsellable",

        "sell blocked",

        "sell tax",

        "high tax",

        "trading restriction",

    ],

    "rug-pull-risk": [

        "rug",

        "rug pull",

        "liquidity removed",

        "lp removed",

        "dev dump",

        "exit liquidity",

    ],

    "chain-solana": [

        "solana",

        "spl token",

        "raydium",

        "jupiter",

    ],

    "chain-ethereum": [

        "ethereum",

        "eth",

        "uniswap",

    ],

    "chain-base": [

        "base",

        "base chain",

    ],

    "chain-bsc": [

        "bsc",

        "binance smart chain",

        "pancakeswap",

    ],

    "chain-arbitrum": [

        "arbitrum",

    ],

    "new-token-risk": [

        "new token",

        "just launched",

        "stealth launch",

        "fair launch",

        "early token",

        "fresh launch",

    ],

    "post-buy-risk": [

        "i bought",

        "i swapped",

        "what now",

        "cannot sell",

        "lost money",

        "got scammed",

    ],

    "general-token-risk": [

        "token risk",

        "coin risk",

        "crypto risk",

        "token analysis",

        "token review",

        "is this token safe",

    ],

}

# --- Deterministic matching order (most specific → most general)

CLUSTER_PRIORITY = [

    "honeypot-risk",

    "rug-pull-risk",

    "contract-risk",

    "holder-risk",

    "token-metrics-risk",

    "buy-intent-risk",

    "post-buy-risk",

    "meme-token-risk",

    "new-token-risk",

    "chain-solana",

    "chain-ethereum",

    "chain-base",

    "chain-bsc",

    "chain-arbitrum",

    "token-safety-check",

    "general-token-risk",

]

# --- Fallback if nothing matches

DEFAULT_CLUSTER = "general-token-risk"

# --- Helpers

def _norm(text: str) -> str:

    return " ".join(str(text).lower().strip().split())

def _contains_phrase(haystack: str, needle: str) -> bool:

    # word-boundary-ish match to avoid partial hits

    import re

    h = _norm(haystack)

    n = _norm(needle)

    if not h or not n:

        return False

    pattern = r"(^|[^a-z0-9])" + re.escape(n) + r"([^a-z0-9]|$)"

    return re.search(pattern, h) is not None

def get_cluster_for_keyword(keyword: str) -> str:

    kw = _norm(keyword)

    for cluster in CLUSTER_PRIORITY:

        terms = CLUSTERS.get(cluster, [])

        for term in terms:

            if _contains_phrase(kw, term):

                return cluster

    return DEFAULT_CLUSTER