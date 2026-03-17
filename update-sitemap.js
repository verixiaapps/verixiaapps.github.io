const fs = require("fs");
const path = require("path");

// Base settings
const BASE_URL = "https://verixiaapps.com";
const APPS = ["scam-check-now", "job-check-now", "crypto-check-now", "review-check-now", "email-check-now", "website-check-now"];
const MAX_URLS = 3000; // per sitemap chunk

// Recursive function to get all HTML pages in a folder
function getAllPages(dir) {
  let results = [];
  const list = fs.readdirSync(dir);

  list.forEach(file => {
    const filePath = path.join(dir, file);

    try {
      const stat = fs.statSync(filePath);

      if (stat.isDirectory()) {
        results = results.concat(getAllPages(filePath));
      } else if (
        file.endsWith(".html") &&
        !file.includes("404") &&
        !file.includes("node_modules")
      ) {
        results.push(filePath);
      }
    } catch (e) {
      console.error("Error reading file:", filePath, e);
    }
  });

  return results;
}

// Generate per-app sitemaps
let sitemapIndex = [];
APPS.forEach(app => {
  const PAGES_DIR = `./${app}`;
  if (!fs.existsSync(PAGES_DIR)) return;

  const files = getAllPages(PAGES_DIR);
  const urls = files.map(file => {
    let clean = file.replace(PAGES_DIR, "").replace(/\\/g, "/");
    if (clean.endsWith("index.html")) clean = clean.replace("index.html", "");
    else clean = clean.replace(".html", "");
    if (clean.startsWith("/")) clean = clean.slice(1);
    return { url: `${BASE_URL}/${app}/${clean}`, filePath: file };
  });

  let chunk = [];
  let count = 1;

  urls.forEach((item, i) => {
    const lastmod = fs.existsSync(item.filePath) ? new Date(fs.statSync(item.filePath).mtime).toISOString().split("T")[0] : new Date().toISOString().split("T")[0];
    chunk.push(`<url>\n<loc>${item.url}</loc>\n<lastmod>${lastmod}</lastmod>\n</url>`);

    if (chunk.length === MAX_URLS || i === urls.length - 1) {
      const sitemapContent = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${chunk.join("\n")}\n</urlset>`;
      const filename = `${app}-sitemap-${count}.xml`;
      fs.writeFileSync(filename, sitemapContent);
      console.log(`Generated ${filename} (${chunk.length} URLs)`);

      sitemapIndex.push(`<sitemap><loc>${BASE_URL}/${filename}</loc></sitemap>`);
      chunk = [];
      count++;
    }
  });
});

// Generate main root sitemap index
const indexContent = `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemapIndex.join("\n")}\n</sitemapindex>`;
fs.writeFileSync("sitemap.xml", indexContent);

console.log("Root sitemap.xml generated successfully with all app sitemaps.");