"""
llm.py — Send articles to LLM for relevance filtering + categorization.
Switch backend via config.py — no code changes needed.
"""

import json
import sys

SYSTEM_PROMPT = """You are a tech industry analyst covering three beats:
1. Neurotechnology — BCIs, neural implants, neuromodulation, brain imaging, neurostimulation, etc.
2. Neuro-AI — AI applied to neuroscience, computational neuroscience, AI-powered brain diagnostics,
   neural-inspired AI, brain-computer interface ML, AI drug discovery for neurological conditions, etc.
3. AI tools — new AI products, model releases, AI startups, developer tools, and notable AI industry news.

Your job is to review article headlines and summaries, filter for relevance to any of these beats, 
and categorize them. Especially prioritize articles at the intersection of neuroscience and AI."""

USER_PROMPT_TEMPLATE = """Review these articles and return a JSON array of the ones that are 
relevant to ANY of these three areas:

1. **Neurotechnology**: brain-computer interfaces, neural implants, neuromodulation, 
   cognitive enhancement tech, brain imaging advances, neurostimulation devices, etc.
2. **Neuro-AI**: AI applied to neuroscience, computational neuroscience, AI-powered brain 
   diagnostics, neural-inspired AI architectures, ML for brain data, AI drug discovery for 
   neurological conditions, digital brain twins, etc. PRIORITIZE these.
3. **AI Tools & Products**: new AI tools, model launches, AI startup news, developer AI tools,
   notable AI product updates, AI coding tools, generative AI releases, etc.

For each relevant article, assign ONE category:
- "approval" — FDA or regulatory approvals/clearances (neurotech)
- "funding" — investments, rounds, acquisitions
- "research" — scientific breakthroughs
- "neuro_ai" — AI + neuroscience intersection
- "product" — new products, launches, company milestones
- "ai_tool" — new AI tools, model releases, AI products
- "policy" — policy, ethics, legal developments
- "other" — notable news that doesn't fit above

Return ONLY valid JSON — an array of objects with these fields:
  title, url, source, category, one_line_summary

Articles to review:
{articles}"""


def analyze(articles, config):
    if not articles:
        print("[llm] No articles to analyze.")
        return []

    backend = config.LLM_BACKEND
    print(f"[llm] Analyzing {len(articles)} articles with backend: {backend}")

    prompt = USER_PROMPT_TEMPLATE.format(
        articles=json.dumps([
            {"title": a["title"], "summary": a["summary"], "url": a["url"], "source": a["source"]}
            for a in articles
        ], indent=2)
    )

    if backend == "ollama":
        raw = _call_ollama(prompt, config)
    elif backend == "claude":
        raw = _call_claude(prompt, config)
    elif backend == "openai":
        raw = _call_openai(prompt, config)
    else:
        sys.exit(f"Unknown LLM_BACKEND '{backend}' in config.py")

    return _parse_response(raw)


# ── OLLAMA ────────────────────────────────────────────────────────────────────

def _call_ollama(prompt, config):
    try:
        import requests
    except ImportError:
        sys.exit("requests not installed. Run: pip install requests")

    try:
        resp = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": config.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "format": "json",
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        sys.exit(
            "Cannot connect to Ollama. Make sure it's running:\n"
            "  1. Install: https://ollama.com\n"
            f"  2. Pull model: ollama pull {config.OLLAMA_MODEL}\n"
            "  3. It should auto-start, or run: ollama serve"
        )


# ── CLAUDE ────────────────────────────────────────────────────────────────────

def _call_claude(prompt, config):
    try:
        import anthropic
    except ImportError:
        sys.exit("anthropic not installed. Run: pip install anthropic")

    if not config.CLAUDE_API_KEY:
        sys.exit("Set CLAUDE_API_KEY in config.py")

    client = anthropic.Anthropic(api_key=config.CLAUDE_API_KEY)
    msg = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── OPENAI ────────────────────────────────────────────────────────────────────

def _call_openai(prompt, config):
    try:
        import openai
    except ImportError:
        sys.exit("openai not installed. Run: pip install openai")

    if not config.OPENAI_API_KEY:
        sys.exit("Set OPENAI_API_KEY in config.py")

    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        max_tokens=4096,
    )
    return resp.choices[0].message.content


# ── PARSE ─────────────────────────────────────────────────────────────────────

def _parse_response(raw):
    import re
    text = raw.strip()
    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    m = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Fix invalid \uXXXX escapes and other common LLM quirks
        text = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\\\u', text)
        try:
            data = json.loads(text, strict=False)
        except Exception as e:
            print(f"[llm] Failed to parse JSON response: {e}")
            print(f"[llm] Raw response:\n{raw[:500]}")
            return []

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                return v
    return []
