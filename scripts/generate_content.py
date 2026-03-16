import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def generate_content(keyword):

    prompt = f"""
Write a short informational explanation for the topic: "{keyword}".

Explain:
1. what the scam usually looks like
2. common warning signs
3. what someone should do if they encounter it

Rules:
- maximum 120 words
- plain language
- informational tone
- avoid repeating the keyword excessively
- do not include headings
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content.strip()

    return text


if __name__ == "__main__":

    # simple test mode
    sample = "amazon scam"
    print(generate_content(sample))