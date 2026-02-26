"""
fetchers.py — Pull articles from RSS, Google, or Bing.
Switch source via config.py — no code changes needed.
"""

import datetime
import re
import sys


def _matches_keywords(text, keywords):
    """Check if text matches any keyword. Uses word-boundary matching for
    short keywords (<=3 chars) to avoid false positives like 'ai' in 'brain'."""
    text_lower = text.lower()
    for kw in keywords:
        if len(kw) <= 3:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                return True
        else:
            if kw in text_lower:
                return True
    return False

def fetch_articles(config):
    source = config.SOURCE
    print(f"[fetch] Using source: {source}")

    if source == "rss":
        return fetch_rss(config)
    elif source == "google":
        return fetch_google(config)
    elif source == "bing":
        return fetch_bing(config)
    elif source == "hn":
        return fetch_hn(config)
    elif source == "rss+hn":
        # Combine RSS and HN — best free option
        rss = fetch_rss(config)
        hn = fetch_hn(config)
        seen = {a["url"] for a in rss}
        combined = rss + [a for a in hn if a["url"] not in seen]
        print(f"[fetch] Combined total: {len(combined)} articles")
        return combined[:config.MAX_ARTICLES_IN_DIGEST]
    else:
        sys.exit(f"Unknown SOURCE '{source}' in config.py")


# ── RSS ──────────────────────────────────────────────────────────────────────

def fetch_rss(config):
    try:
        import feedparser
    except ImportError:
        sys.exit("feedparser not installed. Run: pip install feedparser")

    keywords = [k.lower() for k in config.RSS_KEYWORDS]
    no_filter_feeds = set(getattr(config, "RSS_FEEDS_NO_KEYWORD_FILTER", []))
    all_feeds = list(config.RSS_FEEDS) + list(no_filter_feeds - set(config.RSS_FEEDS))
    articles = []
    days_back = getattr(config, "RSS_DAYS_BACK", 1)
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_back)

    for url in all_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                link = entry.get("link", "")

                # Date check — only last 24h (gracefully skip if no date)
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    pub_dt = datetime.datetime(*published[:6], tzinfo=datetime.timezone.utc)
                    if pub_dt < cutoff:
                        continue

                # Keyword filter (skip for pre-curated feeds)
                if url not in no_filter_feeds:
                    combined = title + " " + summary
                    if not _matches_keywords(combined, keywords):
                        continue

                articles.append({
                    "title": title.strip(),
                    "summary": _clean_html(summary)[:500],
                    "url": link,
                    "source": feed.feed.get("title", url),
                })

                if len(articles) >= config.MAX_ARTICLES_IN_DIGEST:
                    break
        except Exception as e:
            print(f"[rss] Failed to fetch {url}: {e}")

    print(f"[fetch] Got {len(articles)} articles from RSS")
    return articles


# ── GOOGLE CUSTOM SEARCH ─────────────────────────────────────────────────────

def fetch_google(config):
    try:
        import requests
    except ImportError:
        sys.exit("requests not installed. Run: pip install requests")

    if not config.GOOGLE_API_KEY or not config.GOOGLE_CSE_ID:
        sys.exit("Set GOOGLE_API_KEY and GOOGLE_CSE_ID in config.py")

    articles = []
    seen_urls = set()

    for query in config.GOOGLE_QUERIES:
        try:
            resp = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": config.GOOGLE_API_KEY,
                    "cx": config.GOOGLE_CSE_ID,
                    "q": query,
                    "num": config.GOOGLE_RESULTS_PER_QUERY,
                    "dateRestrict": "d1",   # last 24 hours
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("items", []):
                url = item.get("link", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                articles.append({
                    "title": item.get("title", "").strip(),
                    "summary": item.get("snippet", "").strip(),
                    "url": url,
                    "source": item.get("displayLink", ""),
                })
        except Exception as e:
            print(f"[google] Query '{query}' failed: {e}")

    print(f"[fetch] Got {len(articles)} articles from Google")
    return articles[:config.MAX_ARTICLES_IN_DIGEST]


# ── BING SEARCH ───────────────────────────────────────────────────────────────

def fetch_bing(config):
    try:
        import requests
    except ImportError:
        sys.exit("requests not installed. Run: pip install requests")

    if not config.BING_API_KEY:
        sys.exit("Set BING_API_KEY in config.py")

    articles = []
    seen_urls = set()

    for query in config.BING_QUERIES:
        try:
            resp = requests.get(
                "https://api.bing.microsoft.com/v7.0/news/search",
                headers={"Ocp-Apim-Subscription-Key": config.BING_API_KEY},
                params={
                    "q": query,
                    "count": config.BING_RESULTS_PER_QUERY,
                    "freshness": "Day",
                    "mkt": "en-US",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("value", []):
                url = item.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                articles.append({
                    "title": item.get("name", "").strip(),
                    "summary": item.get("description", "").strip(),
                    "url": url,
                    "source": item.get("provider", [{}])[0].get("name", ""),
                })
        except Exception as e:
            print(f"[bing] Query '{query}' failed: {e}")

    print(f"[fetch] Got {len(articles)} articles from Bing")
    return articles[:config.MAX_ARTICLES_IN_DIGEST]


# ── HACKER NEWS (Algolia API — free, no key needed) ──────────────────────────

HN_QUERIES = [
    "neurotech", "brain computer interface", "BCI", "neuralink",
    "neural implant", "neurostimulation", "deep brain stimulation",
]

def fetch_hn(config):
    try:
        import requests
    except ImportError:
        sys.exit("requests not installed. Run: pip install requests")

    days_back = getattr(config, "RSS_DAYS_BACK", 1)
    cutoff_ts = int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_back)).timestamp())
    hn_queries = getattr(config, "HN_QUERIES", HN_QUERIES)

    articles = []
    seen_urls = set()

    for query in hn_queries:
        try:
            resp = requests.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": query,
                    "tags": "(story,show_hn,ask_hn)",
                    "numericFilters": f"created_at_i>{cutoff_ts}",
                    "hitsPerPage": 10,
                },
                timeout=10,
            )
            resp.raise_for_status()
            for hit in resp.json().get("hits", []):
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                articles.append({
                    "title": hit.get("title", "").strip(),
                    "summary": f"HN: {hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments",
                    "url": url,
                    "source": "Hacker News",
                })
        except Exception as e:
            print(f"[hn] Query '{query}' failed: {e}")

    print(f"[fetch] Got {len(articles)} articles from Hacker News")
    return articles[:config.MAX_ARTICLES_IN_DIGEST]


# ── UTILS ─────────────────────────────────────────────────────────────────────

def _clean_html(text):
    return re.sub(r"<[^>]+>", " ", text).strip()
