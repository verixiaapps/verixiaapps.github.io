import fs from "fs";
import path from "path";
import https from "https";

const SITE_URL = process.env.SITE_URL;
const SOURCE_SITEMAP_URL = process.env.SOURCE_SITEMAP_URL;
const DISCOVERY_DIR = process.env.DISCOVERY_DIR || "discovery";
const DISCOVERY_SITEMAP_PATH = process.env.DISCOVERY_SITEMAP_PATH || "discovery-sitemap.xml";

const MAX_LATEST = parseInt(process.env.MAX_LATEST_URLS || "100");
const MAX_TODAY = parseInt(process.env.MAX_TODAY_URLS || "100");
const MAX_WEEK = parseInt(process.env.MAX_THIS_WEEK_URLS || "700");
const MAX_HTML = parseInt(process.env.MAX_HTML_SITEMAP_URLS || "500");
const MAX_FEED = parseInt(process.env.MAX_FEED_URLS || "100");

function fetch(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => resolve(data));
    }).on("error", reject);
  });
}

function extractUrls(xml) {
  const matches = [...xml.matchAll(/<loc>(.*?)<\/loc>/g)];
  return matches.map((m) => m[1].trim());
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function writeFile(filePath, content) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, content);
}

function nowISO() {
  return new Date().toISOString();
}

function todayString() {
  return new Date().toISOString().slice(0, 10);
}

function htmlPage(title, urls) {
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>${title}</title>
</head>
<body>
<h1>${title}</h1>
<ul>
${urls.map((u) => `<li><a href="${u}">${u}</a></li>`).join("\n")}
</ul>
</body>
</html>`;
}

function buildXmlSitemap(urls) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .map(
    (u) => `<url>
  <loc>${u}</loc>
  <lastmod>${nowISO()}</lastmod>
</url>`
  )
  .join("\n")}
</urlset>`;
}

function buildFeed(urls) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Latest URLs</title>
<link>${SITE_URL}</link>
<description>Latest generated URLs</description>
${urls
  .map(
    (u) => `<item>
<title>${u}</title>
<link>${u}</link>
<pubDate>${new Date().toUTCString()}</pubDate>
</item>`
  )
  .join("\n")}
</channel>
</rss>`;
}

async function main() {
  console.log("Fetching main sitemap...");
  const xml = await fetch(SOURCE_SITEMAP_URL);

  const urls = extractUrls(xml);

  if (!urls.length) {
    console.error("No URLs found in sitemap.");
    process.exit(1);
  }

  const latest = urls.slice(-MAX_LATEST).reverse();
  const today = urls.slice(-MAX_TODAY).reverse();
  const week = urls.slice(-MAX_WEEK).reverse();
  const html = urls.slice(-MAX_HTML).reverse();
  const feed = urls.slice(-MAX_FEED).reverse();

  // Build pages
  writeFile(
    path.join(DISCOVERY_DIR, "latest/index.html"),
    htmlPage("Latest Pages", latest)
  );

  writeFile(
    path.join(DISCOVERY_DIR, "today/index.html"),
    htmlPage(`Pages Added ${todayString()}`, today)
  );

  writeFile(
    path.join(DISCOVERY_DIR, "this-week/index.html"),
    htmlPage("Pages This Week", week)
  );

  writeFile(
    path.join(DISCOVERY_DIR, "html-sitemap/index.html"),
    htmlPage("HTML Sitemap", html)
  );

  // Feed
  writeFile(
    path.join(DISCOVERY_DIR, "feeds/latest.xml"),
    buildFeed(feed)
  );

  // Discovery sitemap
  const discoveryUrls = [
    `${SITE_URL}/discovery/latest/`,
    `${SITE_URL}/discovery/today/`,
    `${SITE_URL}/discovery/this-week/`,
    `${SITE_URL}/discovery/html-sitemap/`,
    `${SITE_URL}/discovery/feeds/latest.xml`,
  ];

  writeFile(
    DISCOVERY_SITEMAP_PATH,
    buildXmlSitemap(discoveryUrls)
  );

  console.log("Discovery layer built successfully.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});