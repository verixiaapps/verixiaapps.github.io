import os
from datetime import datetime

BASE_URL = "https://verixiaapps.com"
CHECK_DIR = "check"
OUTPUT_FILE = "discovery-c/latest/index.html"

def get_all_pages(directory):
    pages = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                full_path = os.path.join(root, file)
                pages.append(full_path)
    return pages

def generate():
    pages = get_all_pages(CHECK_DIR)

    # sort newest first
    pages.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    latest = pages[:200]

    links = []
    for file in latest:
        relative = file.replace(CHECK_DIR, "").replace("\\", "/").replace(".html", "")
        url = f"{BASE_URL}/check{relative}"
        name = relative.replace("/", " ").replace("-", " ").strip()

        links.append(f'<li><a href="{url}">{name}</a></li>')

    links_html = "\n".join(links)

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace(
        '<ul id="latest-list">\n    <!-- LINKS WILL BE AUTO-INJECTED -->\n  </ul>',
        f'<ul id="latest-list">\n{links_html}\n</ul>'
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ discovery latest updated with {len(latest)} links")

if __name__ == "__main__":
    generate()