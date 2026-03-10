import os
import re
import time
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

KEYWORDS_FILE = "data/keywords.txt"
CONTENT_DIR = "data/content"

os.makedirs(CONTENT_DIR, exist_ok=True)


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip("-")


with open(KEYWORDS_FILE) as f:
    keywords = [k.strip() for k in f.readlines() if k.strip()]


for kw in keywords:

    slug = slugify(kw)
    file_path = f"{CONTENT_DIR}/{slug}.txt"

    # Skip if already generated
    if os.path.exists(file_path):
        print("skip existing", kw)
        continue

    prompt = f"""
Write a short explanation about the topic: "{kw}".

Explain:
1. what the scam usually looks like
2. common warning signs
3. what someone should do if they receive it

Rules:
- maximum 120 words
- plain language
- avoid repeating the keyword excessively
- write as informational content for a website
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content.strip()

        with open(file_path, "w") as f:
            f.write(text)

        print("generated content for", kw)

        # small delay prevents rate limits
        time.sleep(1)

    except Exception as e:

        print("error generating content for", kw)
        print(e)