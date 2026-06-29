#!/usr/bin/env python3
"""Generate SEO assets for Artemis Strength from data/exercises.json.

Produces:
  data/index.json        -- slim search index (now includes 's' = slug)
  data/ex/<id>.json       -- per-exercise detail (loaded on demand by the SPA)
  e/<slug>/index.html     -- crawlable static page per exercise (1,324 pages)
  sitemap.xml             -- lists the homepage + every exercise page
  robots.txt              -- allows crawling, points to the sitemap
  assets/og-default.jpg   -- 1200x630 branded social banner for the homepage

Run:  python build_seo.py
"""
import json, os, re, html
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://artemisstrength.in"
SRC = os.path.join(ROOT, "data", "exercises.json")
EXDIR = os.path.join(ROOT, "data", "ex")
PAGEDIR = os.path.join(ROOT, "e")
TODAY = date.today().isoformat()
LANG_NAMES = {"en": "English", "es": "Español", "it": "Italiano", "tr": "Türkçe"}


def slugify(s):
    s = s.lower().replace("/", " ").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


def esc(s):
    return html.escape(str(s), quote=True)


def cap(s):
    return str(s).strip().capitalize()


def page_html(e, slug, media):
    name = e["name"]
    title = f"{cap(name)} — How to, Muscles & Equipment | Artemis Strength"
    steps_en = (e.get("instruction_steps") or {}).get("en") or []
    para_en = (e.get("instructions") or {}).get("en") or ""
    desc = (para_en[:155] + "…") if len(para_en) > 156 else para_en
    if not desc:
        desc = f"{cap(name)}: target {e['target']}, equipment {e['equipment']}. Animated demo and step-by-step instructions."
    url = f"{SITE}/e/{slug}/"
    img = f"{SITE}/images/{media}.jpg"
    gif = f"{SITE}/videos/{media}.gif"

    # JSON-LD: HowTo (steps) + breadcrumb
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": cap(name),
        "description": desc,
        "image": img,
        "totalTime": "PT5M",
        "step": [{"@type": "HowToStep", "position": i + 1, "text": s}
                 for i, s in enumerate(steps_en)],
    }
    crumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": cap(name), "item": url},
        ],
    }

    steps_html = "".join(f"<li>{esc(s)}</li>" for s in steps_en) if steps_en \
        else (f"<li>{esc(para_en)}</li>" if para_en else "")
    sec_muscles = "".join(f"<span>{esc(m)}</span>" for m in e.get("secondary_muscles", []))

    # other languages as collapsible text (real crawlable content)
    other_langs = ""
    for lg in ("es", "it", "tr"):
        p = (e.get("instructions") or {}).get(lg)
        if p:
            other_langs += (f'<details><summary>{LANG_NAMES[lg]}</summary>'
                            f'<p>{esc(p)}</p></details>')

    return f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0d1117">
