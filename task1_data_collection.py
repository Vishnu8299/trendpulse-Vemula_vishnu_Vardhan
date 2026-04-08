import requests
import json
import os
import time
from datetime import datetime
TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL        = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

HEADERS          = {"User-Agent": "TrendPulse/1.0"}
MAX_IDS          = 500   
MAX_PER_CATEGORY = 25    
MAX_RETRIES      = 3     
RETRY_DELAY      = 2    

CACHE_FILE = os.path.join("data", "_cache.json")


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

def assign_category(title):
    lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in lower:
                return category
    return None



def fetch_url(session, url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as err:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)   
            else:
                short_err = str(err)[:120]
                print(f"  [WARNING] Gave up on {url.split('/')[-1]}  → {short_err}")
                return None



def load_cache():
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
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_dict, f, ensure_ascii=False)



print("=" * 55)
print("  TrendPulse – Task 1: HackerNews Data Collection")
print("=" * 55)
print()


print(f"[Step 1] Fetching top {MAX_IDS} story IDs …")

session = requests.Session()
session.headers.update(HEADERS)

ids_data = fetch_url(session, TOP_STORIES_URL)
if ids_data is None:
    print("[ERROR] Cannot reach HackerNews API. Check internet connection.")
    raise SystemExit(1)

all_ids = ids_data[:MAX_IDS]
print(f"         Got {len(all_ids)} story IDs.\n")


print("[Step 2] Fetching story details …")
cache = load_cache()   

fetched_new = 0
for story_id in all_ids:
    key = str(story_id)
    if key in cache:
        continue

    url   = ITEM_URL.format(id=story_id)
    story = fetch_url(session, url)

    if story and "title" in story:
        cache[key] = story
        fetched_new += 1

        if fetched_new % 50 == 0:
            save_cache(cache)
            print(f"  … {len(cache)} stories cached so far")

save_cache(cache)

valid_stories = [s for s in cache.values() if "title" in s]
print(f"  Total valid stories available: {len(valid_stories)}\n")


print("[Step 2b] Assigning categories …")
print(f"          (up to {MAX_PER_CATEGORY} stories per category)\n")

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

        record = {
            "post_id":      story.get("id"),
            "title":        title,
            "category":     category,
            "score":        story.get("score", 0),
            "num_comments": story.get("descendants", 0),
            "author":       story.get("by", "unknown"),
            "collected_at": collected_at,
        }
        buckets[category].append(record)

    n = len(buckets[category])
    bar = "█" * n
    print(f"     {n:>2} stories  {bar}")

        if idx < len(category_names) - 1:
        print("     Sleeping 2 s …")
        time.sleep(2)


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


print(f"\nCollected {len(final_stories)} stories. Saved to {output_path}")
print()
print("Breakdown by category:")
for cat, stories in buckets.items():
    bar = "█" * len(stories)
    print(f"  {cat:<15} {len(stories):>3} stories  {bar}")

print("\nDone! ✓")
