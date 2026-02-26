"""
renderer.py — Turn categorized articles into a beautiful HTML digest.
"""

import datetime

CATEGORY_META = {
    "approval":  {"label": "Approvals & Regulatory", "icon": "✦", "color": "#4a9eff"},
    "funding":   {"label": "Funding & Deals",         "icon": "◈", "color": "#ff6b35"},
    "research":  {"label": "Research → Industry",     "icon": "◎", "color": "#7eb8f7"},
    "product":   {"label": "Products & Launches",     "icon": "◆", "color": "#d4a8ff"},
    "policy":    {"label": "Policy & Ethics",          "icon": "◉", "color": "#ffd166"},
    "neuro_ai":  {"label": "Neuro-AI",                  "icon": "◈", "color": "#c084fc"},
    "ai_tool":   {"label": "AI Tools & Products",      "icon": "◇", "color": "#00d4ff"},
    "other":     {"label": "Notable News",             "icon": "○", "color": "#aaaaaa"},
}

CATEGORY_ORDER = ["approval", "funding", "research", "neuro_ai", "product", "ai_tool", "policy", "other"]


def render(articles, config, output_path):
    today = datetime.date.today().strftime("%B %d, %Y")
    source_label = {"rss": "RSS Feeds", "google": "Google Search", "bing": "Bing News"}.get(config.SOURCE, config.SOURCE)

    # Group by category
    grouped = {cat: [] for cat in CATEGORY_ORDER}
    for a in articles:
        cat = a.get("category", "other").lower()
        if cat not in grouped:
            cat = "other"
        grouped[cat].append(a)

    # Build sections HTML
    sections_html = ""
    total = 0
    for cat in CATEGORY_ORDER:
        items = grouped[cat]
        if not items:
            continue
        total += len(items)
        meta = CATEGORY_META[cat]
        cards = ""
        for a in items:
            cards += f"""
            <a class="card" href="{a.get('url','#')}" target="_blank" rel="noopener">
                <div class="card-source">{a.get('source','')}</div>
                <div class="card-title">{a.get('title','')}</div>
                <div class="card-summary">{a.get('one_line_summary', a.get('summary',''))}</div>
                <div class="card-arrow">→</div>
            </a>"""

        sections_html += f"""
        <section class="category" data-cat="{cat}">
            <div class="cat-header">
                <span class="cat-icon" style="color:{meta['color']}">{meta['icon']}</span>
                <h2 class="cat-title">{meta['label']}</h2>
                <span class="cat-count" style="background:{meta['color']}20;color:{meta['color']}">{len(items)}</span>
            </div>
            <div class="cards">{cards}</div>
        </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Neurotech & AI Signal — {today}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>@import url('https://fonts.cdnfonts.com/css/helvetica-neue-55');</style>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg: #0a0a0f;
    --surface: #111118;
    --border: #1e1e2e;
    --text: #e8e8f0;
    --muted: #5a5a7a;
    --accent: #4a9eff;
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    min-height: 100vh;
    padding: 0 0 80px;
  }}

  /* Scanline overlay */
  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.03) 2px,
      rgba(0,0,0,0.03) 4px
    );
    pointer-events: none;
    z-index: 999;
  }}

  header {{
    border-bottom: 1px solid var(--border);
    padding: 48px 64px 32px;
    position: relative;
    overflow: hidden;
  }}

  header::after {{
    content: 'NEURO × AI';
    position: absolute;
    right: -20px;
    top: 50%;
    transform: translateY(-50%);
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 160px;
    color: #ffffff04;
    letter-spacing: -4px;
    pointer-events: none;
    user-select: none;
  }}

  .header-meta {{
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 16px;
  }}

  h1 {{
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: clamp(36px, 5vw, 64px);
    font-weight: 400;
    font-style: italic;
    letter-spacing: -1px;
    line-height: 1.1;
  }}

  h1 span {{
    color: var(--accent);
    font-style: normal;
  }}

  .header-stats {{
    margin-top: 24px;
    display: flex;
    gap: 32px;
    flex-wrap: wrap;
  }}

  .stat {{
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}

  .stat-value {{
    font-size: 24px;
    font-weight: 700;
    color: var(--accent);
  }}

  .stat-label {{
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
  }}

  /* Filter bar */
  .filter-bar {{
    padding: 20px 64px;
    border-bottom: 1px solid var(--border);
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }}

  .filter-label {{
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-right: 8px;
  }}

  .filter-btn {{
    background: none;
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 6px 14px;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 13px;
    letter-spacing: 1px;
    cursor: pointer;
    transition: all 0.15s;
  }}

  .filter-btn:hover, .filter-btn.active {{
    border-color: var(--accent);
    color: var(--accent);
  }}

  /* Main content */
  main {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 48px 64px 0;
  }}

  .category {{ margin-bottom: 56px; }}

  .cat-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
  }}

  .cat-icon {{ font-size: 20px; }}

  .cat-title {{
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text);
  }}

  .cat-count {{
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 2px;
    font-weight: 700;
  }}

  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1px;
    background: var(--border);
  }}

  .card {{
    display: block;
    background: var(--surface);
    padding: 20px 24px;
    text-decoration: none;
    color: inherit;
    position: relative;
    transition: background 0.15s;
    overflow: hidden;
  }}

  .card:hover {{ background: #16161f; }}

  .card:hover .card-arrow {{
    opacity: 1;
    transform: translateX(0);
  }}

  .card-source {{
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
  }}

  .card-title {{
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 20px;
    line-height: 1.35;
    color: var(--text);
    margin-bottom: 10px;
  }}

  .card-summary {{
    font-size: 14px;
    line-height: 1.7;
    color: #7878a0;
    padding-right: 20px;
  }}

  .card-arrow {{
    position: absolute;
    bottom: 20px;
    right: 20px;
    font-size: 16px;
    color: var(--accent);
    opacity: 0;
    transform: translateX(-8px);
    transition: all 0.2s;
  }}

  .empty {{
    text-align: center;
    padding: 80px 20px;
    color: var(--muted);
    font-size: 15px;
    letter-spacing: 2px;
  }}

  footer {{
    text-align: center;
    padding: 40px;
    color: var(--muted);
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
    border-top: 1px solid var(--border);
    margin-top: 40px;
  }}

  @media (max-width: 768px) {{
    header, .filter-bar, main {{ padding-left: 24px; padding-right: 24px; }}
    header::after {{ display: none; }}
  }}
</style>
</head>
<body>

<header>
  <div class="header-meta">Neurotech · AI Tools · Neuro-AI</div>
  <h1>The Daily<br><span>Signal</span></h1>
  <div class="header-stats">
    <div class="stat">
      <span class="stat-value">{today}</span>
      <span class="stat-label">Date</span>
    </div>
    <div class="stat">
      <span class="stat-value">{total}</span>
      <span class="stat-label">Stories</span>
    </div>
    <div class="stat">
      <span class="stat-value">{source_label}</span>
      <span class="stat-label">Source</span>
    </div>
  </div>
</header>

<div class="filter-bar">
  <span class="filter-label">Filter</span>
  <button class="filter-btn active" onclick="filterCat('all', this)">All</button>
  {"".join(
    f'<button class="filter-btn" onclick="filterCat(\'{cat}\', this)">{CATEGORY_META[cat]["icon"]} {CATEGORY_META[cat]["label"]}</button>'
    for cat in CATEGORY_ORDER if grouped[cat]
  )}
</div>

<main>
  {"".join([f'<div class="empty">No articles found today. Try adjusting your RSS feeds or search queries in config.py.</div>' if total == 0 else sections_html])}
</main>

<footer>
  Generated {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} · Source: {source_label} · LLM: {config.LLM_BACKEND}
</footer>

<script>
function filterCat(cat, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.category').forEach(sec => {{
    if (cat === 'all' || sec.dataset.cat === cat) {{
      sec.style.display = '';
    }} else {{
      sec.style.display = 'none';
    }}
  }});
}}
</script>

</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[render] Digest written to: {output_path}")
