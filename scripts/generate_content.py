import requests

RAILWAY_API = "https://awake-integrity-production-faa0.up.railway.app"


def generate_content(keyword):

    response = requests.post(
        f"{RAILWAY_API}/seo-content",
        json={"keyword": keyword},
        timeout=60
    )

    if response.status_code != 200:
        raise RuntimeError(f"Railway SEO content error: {response.status_code}")

    data = response.json()

    text = data.get("content", "").strip()

    if not text:
        raise RuntimeError("Empty content returned from Railway")

    return text


if __name__ == "__main__":

    sample = "amazon scam"
    print(generate_content(sample))