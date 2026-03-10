import os

SEED_FILE = "data/seed_keywords.txt"
PATTERN_FILE = "data/patterns.txt"
OUTPUT_FILE = "data/keywords.txt"


# ensure data directory exists
os.makedirs("data", exist_ok=True)


# load seeds
with open(SEED_FILE) as f:
    seeds = [s.strip() for s in f.readlines() if s.strip()]


# load patterns
with open(PATTERN_FILE) as f:
    patterns = [p.strip() for p in f.readlines() if p.strip()]


keywords = set()


for seed in seeds:
    for pattern in patterns:

        kw = pattern.replace("{keyword}", seed)

        kw = kw.strip().lower()

        keywords.add(kw)


# sort for stable output
keywords = sorted(list(keywords))


with open(OUTPUT_FILE, "w") as f:
    for kw in keywords:
        f.write(kw + "\n")


print("Generated", len(keywords), "keywords")