<link rel="canonical" href="{url}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css?v=6">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Artemis Strength">
<meta property="og:title" content="{esc(cap(name))} — Artemis Strength">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{img}">
<script type="application/ld+json">{json.dumps(howto, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(crumb, ensure_ascii=False)}</script>
</head>
<body class="detail">

<header>
  <div class="bar">
    <a class="logo" href="/" aria-label="Artemis Strength home">
      <svg class="mark" viewBox="0 0 32 32" width="30" height="30" aria-hidden="true">
        <rect width="32" height="32" rx="8" fill="var(--acc)"/>
        <g fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M7 25 L16 6 L25 25"/><path d="M11 18.5 H21"/>
        </g>
      </svg>
      <span class="brand"><b>ARTEMIS</b><i>STRENGTH</i></span>
    </a>
    <a class="backlink" href="/">← All exercises</a>
  </div>
</header>

<main class="article">
  <nav class="crumbs"><a href="/">Home</a> › <span>{esc(cap(name))}</span></nav>
  <article>
    <img class="hero" src="/videos/{media}.gif" width="420" height="420"
         alt="{esc(cap(name))} animation" loading="eager">
    <div class="info">
      <h1>{esc(cap(name))}</h1>
      <div class="kv">
        <span><b>Body part</b>{esc(cap(e['body_part']))}</span>
        <span><b>Equipment</b>{esc(cap(e['equipment']))}</span>
        <span><b>Target muscle</b>{esc(cap(e['target']))}</span>
        {f"<span><b>Muscle group</b>{esc(cap(e['muscle_group']))}</span>" if e.get('muscle_group') else ""}
      </div>
      {f'<div class="shead">Secondary muscles</div><div class="muscles">{sec_muscles}</div>' if sec_muscles else ''}
    </div>
  </article>

  <section>
    <h2>How to do {esc(cap(name))}</h2>
    <ol class="steps">{steps_html or '<li>Instructions coming soon.</li>'}</ol>
    {f'<div class="shead">Other languages</div>{other_langs}' if other_langs else ''}
  </section>

  <p class="cta"><a href="/">Browse all 1,324 exercises →</a></p>
</main>

<footer><div class="bar">
  <span>© {date.today().year} Artemis Strength · 1,324 exercises with animations</span>
  <a class="ig" href="https://www.instagram.com/artemis_strength" target="_blank" rel="noopener" aria-label="Follow @artemis_strength on Instagram">
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <rect x="2" y="2" width="20" height="20" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/>
    </svg>@artemis_strength</a>
</div></footer>
<script>
(function(){{var h=document.querySelector('header'),t=false;
addEventListener('scroll',function(){{if(t)return;t=true;requestAnimationFrame(function(){{
h.classList.toggle('hide',scrollY>140);t=false;}});}},{{passive:true}});}})();
</script>
</body>
</html>
"""


def make_banner():
    """1200x630 branded social banner using Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        print("  (Pillow missing — skipping og banner)")
        return
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#0d1117")
    d = ImageDraw.Draw(img)
    # accent panel
    d.rectangle([0, H - 14, W, H], fill="#ff5722")
    # logo badge
    d.rounded_rectangle([90, 230, 230, 370], radius=26, fill="#ff5722")
    d.line([120, 350, 160, 250, 200, 350], fill="#fff", width=11, joint="curve")
    d.line([138, 312, 182, 312], fill="#fff", width=11)

    def font(sz, bold=True):
        for name in (("arialbd.ttf" if bold else "arial.ttf"),
                     "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
            try:
                return ImageFont.truetype(name, sz)
            except Exception:
                continue
        return ImageFont.load_default()

    d.text((270, 238), "ARTEMIS", font=font(96), fill="#ffffff")
    d.text((273, 338), "S T R E N G T H", font=font(40), fill="#ff8a65")
    d.text((92, 430), "1,324 exercises · animations · multilingual guides",
           font=font(34, False), fill="#8b949e")
    out = os.path.join(ROOT, "assets", "og-default.jpg")
    img.save(out, "JPEG", quality=88)
    print(f"  wrote {os.path.relpath(out, ROOT)}")


def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(EXDIR, exist_ok=True)
    os.makedirs(PAGEDIR, exist_ok=True)

    slim, urls = [], []
    for e in data:
        base = os.path.basename(e["image"])
        media = os.path.splitext(base)[0]
        slug = f"{slugify(e['name'])}-{e['id']}"

        slim.append({"i": e["id"], "n": e["name"], "b": e["body_part"],
                     "q": e["equipment"], "t": e["target"], "m": media, "s": slug})

        detail = {"id": e["id"], "name": e["name"], "body_part": e["body_part"],
                  "equipment": e["equipment"], "target": e["target"],
                  "muscle_group": e.get("muscle_group"),
                  "secondary_muscles": e.get("secondary_muscles", []),
                  "instructions": e.get("instructions", {}),
                  "instruction_steps": e.get("instruction_steps", {}),
                  "media": media, "slug": slug}
        with open(os.path.join(EXDIR, e["id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(detail, f, ensure_ascii=False, separators=(",", ":"))

        pdir = os.path.join(PAGEDIR, slug)
        os.makedirs(pdir, exist_ok=True)
        with open(os.path.join(pdir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html(e, slug, media))
        urls.append(f"{SITE}/e/{slug}/")

    with open(os.path.join(ROOT, "data", "index.json"), "w", encoding="utf-8") as f:
        json.dump(slim, f, ensure_ascii=False, separators=(",", ":"))

    # sitemap
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
          f"<url><loc>{SITE}/</loc><lastmod>{TODAY}</lastmod>"
          f"<changefreq>weekly</changefreq><priority>1.0</priority></url>"]
    for u in urls:
        sm.append(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod>"
                  f"<changefreq>monthly</changefreq><priority>0.7</priority></url>")
    sm.append("</urlset>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm))

    # robots.txt
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)

    print(f"Generated {len(urls)} exercise pages, sitemap.xml, robots.txt, "
          f"index.json ({len(slim)} entries).")
    make_banner()


if __name__ == "__main__":
    main()
