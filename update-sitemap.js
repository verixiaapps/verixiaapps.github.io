const fs = require("fs");
const path = require("path");

const BASE_URL = "https://verixiaapps.com";
const PAGES_DIR = "./"; // adjust if pages are in subfolder
const MAX_URLS = 3000;

// find all html files
function getAllPages(dir) {
  let results = [];
  const list = fs.readdirSync(dir);

  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat && stat.isDirectory()) {
      results = results.concat(getAllPages(filePath));
    } else if (file.endsWith(".html") && !file.includes("404")) {
      results.push(filePath);
    }
  });

  return results;
}

const files = getAllPages(PAGES_DIR);

// convert to URLs
const urls = files.map(file => {
  let clean = file.replace(PAGES_DIR, "").replace(".html", "");
  clean = clean.replace(/\\/g, "/");
  return `${BASE_URL}/${clean}`;
});

let sitemapIndex = [];
let chunk = [];
let count = 1;

urls.forEach((url, i) => {
  chunk.push(`<url><loc>${url}</loc></url>`);

  if (chunk.length === MAX_URLS || i === urls.length - 1) {
    const sitemapContent = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${chunk.join("\n")}
</urlset>`;

    const filename = `sitemap-${count}.xml`;
    fs.writeFileSync(filename, sitemapContent);

    sitemapIndex.push(`<sitemap><loc>${BASE_URL}/${filename}</loc></sitemap>`);

    chunk = [];
    count++;
  }
});

// main sitemap index
const indexContent = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapIndex.join("\n")}
</sitemapindex>`;

fs.writeFileSync("sitemap.xml", indexContent);

console.log("Sitemaps generated successfully.");