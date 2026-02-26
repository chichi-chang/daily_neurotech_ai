# Neurotech Digest 🧠

A daily neurotech news digest — pulls from RSS/Google/Bing, filters with an LLM, 
and renders a clean local HTML page.

## Quick Start (free, local)

```bash
# 1. Install Python dependencies
pip install feedparser requests

# 2. Install Ollama (free, local LLM)
#    → https://ollama.com
ollama pull llama3.2

# 3. Run!
python run.py
```

That's it. Your digest opens in the browser automatically.

## Publishing to GitHub Pages

Run with `--deploy` to push the generated digest to GitHub Pages:

```bash
python run.py --deploy
```

The digest will be live at your `https://<username>.github.io/daily_neurotech_ai/` URL.
Your API keys stay local — only the rendered HTML is published.

---

## Switching Sources

Edit `config.py` — one line:

```python
SOURCE = "rss"     # free, default — great coverage
SOURCE = "google"  # 100 free queries/day — needs API keys
SOURCE = "bing"    # ~$3/1000 queries — needs API key
```

## Switching LLM Backend

```python
LLM_BACKEND = "ollama"   # free, local, private — recommended
LLM_BACKEND = "claude"   # ~$0.01/day — needs CLAUDE_API_KEY
LLM_BACKEND = "openai"   # ~$0.01/day — needs OPENAI_API_KEY
```

---

## Cost Breakdown

| Setup | Source | LLM | Monthly cost |
|---|---|---|---|
| **Fully free** | RSS | Ollama (local) | **$0** |
| Cheap cloud | RSS | Claude Haiku | **~$0.30** |
| More coverage | Google CSE | Ollama | **$0** (100 q/day free) |
| Best coverage | Bing News | Claude Haiku | **~$3-5** |

---

## Running Daily (Mac/Linux)

Add a cron job to run every morning at 8am:

```bash
crontab -e
# Add this line:
0 8 * * * cd /path/to/neurotech-digest && python run.py --no-open >> digest.log 2>&1
```

---

## Adding RSS Feeds

In `config.py`, add URLs to `RSS_FEEDS`. Good ones to add:
- `https://www.statnews.com/feed/` — STAT News (great biotech/neuro coverage)
- `https://www.mobihealthnews.com/rss.xml` — mobile health/medtech
- Your favorite neuro researchers' lab blogs
- Google Scholar alerts as RSS

## Debug Mode

```bash
python run.py --fetch-only   # see what's being fetched before LLM
python run.py --no-open      # generate without opening browser
python run.py --deploy       # generate + publish to GitHub Pages
```
