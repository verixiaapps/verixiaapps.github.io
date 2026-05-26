#!/usr/bin/env python3
"""
filter_keywords.py — drop keywords the new engine doesn't handle.

The engine v18.0 supports these intents:
    swap_token, bridge_chain, brand_token, meme_token, signals_discovery,
    commercial_native, education_native, general_native

DROPPED intents (no framing, no page type):
    - token_risk (scam, honeypot, rug, safety)
    - perps_defi (perpetuals, leverage, funding rate)
    - prediction_markets (polymarket, kalshi, YES/NO shares)

Usage:
    python3 filter_keywords.py data/nexus_dex_keywords.txt > data/nexus_dex_keywords.filtered.txt

Or in-place (creates a .bak):
    python3 filter_keywords.py --inplace data/nexus_dex_keywords.txt
"""

import sys
import re
import argparse
from pathlib import Path

# Patterns that should be DROPPED entirely
DROP_PATTERNS = [
    # Risk / scam / honeypot
    r"\b(scam|fraud|fake|phish)",
    r"\brug[\s-]?pull|\brugpull|\brug\b",
    r"\bhoneypot|honey[\s-]?pot",
    r"\bis\s+\w+\s+(safe|legit|legitimate)\b",
    r"\b(safe|unsafe)\s+to\s+(invest|buy|trade|ape)\b",
    r"\brisk\s+(score|score|level|scanner|checker)\b",
    r"\b(high|low)\s+risk\s+(token|coin)",
    r"\btoken\s+(risk|safety|checker|scanner|review)",
    r"\bsmart\s+contract\s+risk",
    r"\bsell\s+tax|\bbuy\s+tax|\bhidden\s+tax",
    r"\blp\s+lock|\bliquidity\s+lock|\blocked\s+liquidity",
    r"\bhonest\s+(review|opinion)",
    r"\b(dyor|do\s+your\s+own\s+research)\b",
    r"\bwhale\s+(concentration|wallet|distribution)",
    r"\bholder\s+(concentration|distribution)",
    r"\bmint\s+authority|\bfreeze\s+authority|\brenounce",
    r"\bbefore\s+(you\s+)?ape|\bbefore\s+aping",
    r"\bred\s+flag|\bwarning\s+signs?",
    r"\bexit\s+scam|\bpump\s+and\s+dump",

    # Perps / derivatives
    r"\bperp(s|etual(s|s?))?\b",
    r"\bfunding\s+rate|\bopen\s+interest\b|\bliquidation",
    r"\bleverag(e|ed)",
    r"\b(cross|isolated)[\s-]?margin",
    r"\bperp\s+dex|\bperpetual\s+(dex|trading|swap|protocol)",
    r"\bdrift\s+protocol|\bzeta\s+markets?|\bmango\s+markets?",
    r"\bjupiter\s+perps?\b|\bflash\s+trade\b",
    r"\bhyperliquid",
    r"\bmark\s+price|\bbasis|\bvamm|\bnotional",
    r"\blong\s+short\s+ratio",
    r"\b(50x|100x|10x|25x|leverage|leveraged)\s+(long|short|trading)",

    # Prediction markets
    r"\bprediction\s+(market|markets|trading|platform|protocol|dex|defi)\b",
    r"\bpolymarket\b|\bkalshi\b",
    r"\b(yes|no)\s+shares?\b",
    r"\bbinary\s+(market|outcome|trading)",
    r"\bimplied\s+probability",
    r"\boutcome\s+(market|trading|shares?)\b",
    r"\bwill\s+(bitcoin|btc|ethereum|eth|solana|sol|pepe|wif|bonk)\s+(hit|reach|cross|break|touch|moon)",
    r"\b(memecoin|altcoin)\s+(prediction|forecast|outcome)\b",
    r"\bgraduate\s+(from\s+)?bonding\s+curve",
    r"\bprediction\s+market\s+no[\s-]?kyc",
    r"\bcrypto\s+prediction\s+market",
]

# Pre-compile for speed
COMPILED_DROPS = [re.compile(p, re.IGNORECASE) for p in DROP_PATTERNS]


def should_drop(keyword: str) -> tuple[bool, str]:
    """Returns (drop?, reason). Reason is the pattern that matched, or ''."""
    kw = keyword.strip()
    if not kw:
        return True, "empty"
    for i, pattern in enumerate(COMPILED_DROPS):
        if pattern.search(kw):
            return True, DROP_PATTERNS[i]
    return False, ""


def filter_file(input_path: Path, output_stream, verbose: bool = False):
    kept = 0
    dropped = 0
    drop_reasons = {}

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            kw = line.strip()
            if not kw:
                continue
            drop, reason = should_drop(kw)
            if drop:
                dropped += 1
                drop_reasons[reason] = drop_reasons.get(reason, 0) + 1
                if verbose:
                    print(f"  DROP: {kw}  (matched: {reason})", file=sys.stderr)
            else:
                kept += 1
                output_stream.write(kw + "\n")

    print(f"\nKept:    {kept} keywords", file=sys.stderr)
    print(f"Dropped: {dropped} keywords", file=sys.stderr)
    if drop_reasons:
        print("\nTop drop reasons:", file=sys.stderr)
        sorted_reasons = sorted(drop_reasons.items(), key=lambda x: -x[1])
        for reason, count in sorted_reasons[:10]:
            print(f"  {count:4d}  {reason}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Filter keywords for Verixia engine v18.0")
    parser.add_argument("input", help="Path to keyword file (one per line)")
    parser.add_argument("--inplace", action="store_true", help="Overwrite input file (creates .bak)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print each dropped keyword")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.inplace:
        backup_path = input_path.with_suffix(input_path.suffix + ".bak")
        input_path.rename(backup_path)
        with open(input_path, "w", encoding="utf-8") as out:
            filter_file(backup_path, out, verbose=args.verbose)
        print(f"\nFiltered file written to: {input_path}", file=sys.stderr)
        print(f"Original backed up to:    {backup_path}", file=sys.stderr)
    else:
        filter_file(input_path, sys.stdout, verbose=args.verbose)


if __name__ == "__main__":
    main()
