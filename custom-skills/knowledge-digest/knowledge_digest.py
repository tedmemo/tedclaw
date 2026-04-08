#!/usr/bin/env python3
"""Knowledge digest — periodic summary of captured URLs and bookmarks."""
import argparse
import os
import sys
from datetime import datetime, timedelta
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from safe_json import load_json

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
CAPTURE_FILE = os.path.join(DATA_DIR, "social_captures.json")


def daily_digest(user_id):
    data = load_json(CAPTURE_FILE)
    if user_id not in data or not data[user_id]["items"]:
        print("No captured items yet. Share a URL to start building your knowledge warehouse!")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    items = [i for i in data[user_id]["items"] if i.get("date", "") == today]
    total = len(data[user_id]["items"])

    if not items:
        print(f"No new captures today. Total warehouse: {total} items.")
        return

    print(f"Today's Knowledge Capture ({len(items)} new)")
    print("=" * 40)

    by_platform = Counter(i["platform"] for i in items)
    by_tag = Counter()
    for i in items:
        for t in i.get("tags", []):
            by_tag[t] += 1

    for item in items:
        tags = " ".join(f"#{t}" for t in item.get("tags", []))
        note = f" — {item['note']}" if item.get("note") else ""
        print(f"  [{item['platform']}] {item['title'][:50]}{note}")
        print(f"    {tags}")

    print(f"\nPlatforms: {', '.join(f'{p}({c})' for p, c in by_platform.most_common())}")
    print(f"Topics: {', '.join(f'#{t}({c})' for t, c in by_tag.most_common(5))}")
    print(f"Total warehouse: {total} items")


def weekly_digest(user_id):
    data = load_json(CAPTURE_FILE)
    if user_id not in data or not data[user_id]["items"]:
        print("No captured items yet.")
        return

    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    items = [i for i in data[user_id]["items"] if i.get("date", "") >= week_start]
    total = len(data[user_id]["items"])

    if not items:
        print(f"No new captures this week. Total warehouse: {total} items.")
        return

    print(f"Weekly Knowledge Digest ({len(items)} new items)")
    print(f"Period: {week_start} to {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 40)

    # By topic
    by_tag = Counter()
    for i in items:
        for t in i.get("tags", []):
            by_tag[t] += 1

    # Topic growth (compare to total)
    all_tags = Counter()
    for i in data[user_id]["items"]:
        for t in i.get("tags", []):
            all_tags[t] += 1

    print("\nTopic breakdown:")
    for tag, week_count in by_tag.most_common(10):
        total_count = all_tags.get(tag, 0)
        growth = f" — growing fast!" if week_count >= 3 else ""
        print(f"  #{tag}: {week_count} new (total: {total_count}){growth}")

    # By platform
    by_platform = Counter(i["platform"] for i in items)
    print(f"\nBy source: {', '.join(f'{p}({c})' for p, c in by_platform.most_common())}")

    # By day
    by_day = Counter(i.get("date", "") for i in items)
    most_active = by_day.most_common(1)[0] if by_day else ("", 0)
    print(f"Most active day: {most_active[0]} ({most_active[1]} items)")

    # Suggestions
    print(f"\nTotal warehouse: {total} items")
    untagged = sum(1 for i in data[user_id]["items"] if "untagged" in i.get("tags", []))
    if untagged > 0:
        print(f"  {untagged} items are untagged — want me to auto-tag them?")

    # Stale items (saved 30+ days ago, no note)
    stale_cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    stale = sum(1 for i in data[user_id]["items"]
                if i.get("date", "") <= stale_cutoff and not i.get("note"))
    if stale > 5:
        print(f"  {stale} items from 30+ days ago with no notes — archive or review?")


def show_topics(user_id):
    data = load_json(CAPTURE_FILE)
    if user_id not in data or not data[user_id]["items"]:
        print("No captured items yet.")
        return

    all_tags = Counter()
    for i in data[user_id]["items"]:
        for t in i.get("tags", []):
            all_tags[t] += 1

    print(f"Knowledge Topics ({len(all_tags)} topics, {len(data[user_id]['items'])} total items)")
    print("=" * 40)
    for tag, count in all_tags.most_common():
        bar = "#" * min(count, 20)
        print(f"  #{tag:15s} {count:3d} {bar}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["daily", "weekly", "topics"])
    parser.add_argument("--user", required=True)
    args = parser.parse_args()

    if args.action == "daily":
        daily_digest(args.user)
    elif args.action == "weekly":
        weekly_digest(args.user)
    elif args.action == "topics":
        show_topics(args.user)


if __name__ == "__main__":
    main()
