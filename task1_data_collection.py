"""
TrendPulse - Task 1: Fetch Data from HackerNews API
====================================================
Author : Vishnu Vardhan Vemula
Date   : 2026-04-07

What this script does:
  1. Hits the HackerNews public API to get the top 500 story IDs.
  2. Fetches each story's details (title, score, comments, author …).
  3. Assigns a category to every story based on keywords in its title.
  4. Keeps up to 25 stories per category (5 categories → 125 max).
  5. Saves everything as a nicely formatted JSON file inside data/.

No API key needed — HackerNews is completely open!

Network note:
  - Uses a persistent requests.Session for connection reuse (faster).
  - Caches raw story data in data/_cache.json so any story fetched
    successfully is never lost, even if the script is interrupted.
  - Retries each failed request up to MAX_RETRIES times.
"""

import requests          # HTTP calls
import json              # JSON read/write
import os                # folder creation
import time              # sleep between categories
from datetime import datetime  # timestamp for each record

# ──────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL        = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

HEADERS          = {"User-Agent": "TrendPulse/1.0"}
MAX_IDS          = 500   # how many top story IDs to consider
MAX_PER_CATEGORY = 25    # cap per category (125 total max)
MAX_RETRIES      = 3     # retry attempts per failed request
RETRY_DELAY      = 2     # seconds to wait between retries

# Local cache so partial runs are never wasted
CACHE_FILE = os.path.join("data", "_cache.json")

# ──────────────────────────────────────────────
#  CATEGORY KEYWORD TABLE  (case-insensitive)
# ──────────────────────────────────────────────

CATEGORIES = {
    "technology":    [
        "ai", "software", "tech", "code", "computer", "data", "cloud",
        "api", "gpu", "llm", "python", "github", "linux", "open source",
        "programming", "developer", "startup", "robot", "model",
        "security", "hack", "chip", "hardware", "framework", "database",
    ],
    "worldnews":     [
        "war", "government", "country", "president", "election",
        "climate", "attack", "global", "ukraine", "russia", "china",
        "policy", "military", "sanctions", "treaty", "trade",
        "inflation", "economy", "europe", "india", "nuclear", "crisis",
    ],
    "sports":        [
        "nfl", "nba", "fifa", "sport", "team", "player", "league",
        "championship", "olympic", "tennis", "golf", "soccer", "cricket",
        "tournament", "athlete", "coach", "stadium", "win", "match",
        "score", "season",
    ],
    "science":       [
        "research", "study", "space", "physics", "biology", "discovery",
        "nasa", "genome", "ocean", "planet", "vaccine", "dna",
        "experiment", "telescope", "chemistry", "fossil", "neuroscience",
        "quantum", "asteroid", "species", "drug", "medicine", "gene",
    ],
    "entertainment": [
        "movie", "film", "music", "netflix", "book", "show", "award",
        "streaming", "oscar", "grammy", "spotify", "disney", "youtube",
        "podcast", "album", "concert", "celebrity", "tv", "series",
        "anime", "game", "video game",
    ],
}


# ──────────────────────────────────────────────
#  HELPER: assign a category from a title
# ──────────────────────────────────────────────

def assign_category(title):
    """
    Scan the title (lowercased) for each category's keywords.
    Returns the first matching category name, or None.
    """
    lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in lower:
                return category
    return None


# ──────────────────────────────────────────────
#  HELPER: fetch a URL with retries
# ──────────────────────────────────────────────

def fetch_url(session, url):
    """
    Try GET url up to MAX_RETRIES times using the shared session.
    Waits RETRY_DELAY seconds between attempts.
    Returns parsed JSON dict/list, or None on complete failure.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as err:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)   # brief pause before retry
            else:
                # All retries exhausted – print short warning and give up
                short_err = str(err)[:120]
                print(f"  [WARNING] Gave up on {url.split('/')[-1]}  → {short_err}")
                return None


# ──────────────────────────────────────────────
#  CACHE helpers  (survive interrupted runs)
# ──────────────────────────────────────────────

def load_cache():
    """Load previously fetched raw stories from disk (dict keyed by ID)."""
    os.makedirs("data", exist_ok=True)
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            print(f"  Loaded {len(data)} stories from local cache.")
            return data
        except Exception:
            pass
    return {}


def save_cache(cache_dict):
    """Persist the raw story cache to disk."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_dict, f, ensure_ascii=False)


# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════

print("=" * 55)
print("  TrendPulse – Task 1: HackerNews Data Collection")
print("=" * 55)
print()

# ── Step 1: get top story IDs ──────────────────

print(f"[Step 1] Fetching top {MAX_IDS} story IDs …")

# A persistent session reuses the underlying TCP connection (faster)
session = requests.Session()
session.headers.update(HEADERS)

ids_data = fetch_url(session, TOP_STORIES_URL)
if ids_data is None:
    print("[ERROR] Cannot reach HackerNews API. Check internet connection.")
    raise SystemExit(1)

all_ids = ids_data[:MAX_IDS]
print(f"         Got {len(all_ids)} story IDs.\n")

# ── Step 2: fetch story details (with cache) ───

print("[Step 2] Fetching story details …")
cache = load_cache()   # {str(id): story_dict}

fetched_new = 0
for story_id in all_ids:
    key = str(story_id)
    if key in cache:
        continue   # already have this one

    url   = ITEM_URL.format(id=story_id)
    story = fetch_url(session, url)

    if story and "title" in story:
        cache[key] = story
        fetched_new += 1

        # Save cache every 50 new stories so progress isn't lost
        if fetched_new % 50 == 0:
            save_cache(cache)
            print(f"  … {len(cache)} stories cached so far")

# Final cache save
save_cache(cache)

valid_stories = [s for s in cache.values() if "title" in s]
print(f"  Total valid stories available: {len(valid_stories)}\n")

# ── Step 3: assign categories ──────────────────

print("[Step 2b] Assigning categories …")
print(f"          (up to {MAX_PER_CATEGORY} stories per category)\n")

# Sort by score (highest first) so each bucket gets the best stories
valid_stories.sort(key=lambda s: s.get("score", 0), reverse=True)

collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
buckets      = {cat: [] for cat in CATEGORIES}

category_names = list(CATEGORIES.keys())
for idx, category in enumerate(category_names):

    print(f"  → Assigning: {category.upper()}")

    for story in valid_stories:
        if len(buckets[category]) >= MAX_PER_CATEGORY:
            break

        title = story.get("title", "")
        if assign_category(title) != category:
            continue

        # Build the 7-field record required by the task spec
        record = {
            "post_id":      story.get("id"),             # unique HN story ID
            "title":        title,                        # story headline
            "category":     category,                     # our assigned label
            "score":        story.get("score", 0),        # upvote count
            "num_comments": story.get("descendants", 0),  # comment count
            "author":       story.get("by", "unknown"),   # HN username
            "collected_at": collected_at,                 # timestamp
        }
        buckets[category].append(record)

    n = len(buckets[category])
    bar = "█" * n
    print(f"     {n:>2} stories  {bar}")

    # Mandatory 2-second pause between categories (task requirement)
    if idx < len(category_names) - 1:
        print("     Sleeping 2 s …")
        time.sleep(2)

# ── Step 4: save to JSON ───────────────────────

print()
print("[Step 3] Saving to JSON …")

final_stories = []
for cat_stories in buckets.values():
    final_stories.extend(cat_stories)

os.makedirs("data", exist_ok=True)
today_str   = datetime.now().strftime("%Y%m%d")
output_path = os.path.join("data", f"trends_{today_str}.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_stories, f, indent=2, ensure_ascii=False)

# ── Final summary ──────────────────────────────

print(f"\nCollected {len(final_stories)} stories. Saved to {output_path}")
print()
print("Breakdown by category:")
for cat, stories in buckets.items():
    bar = "█" * len(stories)
    print(f"  {cat:<15} {len(stories):>3} stories  {bar}")

print("\nDone! ✓")
