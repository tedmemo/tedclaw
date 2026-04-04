#!/usr/bin/env python3
"""Addiction recovery streak tracker with trigger analysis."""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from collections import Counter

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
DATA_FILE = os.path.join(DATA_DIR, "recovery_tracker.json")

MILESTONES = [1, 7, 14, 30, 60, 90, 180, 365]
MILESTONE_LABELS = {
    1: "First Step", 7: "One Week", 14: "Two Weeks",
    30: "One Month", 60: "Two Months", 90: "Three Months",
    180: "Six Months", 365: "One Year"
}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_user(data, user_id):
    if user_id not in data:
        data[user_id] = {
            "streak_start": datetime.now().isoformat(),
            "current_streak": 0,
            "longest_streak": 0,
            "total_clean_days": 0,
            "relapses": [],
            "resisted_triggers": [],
            "milestones_celebrated": [],
        }
    return data[user_id]


def calc_streak(user):
    start = datetime.fromisoformat(user["streak_start"])
    days = (datetime.now() - start).days
    return max(0, days)


def show_status(user_id):
    data = load_data()
    user = get_user(data, user_id)
    streak = calc_streak(user)

    # Check for new milestones
    new_milestones = []
    for m in MILESTONES:
        if streak >= m and m not in user.get("milestones_celebrated", []):
            new_milestones.append(m)
            user.setdefault("milestones_celebrated", []).append(m)

    if new_milestones:
        save_data(data)

    print(f"Recovery Status:")
    print(f"  Current streak: {streak} days")
    print(f"  Longest streak: {max(streak, user.get('longest_streak', 0))} days")
    print(f"  Total relapses: {len(user.get('relapses', []))}")
    print(f"  Triggers resisted: {len(user.get('resisted_triggers', []))}")

    if new_milestones:
        for m in new_milestones:
            print(f"  NEW MILESTONE: {MILESTONE_LABELS.get(m, f'Day {m}')}!")

    # Next milestone
    for m in MILESTONES:
        if streak < m:
            days_to = m - streak
            print(f"  Next milestone: {MILESTONE_LABELS.get(m, f'Day {m}')} in {days_to} days")
            break


def log_relapse(user_id, trigger="", note=""):
    data = load_data()
    user = get_user(data, user_id)
    streak = calc_streak(user)

    # Save the broken streak
    if streak > user.get("longest_streak", 0):
        user["longest_streak"] = streak
    user["total_clean_days"] = user.get("total_clean_days", 0) + streak

    user["relapses"].append({
        "date": datetime.now().isoformat(),
        "streak_broken": streak,
        "trigger": trigger,
        "note": note,
        "day_of_week": datetime.now().strftime("%A"),
        "hour": datetime.now().hour,
    })

    # Reset streak
    user["streak_start"] = datetime.now().isoformat()
    user["milestones_celebrated"] = []
    save_data(data)

    print(f"Relapse logged. Previous streak: {streak} days.")
    if trigger:
        print(f"  Trigger: {trigger}")
    if note:
        print(f"  Note: {note}")
    print(f"  Streak reset to Day 0. You can start again right now.")
    print(f"  Total clean days (lifetime): {user['total_clean_days']}")


def log_resisted(user_id, trigger="", note=""):
    data = load_data()
    user = get_user(data, user_id)

    user["resisted_triggers"].append({
        "date": datetime.now().isoformat(),
        "trigger": trigger,
        "note": note,
        "streak_day": calc_streak(user),
    })
    save_data(data)

    total = len(user["resisted_triggers"])
    print(f"VICTORY! Trigger resisted. You're stronger than the urge.")
    if trigger:
        print(f"  Trigger: {trigger}")
    print(f"  Total triggers resisted: {total}")
    print(f"  Current streak: Day {calc_streak(user)}")


def show_milestones(user_id):
    data = load_data()
    user = get_user(data, user_id)
    streak = calc_streak(user)

    print("Recovery Milestones:")
    for m in MILESTONES:
        if streak >= m:
            print(f"  [ACHIEVED] Day {m}: {MILESTONE_LABELS.get(m, '')}")
        else:
            days_to = m - streak
            print(f"  [ ] Day {m}: {MILESTONE_LABELS.get(m, '')} ({days_to} days away)")


def show_patterns(user_id):
    data = load_data()
    user = get_user(data, user_id)
    relapses = user.get("relapses", [])

    if len(relapses) < 2:
        print("Need at least 2 relapses to identify patterns. Keep going!")
        return

    # Trigger frequency
    triggers = Counter(r.get("trigger", "unknown") for r in relapses if r.get("trigger"))
    days = Counter(r.get("day_of_week", "") for r in relapses if r.get("day_of_week"))
    hours = [r.get("hour", 0) for r in relapses if "hour" in r]

    print("Trigger Pattern Analysis:")
    print(f"  Total relapses analyzed: {len(relapses)}")

    if triggers:
        print(f"\n  Top triggers:")
        for t, count in triggers.most_common(5):
            print(f"    {t}: {count} times")

    if days:
        print(f"\n  Highest risk days:")
        for d, count in days.most_common(3):
            print(f"    {d}: {count} relapses")

    if hours:
        avg_hour = sum(hours) // len(hours)
        late_night = sum(1 for h in hours if h >= 21 or h <= 5)
        print(f"\n  Time patterns:")
        print(f"    Average relapse hour: {avg_hour}:00")
        print(f"    Late night (9PM-5AM): {late_night}/{len(hours)} ({late_night*100//len(hours)}%)")

    # Resisted triggers
    resisted = user.get("resisted_triggers", [])
    if resisted:
        print(f"\n  Victories: {len(resisted)} triggers resisted!")


def show_history(user_id, days=90):
    data = load_data()
    user = get_user(data, user_id)
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    relapses = [r for r in user.get("relapses", []) if r["date"] >= cutoff]
    resisted = [r for r in user.get("resisted_triggers", []) if r["date"] >= cutoff]
    streak = calc_streak(user)

    print(f"Recovery History (last {days} days):")
    print(f"  Current streak: {streak} days")
    print(f"  Relapses: {len(relapses)}")
    print(f"  Triggers resisted: {len(resisted)}")

    if relapses:
        print(f"\n  Recent relapses:")
        for r in relapses[-5:]:
            dt = datetime.fromisoformat(r["date"]).strftime("%b %d")
            t = r.get("trigger", "")
            s = r.get("streak_broken", 0)
            print(f"    {dt}: streak={s}d, trigger={t}")


def main():
    parser = argparse.ArgumentParser(description="Recovery tracker")
    parser.add_argument("action", choices=["status", "relapse", "trigger", "milestones", "patterns", "history"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--trigger", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--days", type=int, default=90)
    args = parser.parse_args()

    if args.action == "status":
        show_status(args.user)
    elif args.action == "relapse":
        log_relapse(args.user, args.trigger, args.note)
    elif args.action == "trigger":
        log_resisted(args.user, args.trigger, args.note)
    elif args.action == "milestones":
        show_milestones(args.user)
    elif args.action == "patterns":
        show_patterns(args.user)
    elif args.action == "history":
        show_history(args.user, args.days)


if __name__ == "__main__":
    main()
