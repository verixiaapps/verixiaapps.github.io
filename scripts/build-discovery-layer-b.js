const fs = require("fs");
const path = require("path");

const SITE_URL = (process.env.SITE_URL || "https://verixiaapps.com").replace(/\/+$/, "");
const DISCOVERY_DIR = process.env.DISCOVERY_DIR || "discovery-b";
const OUTPUT_SITEMAP = process.env.DISCOVERY_SITEMAP_PATH || "discovery-b-sitemap.xml";
const ROOT_DIR = path.join(process.cwd(), "scam-check-now-b");

function getAllPages(dir) {
  if (!fs.existsSync(dir)) return [];

  const folders = fs.readdirSync(dir, { withFileTypes: true });
  const pages = [];

  for (const f of folders) {
    if (!f.isDirectory()) continue;

    const pagePath = path.join(dir, f.name, "index.html");
    if (!fs.existsSync(pagePath)) continue;

    pages.push({
      slug: f.name,
      path: `/scam-check-now-b/${f.name}/`,
      mtime: fs.statSync(pagePath).mtime
    });
  }

  return pages;
}

function sortByNewest(pages) {
  return [...pages].sort((a, b) => b.mtime - a.mtime);
}

function limit(arr, n) {
  return arr.slice(0, n);
}

function writeHtml(filePath, urls) {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="robots" content="index,follow">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Discovery B</title>
</head>
<body>
  <h1>Latest Pages</h1>
  <ul>
    ${urls.map(u => `<li><a href="${SITE_URL}${u.path}">${u.path}</a></li>`).join("\n")}
  </ul>
</body>
</html>`;

  fs.writeFileSync(filePath, html, "utf8");
}

function writeXml(filePath, urls) {
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(u => `  <url>
    <loc>${SITE_URL}${u.path}</loc>
    <lastmod>${u.mtime.toISOString()}</lastmod>
  </url>`).join("\n")}
</urlset>`;

  fs.writeFileSync(filePath, xml, "utf8");
}

function run() {
  const maxLatest = Number.parseInt(process.env.MAX_LATEST_URLS || "100", 10);
  const safeMaxLatest = Number.isFinite(maxLatest) && maxLatest > 0 ? maxLatest : 100;

  const pages = getAllPages(ROOT_DIR);
  const latest = limit(sortByNewest(pages), safeMaxLatest);

  const discoveryPath = path.join(process.cwd(), DISCOVERY_DIR);
  fs.mkdirSync(discoveryPath, { recursive: true });

  writeHtml(path.join(discoveryPath, "index.html"), latest);
  writeXml(path.join(process.cwd(), OUTPUT_SITEMAP), latest);

  console.log(`Generated ${latest.length} discovery URLs for B`);
}

run();