#!/usr/bin/env python3
"""Weekly reflection report aggregating all tracked data."""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")

FILES = {
    "mood": os.path.join(DATA_DIR, "mood_tracker.json"),
    "recovery": os.path.join(DATA_DIR, "recovery_tracker.json"),
    "learning": os.path.join(DATA_DIR, "learning_tracker.json"),
    "gratitude": os.path.join(DATA_DIR, "gratitude_journal.json"),
}


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from safe_json import load_json as _safe_load


def load(key):
    return _safe_load(FILES.get(key, ""))


def week_range():
    now = datetime.now()
    start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    return start, end


def generate_report(user_id):
    start, end = week_range()
    print(f"Weekly Reflection Report")
    print(f"Period: {start} to {end}")
    print("=" * 40)

    # Recovery
    recovery = load("recovery").get(user_id, {})
    if recovery:
        streak_start = datetime.fromisoformat(recovery.get("streak_start", datetime.now().isoformat()))
        streak = (datetime.now() - streak_start).days
        relapses_week = [r for r in recovery.get("relapses", []) if r.get("date", "") >= start]
        resisted_week = [r for r in recovery.get("resisted_triggers", []) if r.get("date", "") >= start]
        print(f"\nRecovery:")
        print(f"  Current streak: {streak} days")
        print(f"  Relapses this week: {len(relapses_week)}")
        print(f"  Triggers resisted: {len(resisted_week)}")
        if resisted_week:
            print(f"  Victories!")
        longest = recovery.get("longest_streak", 0)
        if streak > longest:
            print(f"  NEW RECORD STREAK!")

    # Mood
    mood_data = load("mood").get(user_id, {})
    if mood_data:
        entries = [e for e in mood_data.get("entries", []) if e.get("date", "") >= start]
        if entries:
            ratings = [e["rating"] for e in entries]
            avg = sum(ratings) / len(ratings)
            trend = "improving" if len(ratings) >= 3 and ratings[-1] > ratings[0] else \
                    "declining" if len(ratings) >= 3 and ratings[-1] < ratings[0] else "stable"
            emoji = "up" if trend == "improving" else "down" if trend == "declining" else "steady"
            print(f"\nMood:")
            print(f"  Entries: {len(entries)}")
            print(f"  Average: {avg:.1f}/10")
            print(f"  Trend: {trend} ({emoji})")
            print(f"  Range: {min(ratings)}-{max(ratings)}")

    # Learning
    learn_data = load("learning").get(user_id, {})
    if learn_data:
        entries = [e for e in learn_data.get("entries", []) if e.get("date", "") >= start]
        if entries:
            tracks = {}
            for e in entries:
                t = e.get("track", "general")
                tracks[t] = tracks.get(t, 0) + 1
            total_min = sum(e.get("minutes", 0) for e in entries)
            print(f"\nLearning:")
            print(f"  Entries: {len(entries)}")
            for t, c in tracks.items():
                print(f"    {t.upper()}: {c} entries")
            if total_min:
                print(f"  Total time: {total_min} min")
            covered = len(tracks)
            print(f"  Tracks covered: {covered}/3")

    # Gratitude
    grat_data = load("gratitude").get(user_id, {})
    if grat_data:
        entries = [e for e in grat_data.get("entries", []) if e.get("date", "") >= start]
        if entries:
            print(f"\nGratitude:")
            print(f"  Entries: {len(entries)}")
            # Show a few highlights
            for e in entries[:3]:
                print(f"    - {e['text'][:60]}")
            if len(entries) > 3:
                print(f"    ...and {len(entries)-3} more")

    # Summary
    print(f"\n{'=' * 40}")
    print(f"Summary:")
    has_data = any([recovery, mood_data, learn_data, grat_data])
    if not has_data:
        print("  No data tracked this week yet. Start by logging your mood or recovery status!")
    else:
        print("  Keep going! Every day you show up is a victory.")


def show_trends(user_id, weeks=4):
    print(f"Trends (last {weeks} weeks)")
    print("=" * 40)

    mood_data = load("mood").get(user_id, {})
    if mood_data and mood_data.get("entries"):
        print("\nMood by week:")
        for w in range(weeks - 1, -1, -1):
            w_start = (datetime.now() - timedelta(weeks=w, days=datetime.now().weekday())).strftime("%Y-%m-%d")
            w_end = (datetime.now() - timedelta(weeks=w - 1, days=datetime.now().weekday())).strftime("%Y-%m-%d") if w > 0 else datetime.now().strftime("%Y-%m-%d")
            entries = [e for e in mood_data["entries"] if w_start <= e.get("date", "") <= w_end]
            if entries:
                avg = sum(e["rating"] for e in entries) / len(entries)
                bar = "#" * int(avg)
                print(f"  {w_start}: {avg:.1f}/10 {bar}")
            else:
                print(f"  {w_start}: no data")

    recovery = load("recovery").get(user_id, {})
    if recovery and recovery.get("relapses"):
        print("\nRelapses by week:")
        for w in range(weeks - 1, -1, -1):
            w_start = (datetime.now() - timedelta(weeks=w, days=datetime.now().weekday())).isoformat()
            w_end = (datetime.now() - timedelta(weeks=w - 1, days=datetime.now().weekday())).isoformat() if w > 0 else datetime.now().isoformat()
            count = len([r for r in recovery["relapses"] if w_start <= r.get("date", "") <= w_end])
            print(f"  Week -{w}: {count} relapses")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["report", "trends"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--weeks", type=int, default=4)
    args = parser.parse_args()

    if args.action == "report":
        generate_report(args.user)
    elif args.action == "trends":
        show_trends(args.user, args.weeks)


if __name__ == "__main__":
    main()
