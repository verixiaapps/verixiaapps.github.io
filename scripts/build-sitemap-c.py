import os
from datetime import datetime
from xml.sax.saxutils import escape

BASE_URL = "https://verixiaapps.com"

CHECK_DIR = "scam-check-now-c"
DISCOVERY_DIR = "discovery-c"

SITEMAP_INDEX_FILE = "sitemap-c-index.xml"
SITEMAP_PAGE_FILE = "sitemap-c-1.xml"
SITEMAP_DISCOVERY_FILE = "sitemap-c-discovery.xml"


def get_today():
    return datetime.utcnow().strftime("%Y-%m-%d")


def get_all_html_urls(directory, base_path):
    urls = []

    if not os.path.exists(directory):
        return urls

    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith(".html"):
                continue

            full_path = os.path.join(root, file)
            relative = os.path.relpath(full_path, directory).replace("\\", "/")

            if relative.endswith("index.html"):
                relative = relative[:-10]
            else:
                relative = relative[:-5]

            relative = relative.strip("/")

            url = f"{BASE_URL}/{base_path}/"
            if relative:
                url = f"{BASE_URL}/{base_path}/{relative}/"

            urls.append(url)

    return sorted(set(urls))


def build_url_entry(loc, lastmod, changefreq, priority):
    return f"""  <url>
    <loc>{escape(loc)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""


def write_page_sitemap():
    today = get_today()
    page_urls = get_all_html_urls(CHECK_DIR, "scam-check-now-c")

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in page_urls:
        xml.append(build_url_entry(url, today, "daily", "0.8"))

    xml.append("</urlset>")

    with open(SITEMAP_PAGE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(xml) + "\n")

    print(f"✅ Built {SITEMAP_PAGE_FILE} with {len(page_urls)} URLs from {CHECK_DIR}")


def write_discovery_sitemap():
    today = get_today()
    discovery_urls = get_all_html_urls(DISCOVERY_DIR, "discovery-c")

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in discovery_urls:
        xml.append(build_url_entry(url, today, "hourly", "1.0"))

    xml.append("</urlset>")

    with open(SITEMAP_DISCOVERY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(xml) + "\n")

    print(f"✅ Built {SITEMAP_DISCOVERY_FILE} with {len(discovery_urls)} URLs from {DISCOVERY_DIR}")


def write_sitemap_index():
    today = get_today()

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    xml.append("  <sitemap>")
    xml.append(f"    <loc>{escape(f'{BASE_URL}/{SITEMAP_PAGE_FILE}')}</loc>")
    xml.append(f"    <lastmod>{today}</lastmod>")
    xml.append("  </sitemap>")
    xml.append("  <sitemap>")
    xml.append(f"    <loc>{escape(f'{BASE_URL}/{SITEMAP_DISCOVERY_FILE}')}</loc>")
    xml.append(f"    <lastmod>{today}</lastmod>")
    xml.append("  </sitemap>")
    xml.append("</sitemapindex>")

    with open(SITEMAP_INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(xml) + "\n")

    print(f"✅ Built {SITEMAP_INDEX_FILE}")


def main():
    write_page_sitemap()
    write_discovery_sitemap()
    write_sitemap_index()
    print("✅ C sitemap system complete")


if __name__ == "__main__":
    main()