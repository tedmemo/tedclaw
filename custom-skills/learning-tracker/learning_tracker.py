#!/usr/bin/env python3
"""TedOS learning tracker — IT/Health/Wealth pillars."""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
DATA_FILE = os.path.join(DATA_DIR, "learning_tracker.json")

TRACKS = {"it": "IT", "health": "Health", "wealth": "Wealth"}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_entry(user_id, track, entry, url="", minutes=0):
    if track not in TRACKS:
        print(f"Error: track must be one of: {', '.join(TRACKS.keys())}")
        sys.exit(1)

    data = load_data()
    if user_id not in data:
        data[user_id] = {"entries": []}

    record = {
        "track": track,
        "entry": entry,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
    }
    if url:
        record["url"] = url
    if minutes:
        record["minutes"] = minutes

    data[user_id]["entries"].append(record)
    save_data(data)

    label = TRACKS[track]
    print(f"📚 Logged [{label}]: {entry}")
    if minutes:
        print(f"   ⏱ {minutes} min")

    # Count this week
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    week_entries = [e for e in data[user_id]["entries"] if e["date"] >= week_start]
    tracks_this_week = set(e["track"] for e in week_entries)
    print(f"   This week: {len(week_entries)} entries across {len(tracks_this_week)}/3 tracks")
    if len(tracks_this_week) == 3:
        print("   🌟 All 3 tracks covered this week!")


def show_status(user_id):
    data = load_data()
    if user_id not in data or not data[user_id]["entries"]:
        print("No learning entries yet. Start with: log --track it --entry 'what you learned'")
        return

    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    week_entries = [e for e in data[user_id]["entries"] if e["date"] >= week_start]

    print("📊 This Week's Learning:")
    for key, label in TRACKS.items():
        track_entries = [e for e in week_entries if e["track"] == key]
        total_min = sum(e.get("minutes", 0) for e in track_entries)
        status = f"{len(track_entries)} entries" + (f", {total_min} min" if total_min else "")
        icon = "✅" if track_entries else "⬜"
        print(f"  {icon} {label}: {status}")
        for e in track_entries[-3:]:
            print(f"     - {e['entry'][:60]}")

    total = len(data[user_id]["entries"])
    print(f"\n📈 Total entries (all time): {total}")


def show_history(user_id, track, days=30):
    data = load_data()
    if user_id not in data or not data[user_id]["entries"]:
        print("No learning entries yet")
        return

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    entries = [e for e in data[user_id]["entries"]
               if e["track"] == track and e["date"] >= cutoff]

    if not entries:
        print(f"No {TRACKS.get(track, track)} entries in the last {days} days")
        return

    label = TRACKS.get(track, track)
    print(f"📚 {label} History (last {days} days):")
    for e in entries:
        dt = datetime.fromisoformat(e["timestamp"]).strftime("%b %d")
        mins = f" ({e['minutes']} min)" if e.get("minutes") else ""
        url = f" — {e['url']}" if e.get("url") else ""
        print(f"  {dt}: {e['entry'][:70]}{mins}{url}")


def show_digest(user_id):
    data = load_data()
    if user_id not in data or not data[user_id]["entries"]:
        print("No learning entries yet")
        return

    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    week_entries = [e for e in data[user_id]["entries"] if e["date"] >= week_start]

    if not week_entries:
        print("No entries this week yet")
        return

    total_min = sum(e.get("minutes", 0) for e in week_entries)
    print("📋 Weekly Learning Digest")
    print(f"   Period: {week_start} to {datetime.now().strftime('%Y-%m-%d')}")
    print(f"   Total entries: {len(week_entries)}")
    if total_min:
        print(f"   Total time: {total_min} min")
    print()

    for key, label in TRACKS.items():
        track_entries = [e for e in week_entries if e["track"] == key]
        if track_entries:
            print(f"  {label}:")
            for e in track_entries:
                print(f"    - {e['entry'][:70]}")
            print()

    missing = [TRACKS[k] for k in TRACKS if k not in set(e["track"] for e in week_entries)]
    if missing:
        print(f"  💡 Missing tracks: {', '.join(missing)}")


def main():
    parser = argparse.ArgumentParser(description="Learning tracker")
    parser.add_argument("action", choices=["log", "status", "history", "digest"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--track", choices=list(TRACKS.keys()), default="it")
    parser.add_argument("--entry", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--minutes", type=int, default=0)
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()

    if args.action == "log":
        if not args.entry:
            print("Error: --entry required for log")
            sys.exit(1)
        log_entry(args.user, args.track, args.entry, args.url, args.minutes)
    elif args.action == "status":
        show_status(args.user)
    elif args.action == "history":
        show_history(args.user, args.track, args.days)
    elif args.action == "digest":
        show_digest(args.user)


if __name__ == "__main__":
    main()
