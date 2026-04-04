#!/usr/bin/env python3
"""Gratitude journal with daily entries and weekly review."""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
DATA_FILE = os.path.join(DATA_DIR, "gratitude_journal.json")


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from safe_json import load_json, save_json


def load_data():
    return load_json(DATA_FILE)


def save_data(data):
    save_json(DATA_FILE, data)


def add_entries(user_id, entries_str):
    data = load_data()
    if user_id not in data:
        data[user_id] = {"entries": []}

    items = [e.strip() for e in entries_str.split(",") if e.strip()]
    today = datetime.now().strftime("%Y-%m-%d")

    for item in items:
        data[user_id]["entries"].append({
            "text": item,
            "date": today,
            "timestamp": datetime.now().isoformat(),
        })

    save_data(data)
    print(f"Grateful for {len(items)} things today:")
    for item in items:
        print(f"  - {item}")

    today_total = len([e for e in data[user_id]["entries"] if e["date"] == today])
    print(f"  Total today: {today_total}")


def show_today(user_id):
    data = load_data()
    if user_id not in data:
        print("No gratitude entries yet. Start with what you're thankful for today.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    entries = [e for e in data[user_id]["entries"] if e["date"] == today]

    if not entries:
        print("No entries today yet. What are you grateful for?")
        return

    print(f"Today's gratitude ({len(entries)} entries):")
    for e in entries:
        print(f"  - {e['text']}")


def show_week(user_id):
    data = load_data()
    if user_id not in data or not data[user_id]["entries"]:
        print("No gratitude entries yet.")
        return

    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    entries = [e for e in data[user_id]["entries"] if e["date"] >= week_start]

    if not entries:
        print("No entries this week.")
        return

    print(f"This week's gratitude ({len(entries)} entries):")
    by_date = {}
    for e in entries:
        by_date.setdefault(e["date"], []).append(e["text"])

    for date in sorted(by_date.keys()):
        dt = datetime.strptime(date, "%Y-%m-%d").strftime("%A %b %d")
        print(f"\n  {dt}:")
        for text in by_date[date]:
            print(f"    - {text}")


def show_stats(user_id):
    data = load_data()
    if user_id not in data or not data[user_id]["entries"]:
        print("No gratitude entries yet.")
        return

    entries = data[user_id]["entries"]
    dates = sorted(set(e["date"] for e in entries))
    total = len(entries)

    # Streak
    streak = 0
    check = datetime.now().strftime("%Y-%m-%d")
    for i in range(len(dates)):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if d in dates:
            streak += 1
        else:
            break

    print(f"Gratitude Stats:")
    print(f"  Total entries: {total}")
    print(f"  Days journaled: {len(dates)}")
    print(f"  Current streak: {streak} days")
    print(f"  Average per day: {total / max(len(dates), 1):.1f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["add", "today", "week", "stats"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--entries", default="")
    args = parser.parse_args()

    if args.action == "add":
        if not args.entries:
            print("Error: --entries required")
        else:
            add_entries(args.user, args.entries)
    elif args.action == "today":
        show_today(args.user)
    elif args.action == "week":
        show_week(args.user)
    elif args.action == "stats":
        show_stats(args.user)


if __name__ == "__main__":
    main()
