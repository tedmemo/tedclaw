#!/usr/bin/env python3
"""Wellness check-in and mood tracker for TedClaw."""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
DATA_FILE = os.path.join(DATA_DIR, "mood_tracker.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_mood(user_id, rating, note=""):
    data = load_data()
    if user_id not in data:
        data[user_id] = {"entries": []}

    entry = {
        "rating": max(1, min(10, rating)),
        "note": note,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    data[user_id]["entries"].append(entry)
    save_data(data)

    emoji = "😊" if rating >= 7 else "😐" if rating >= 4 else "😔"
    print(f"{emoji} Mood logged: {rating}/10")
    if note:
        print(f"   Note: {note}")

    # Check streak
    entries = data[user_id]["entries"]
    dates = sorted(set(e["date"] for e in entries), reverse=True)
    streak = 1
    for i in range(1, len(dates)):
        d1 = datetime.strptime(dates[i - 1], "%Y-%m-%d")
        d2 = datetime.strptime(dates[i], "%Y-%m-%d")
        if (d1 - d2).days == 1:
            streak += 1
        else:
            break
    if streak >= 3:
        print(f"   🔥 {streak}-day streak!")


def show_history(user_id, days=7):
    data = load_data()
    if user_id not in data or not data[user_id]["entries"]:
        print("No mood entries yet")
        return

    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    entries = [e for e in data[user_id]["entries"] if e["timestamp"] >= cutoff]

    if not entries:
        print(f"No entries in the last {days} days")
        return

    print(f"Mood history (last {days} days):")
    for e in entries[-10:]:
        dt = datetime.fromisoformat(e["timestamp"]).strftime("%b %d %H:%M")
        emoji = "😊" if e["rating"] >= 7 else "😐" if e["rating"] >= 4 else "😔"
        note = f" — {e['note']}" if e.get("note") else ""
        print(f"  {dt}: {emoji} {e['rating']}/10{note}")


def show_summary(user_id, period="week"):
    data = load_data()
    if user_id not in data or not data[user_id]["entries"]:
        print("No mood entries yet")
        return

    days = 7 if period == "week" else 30
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    entries = [e for e in data[user_id]["entries"] if e["timestamp"] >= cutoff]

    if not entries:
        print(f"No entries in the last {period}")
        return

    ratings = [e["rating"] for e in entries]
    avg = sum(ratings) / len(ratings)
    high = max(ratings)
    low = min(ratings)
    trend = "improving" if len(ratings) >= 3 and ratings[-1] > ratings[0] else \
            "declining" if len(ratings) >= 3 and ratings[-1] < ratings[0] else "stable"

    print(f"{'Weekly' if period == 'week' else 'Monthly'} Summary:")
    print(f"  Entries: {len(entries)}")
    print(f"  Average: {avg:.1f}/10")
    print(f"  Range: {low}-{high}")
    print(f"  Trend: {trend}")

    # Find dates with entries
    dates = sorted(set(e["date"] for e in data[user_id]["entries"]), reverse=True)
    streak = 1
    for i in range(1, len(dates)):
        d1 = datetime.strptime(dates[i - 1], "%Y-%m-%d")
        d2 = datetime.strptime(dates[i], "%Y-%m-%d")
        if (d1 - d2).days == 1:
            streak += 1
        else:
            break
    print(f"  Current streak: {streak} days")


def show_streak(user_id):
    data = load_data()
    if user_id not in data or not data[user_id]["entries"]:
        print("No mood entries yet. Start tracking to build a streak!")
        return

    dates = sorted(set(e["date"] for e in data[user_id]["entries"]), reverse=True)
    streak = 1
    for i in range(1, len(dates)):
        d1 = datetime.strptime(dates[i - 1], "%Y-%m-%d")
        d2 = datetime.strptime(dates[i], "%Y-%m-%d")
        if (d1 - d2).days == 1:
            streak += 1
        else:
            break

    total = len(data[user_id]["entries"])
    print(f"🔥 Current streak: {streak} days")
    print(f"📊 Total entries: {total}")
    if streak >= 7:
        print("💪 Amazing consistency!")
    elif streak >= 3:
        print("👍 Keep it up!")


def main():
    parser = argparse.ArgumentParser(description="Mood tracker")
    parser.add_argument("action", choices=["log", "history", "summary", "streak"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--rating", type=int, default=5)
    parser.add_argument("--note", default="")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--period", choices=["week", "month"], default="week")
    args = parser.parse_args()

    if args.action == "log":
        log_mood(args.user, args.rating, args.note)
    elif args.action == "history":
        show_history(args.user, args.days)
    elif args.action == "summary":
        show_summary(args.user, args.period)
    elif args.action == "streak":
        show_streak(args.user)


if __name__ == "__main__":
    main()
