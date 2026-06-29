# Deploying the Exercise Library to cPanel

This site is **100% static** — plain HTML, CSS, and JavaScript. It needs **no PHP,
Node, Python, or database**, so it runs on the cheapest cPanel plan and is as fast
as your host can serve files. (PHP/Node/Python are all available on cPanel if you
ever want them, but this site deliberately needs none of them — static is fastest.)

## What to upload

Upload the **entire contents** of this folder into `public_html` (or a subfolder),
keeping the directory structure intact:

```
public_html/
├── index.html          ← the app (2.4 KB)
├── .htaccess           ← gzip + caching + no directory listing
├── robots.txt          ← lets crawlers in, points to the sitemap
├── sitemap.xml         ← lists the homepage + all 1,324 exercise pages
├── assets/
│   ├── app.js
│   ├── style.css
│   ├── favicon.svg
│   └── og-default.jpg  ← social share banner
├── data/
│   ├── index.json      ← slim search index (~150 KB, loads instantly)
│   └── ex/             ← 1,324 per-exercise detail files (for the SPA)
├── e/                  ← 1,324 crawlable static exercise pages (SEO)
│   └── <slug>/index.html
├── images/             ← 1,324 thumbnails (.jpg)
└── videos/             ← 1,324 animations (.gif)
```

You can delete these — they are not used by the live site:
`index-legacy.html`, `setup.html`, `README.md`, `DEPLOY.md`, `build_data.py`,
`build_seo.py`, `data/exercises.json`, `.git/`.
(`data/exercises.json` is the original full dump; the site reads the split files.
`build_seo.py` regenerates `e/`, `sitemap.xml`, `robots.txt` and the index if data changes.)

## Steps

1. **Zip & upload (fastest):** In cPanel **File Manager**, open `public_html`,
   click **Upload**, and upload a ZIP of this folder. Then right-click the ZIP →
   **Extract**. Uploading ~2,650 media files individually over FTP is slow — zip first.
2. Make sure **`.htaccess` is present** in `public_html`. File Manager hides dotfiles
   by default → **Settings → Show Hidden Files (dotfiles)**.
3. Visit your domain. Done.

## Get indexed by Google

1. Confirm these load in a browser after upload:
   `https://artemisstrength.in/robots.txt`,
   `https://artemisstrength.in/sitemap.xml`, and any exercise page e.g.
   `https://artemisstrength.in/e/air-bike-0003/`.
2. Go to **[Google Search Console](https://search.google.com/search-console)** →
   add property `artemisstrength.in` → verify (the DNS or HTML-file method works on cPanel).
3. In Search Console open **Sitemaps** and submit `sitemap.xml`.
4. (Optional) Do the same in **[Bing Webmaster Tools](https://www.bing.com/webmasters)**.

Google will then crawl all 1,325 URLs. Indexing takes days to a few weeks — that's
normal; the sitemap just makes sure nothing is missed.

## Why it's fast

- Homepage is **2.4 KB**; the search index is **~145 KB** (≈30 KB gzipped).
- Full exercise details load **on demand**, one ~4 KB file per click.
- Images/GIFs are **lazy-loaded** and rendered in batches as you scroll.
- `.htaccess` enables **gzip** and **1-year immutable caching** for media/CSS/JS.

## Optional speed boosts

- **Enable a CDN** (Cloudflare is free) in front of the domain — caches everything globally.
- In cPanel, if **LiteSpeed** is available, the `.htaccess` rules work as-is and LiteSpeed
  serves static files even faster than Apache.
- Convert thumbnails to **WebP** to cut image weight ~70% (optional; JPGs already cache well).

## Updating the data

If `data/exercises.json` changes, regenerate the split files by re-running the
generator (see project notes), then re-upload `data/index.json` and `data/ex/`.
