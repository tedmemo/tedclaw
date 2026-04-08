#!/usr/bin/env python3
"""Universal social capture — save URLs from any platform with auto-tagging."""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from collections import Counter
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from safe_json import load_json, save_json

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
DATA_FILE = os.path.join(DATA_DIR, "social_captures.json")

# Platform detection patterns
PLATFORM_PATTERNS = {
    "youtube": [r"youtube\.com/watch", r"youtu\.be/", r"youtube\.com/shorts"],
    "tiktok": [r"tiktok\.com/", r"vm\.tiktok\.com/"],
    "twitter": [r"twitter\.com/", r"x\.com/"],
    "facebook": [r"facebook\.com/", r"fb\.com/", r"fb\.watch/"],
    "linkedin": [r"linkedin\.com/"],
    "instagram": [r"instagram\.com/", r"instagr\.am/"],
    "pinterest": [r"pinterest\.com/", r"pin\.it/"],
    "reddit": [r"reddit\.com/", r"redd\.it/"],
    "github": [r"github\.com/"],
}

# Auto-tag keywords
TAG_KEYWORDS = {
    "cooking": ["recipe", "cook", "food", "kitchen", "meal", "ingredient", "chef"],
    "fitness": ["workout", "exercise", "gym", "fitness", "health", "muscle", "cardio"],
    "tech": ["programming", "code", "developer", "software", "api", "react", "python"],
    "faith": ["catholic", "prayer", "bible", "church", "saint", "gospel", "mass"],
    "finance": ["money", "invest", "budget", "savings", "crypto", "stock", "finance"],
    "parenting": ["kids", "children", "parenting", "family", "baby", "school"],
    "learning": ["tutorial", "course", "learn", "study", "education", "guide"],
    "vietnamese": ["vietnamese", "vietnam", "pho", "banh mi", "tieng viet"],
}


def detect_platform(url):
    """Detect which platform a URL belongs to."""
    url_lower = url.lower()
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url_lower):
                return platform
    return "website"


def auto_tag(title, note, url):
    """Generate tags from title, note, and URL."""
    text = f"{title} {note} {url}".lower()
    tags = set()

    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.add(tag)

    # Add platform as tag
    platform = detect_platform(url)
    if platform != "website":
        tags.add(platform)

    return sorted(tags) if tags else ["untagged"]


def extract_title_from_url(url):
    """Extract a readable title from URL when no metadata available."""
    parsed = urlparse(url)
    path = parsed.path.strip("/").split("/")

    platform = detect_platform(url)
    domain = parsed.netloc.replace("www.", "")

    if platform == "youtube":
        return f"YouTube video from {domain}"
    elif platform == "reddit":
        if len(path) >= 4:
            return f"Reddit: r/{path[1]} — {path[3].replace('_', ' ').replace('-', ' ')}"
    elif platform == "github":
        if len(path) >= 2:
            return f"GitHub: {path[0]}/{path[1]}"

    # Generic: use last path segment
    if path and path[-1]:
        title = path[-1].replace("-", " ").replace("_", " ")
        return f"{title} ({domain})"

    return domain


def save_url(user_id, url, note=""):
    """Save a URL with auto-detected metadata."""
    data = load_json(DATA_FILE)
    if user_id not in data:
        data[user_id] = {"items": []}

    # Check duplicate
    existing_urls = [item["url"] for item in data[user_id]["items"]]
    if url in existing_urls:
        print(f"Already saved: {url}")
        return

    platform = detect_platform(url)
    title = extract_title_from_url(url)
    tags = auto_tag(title, note, url)

    item = {
        "url": url,
        "platform": platform,
        "title": title,
        "note": note,
        "tags": tags,
        "saved_at": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    data[user_id]["items"].append(item)
    save_json(DATA_FILE, data)

    total = len(data[user_id]["items"])
    tag_str = ", ".join(f"#{t}" for t in tags)

    # Count items with same primary tag
    primary_tag = tags[0] if tags else "untagged"
    tag_count = sum(1 for i in data[user_id]["items"] if primary_tag in i.get("tags", []))

    print(f"Saved! [{platform}] {title}")
    if note:
        print(f"  Note: {note}")
    print(f"  Tags: {tag_str}")
    print(f"  You now have {tag_count} items about {primary_tag} ({total} total)")


def show_recent(user_id, count=10):
    """Show recently saved items."""
    data = load_json(DATA_FILE)
    if user_id not in data or not data[user_id]["items"]:
        print("No saved items yet. Share a URL to start capturing!")
        return

    items = data[user_id]["items"][-count:]
    items.reverse()

    print(f"Recent saves ({len(items)}):")
    for item in items:
        dt = datetime.fromisoformat(item["saved_at"]).strftime("%b %d")
        tags = " ".join(f"#{t}" for t in item.get("tags", []))
        note = f" — {item['note']}" if item.get("note") else ""
        print(f"  [{dt}] [{item['platform']}] {item['title'][:50]}{note}")
        print(f"    {tags} | {item['url'][:60]}")


def show_stats(user_id):
    """Show knowledge warehouse stats."""
    data = load_json(DATA_FILE)
    if user_id not in data or not data[user_id]["items"]:
        print("No saved items yet.")
        return

    items = data[user_id]["items"]
    total = len(items)

    # By platform
    platforms = Counter(i["platform"] for i in items)
    # By tag
    all_tags = Counter()
    for i in items:
        for t in i.get("tags", []):
            all_tags[t] += 1

    # This week
    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    this_week = sum(1 for i in items if i.get("date", "") >= week_start)

    print(f"Knowledge Warehouse Stats:")
    print(f"  Total items: {total}")
    print(f"  This week: {this_week}")

    print(f"\n  By platform:")
    for p, c in platforms.most_common():
        print(f"    {p}: {c}")

    print(f"\n  By topic:")
    for t, c in all_tags.most_common(10):
        print(f"    #{t}: {c}")


def search_items(user_id, query):
    """Search saved items by keyword."""
    data = load_json(DATA_FILE)
    if user_id not in data or not data[user_id]["items"]:
        print("No saved items to search.")
        return

    query_lower = query.lower()
    results = []
    for item in data[user_id]["items"]:
        searchable = f"{item.get('title', '')} {item.get('note', '')} {' '.join(item.get('tags', []))} {item.get('url', '')}".lower()
        if query_lower in searchable:
            results.append(item)

    if not results:
        print(f"No items matching '{query}'")
        return

    print(f"Found {len(results)} items matching '{query}':")
    for item in results[-5:]:
        tags = " ".join(f"#{t}" for t in item.get("tags", []))
        print(f"  [{item['platform']}] {item['title'][:50]}")
        print(f"    {tags} | {item['url'][:60]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["save", "recent", "stats", "search"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--url", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--query", default="")
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    if args.action == "save":
        if not args.url:
            print("Error: --url required")
            sys.exit(1)
        save_url(args.user, args.url, args.note)
    elif args.action == "recent":
        show_recent(args.user, args.count)
    elif args.action == "stats":
        show_stats(args.user)
    elif args.action == "search":
        if not args.query:
            print("Error: --query required")
            sys.exit(1)
        search_items(args.user, args.query)


if __name__ == "__main__":
    main()
