import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

keywords = open("data/keywords.txt").read().splitlines()

content_dir = "data/content"

os.makedirs(content_dir, exist_ok=True)

for kw in keywords:

    slug = kw.replace(" ","-")

    prompt = f"""
Write a short explanation about the topic: "{kw}".

Explain:
1. what the scam usually looks like
2. common warning signs
3. what someone should do if they receive it

Keep it under 120 words.
Plain language.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}]
    )

    text = response.choices[0].message.content.strip()

    with open(f"{content_dir}/{slug}.txt","w") as f:
        f.write(text)

    print("generated content for",kw)