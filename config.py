# ============================================================
#  THE DAILY SIGNAL — CONFIG
#  Edit this file to switch data sources, add API keys, etc.
#  API keys are loaded from a local .env file (never uploaded to GitHub).
# ============================================================
import os
from pathlib import Path

def _load_env():
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip("\"'")
        os.environ.setdefault(key.strip(), value)

_load_env()

# ----- DATA SOURCE -----
# Options: "rss" | "hn" | "rss+hn" | "google" | "bing"
# "rss+hn" is recommended — free, broad coverage, no API keys needed
SOURCE = "rss"

# ----- LLM BACKEND -----
# Options: "ollama" | "claude" | "openai"
LLM_BACKEND = "claude"
OLLAMA_MODEL = "llama3.2"
OLLAMA_BASE_URL = "http://localhost:11434"

# Claude API (~$0.30/month at Haiku prices)
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")  # set via env var or paste here for local use
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"

# ----- GOOGLE CUSTOM SEARCH -----
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID", "")
GOOGLE_QUERIES = [
    "neurotech news",
    "brain-computer interface",
    "neural implant FDA approval",
    "neurotechnology investment funding",
    "Neuralink news",
]
GOOGLE_RESULTS_PER_QUERY = 5


# ----- RSS FEEDS -----
RSS_FEEDS = [
    # Neurotech specific
    "https://www.neurotechreports.com/pages/feed.html",
    "https://neurotechx.com/feed/",

    # Tech / med-tech
    "https://techcrunch.com/category/biotech-health/feed/",  # biotech-specific, not all of TC
    "https://www.technologyreview.com/feed/",
    "https://spectrum.ieee.org/feeds/topic/biomedical.rss",
    "https://www.medtechdive.com/feeds/news/",
    "https://www.fiercebiotech.com/rss/xml",
    "https://www.statnews.com/feed/",

    # Research
    "https://www.nature.com/subjects/neuroscience.rss",
    "https://www.sciencedaily.com/rss/mind_brain.xml",
    "https://www.sciencedaily.com/rss/matter_energy/medical_technology.xml",

    # VC / industry
    "https://www.biopharmadive.com/feeds/news/",
    "https://www.mobihealthnews.com/rss.xml",

]

# AI-specific feeds — these skip keyword filtering since they're already AI-curated
RSS_FEEDS_NO_KEYWORD_FILTER = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
]

# How many days back to look (1 = last 24h, 7 = past week)
RSS_DAYS_BACK = 7

# ----- HACKER NEWS -----
# Searched via free Algolia API — no key needed
HN_QUERIES = [
    "neurotech",
    "brain computer interface",
    "BCI",
    "neuralink",
    "neural implant",
    "neurostimulation",
    "deep brain stimulation",
    "merge labs",
    "precision neuroscience",
]

# ----- RSS KEYWORD FILTER -----
RSS_KEYWORDS = [
    # Core neurotech
    "neuro", "brain", "neural", "bci", "implant", "electrode",
    "cognit", "neurostim", "eeg", "emg", "ecog",
    "brain-computer", "brain computer",
    "tms", "tdcs", "tacs", "neurostimulation",
    "ultrasound bci", "focused ultrasound",

    # US companies
    "neuralink", "synchron", "paradromics",
    "blackrock neuro", "medtronic brain",
    "precision neuroscience", "merge labs",
    "forest neurotech", "stentrode",
    "neurosity", "emotiv", "openwater",

    # Chinese companies (increasingly newsworthy)
    "neuroxess", "brainco", "neuracle",
    "gestala", "stairmed", "neuralmatrix",
    "brainland", "zhiran medical",

    # Clinical/device terms
    "deep brain", "vagus nerve",
    "spinal cord stimulation",
    "neuroprosthetic", "neuroprosthesis",
    "closed-loop", "neurofeedback",
    "cochlear", "retinal implant",
    "dbs",

    # Regulatory signals
    "510k", "510(k)",
    "breakthrough device",
    "neural interface",

    # Neurological conditions
    "dementia", "alzheimer", "parkinson",
    "epilep", "seizure", "neuropath",
    "stroke rehabilitation", "paralys",

    # Imaging / sensing
    "fmri", "meg", "fnirs",
    "brain scan", "brain imag",
    "connectome",

    # Emerging / research-to-industry
    "neuromorphic", "optogenet",
    "brain organoid", "neural data",
    "human augmentation", "neuroethics",

    # Broader neuro
    "cortex", "cortical", "cerebr",
    "hippocam", "synap", "neuron",

    # Neuro-AI intersection
    "neuro-ai", "neuro ai", "neural ai", "brain ai",
    "ai neuroscience", "ai brain", "ai neural",
    "computational neuroscience", "neural network brain",
    "ai diagnosis", "ai neurolog", "ai psychiatr",
    "ai drug discovery neuro", "digital twin brain",

    # AI tools & models (short keywords like "ai" use word-boundary matching)
    "ai", "ai tool", "ai agent", "llm", "large language model",
    "gpt", "claude", "gemini", "openai", "anthropic",
    "copilot", "chatbot", "generative ai", "gen ai",
    "ai startup", "ai launch", "ai release",
    "machine learning", "deep learning",
    "transformer", "diffusion model",
    "text-to", "image gen", "ai coding",
    "ai productiv", "ai workflow", "ai automat",
]

# ----- OUTPUT -----
OUTPUT_FILE = "digest.html"
MAX_ARTICLES_IN_DIGEST = 60
