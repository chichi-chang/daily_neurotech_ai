#!/usr/bin/env python3
"""
run.py — Neurotech Digest entry point.

Usage:
  python run.py              # fetch + analyze + open digest
  python run.py --no-open    # fetch + analyze, don't open browser
  python run.py --fetch-only # just print raw fetched articles (debug)
"""

import argparse
import os
import sys
import webbrowser
import pathlib

import config
import fetchers
import llm
import renderer


def main():
    parser = argparse.ArgumentParser(description="Neurotech daily digest generator")
    parser.add_argument("--no-open",    action="store_true", help="Don't open browser")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch, skip LLM")
    args = parser.parse_args()

    print("=" * 50)
    print("  THE DAILY SIGNAL — Neurotech & AI")
    print("=" * 50)

    # 1. Fetch
    articles = fetchers.fetch_articles(config)

    if not articles:
        print("[!] No articles fetched. Check your config and network.")
        sys.exit(1)

    if args.fetch_only:
        print(f"\nFetched {len(articles)} articles:\n")
        for a in articles:
            print(f"  [{a['source']}] {a['title']}")
            print(f"    {a['url']}\n")
        return

    # 2. LLM analysis
    analyzed = llm.analyze(articles, config)
    print(f"[llm] {len(analyzed)} articles passed relevance filter")

    kept_urls = {a.get("url") for a in analyzed}
    rejected = [a for a in articles if a["url"] not in kept_urls]
    if rejected:
        print(f"[llm] {len(rejected)} articles filtered out:")
        for a in rejected:
            print(f"       ✗ [{a['source']}] {a['title']}")

    if not analyzed:
        print("[!] LLM returned no relevant articles.")
        print("    Try: python run.py --fetch-only  to check raw fetched articles")
        sys.exit(1)

    # 3. Render
    output_path = pathlib.Path(__file__).parent / config.OUTPUT_FILE
    renderer.render(analyzed, config, output_path)

    # 4. Open
    if not args.no_open:
        webbrowser.open(f"file://{output_path.resolve()}")
        print(f"[open] Opened in browser: {output_path}")

    print("\n✓ Done!")


if __name__ == "__main__":
    main()
