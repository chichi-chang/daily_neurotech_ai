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
import subprocess
import sys
import tempfile
import shutil
import webbrowser
import pathlib

import config
import fetchers
import llm
import renderer


def deploy_to_gh_pages(html_path: pathlib.Path):
    """Push digest.html to the gh-pages branch for GitHub Pages hosting."""
    repo_root = pathlib.Path(__file__).parent

    remote_url = subprocess.check_output(
        ["git", "remote", "get-url", "origin"], cwd=repo_root, text=True
    ).strip()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        subprocess.run(["git", "init", "-b", "gh-pages"], cwd=tmp, check=True,
                       capture_output=True)

        shutil.copy(html_path, tmp / "index.html")

        subprocess.run(["git", "add", "index.html"], cwd=tmp, check=True,
                       capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Update digest"],
            cwd=tmp, check=True, capture_output=True,
        )
        subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=tmp,
                       check=True, capture_output=True)
        subprocess.run(["git", "push", "--force", "origin", "gh-pages"], cwd=tmp,
                       check=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser(description="Neurotech daily digest generator")
    parser.add_argument("--no-open",    action="store_true", help="Don't open browser")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch, skip LLM")
    parser.add_argument("--deploy",     action="store_true",
                        help="Push digest to GitHub Pages after generating")
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

    # 4. Deploy to GitHub Pages
    if args.deploy:
        print("[deploy] Pushing digest to GitHub Pages...")
        try:
            deploy_to_gh_pages(output_path)
            print("[deploy] Live at https://chichi-chang.github.io/daily_neurotech_ai/")
        except subprocess.CalledProcessError as e:
            print(f"[deploy] Failed: {e}")
            if e.stderr:
                print(f"         {e.stderr.strip()}")

    # 5. Open
    if not args.no_open:
        webbrowser.open(f"file://{output_path.resolve()}")
        print(f"[open] Opened in browser: {output_path}")

    print("\n✓ Done!")


if __name__ == "__main__":
    main()
