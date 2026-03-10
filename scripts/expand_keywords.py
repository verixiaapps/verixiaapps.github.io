import os

seed_file = "data/seed_keywords.txt"
pattern_file = "data/patterns.txt"

output_file = "data/keywords.txt"

seeds = open(seed_file).read().splitlines()
patterns = open(pattern_file).read().splitlines()

keywords = []

for seed in seeds:

    for pattern in patterns:

        kw = pattern.replace("{keyword}", seed)

        keywords.append(kw)


keywords = list(set(keywords))

with open(output_file,"w") as f:

    for kw in keywords:

        f.write(kw + "\n")

print("Generated", len(keywords), "keywords")