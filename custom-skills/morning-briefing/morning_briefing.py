#!/usr/bin/env python3
"""Morning briefing — personalized daily digest from all tracked data."""
import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta, date

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")

MORNING_VERSES = [
    ("Lamentations 3:22-23", "The steadfast love of the LORD never ceases; his mercies never come to an end; they are new every morning; great is your faithfulness."),
    ("Psalm 118:24", "This is the day the LORD has made; let us rejoice and be glad in it."),
    ("Psalm 5:3", "In the morning, LORD, you hear my voice; in the morning I lay my requests before you and wait expectantly."),
    ("Isaiah 40:31", "But those who hope in the LORD will renew their strength. They will soar on wings like eagles."),
    ("Philippians 4:13", "I can do all things through Christ who strengthens me."),
    ("Proverbs 3:5-6", "Trust in the LORD with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight."),
    ("Matthew 6:34", "Therefore do not worry about tomorrow, for tomorrow will worry about itself. Each day has enough trouble of its own."),
    ("Romans 8:28", "And we know that in all things God works for the good of those who love him."),
    ("Jeremiah 29:11", "For I know the plans I have for you, declares the LORD, plans to prosper you and not to harm you, plans to give you hope and a future."),
    ("2 Corinthians 12:9", "My grace is sufficient for you, for my power is made perfect in weakness."),
]

# Liturgical data (simplified — imported inline to keep skill self-contained)
FEASTS = {
    (1, 1): "Mary, Mother of God", (3, 19): "St. Joseph",
    (3, 25): "Annunciation", (8, 15): "Assumption of Mary",
    (8, 28): "St. Augustine", (9, 29): "Archangels Michael, Gabriel, Raphael",
    (10, 1): "St. Therese of Lisieux", (10, 4): "St. Francis of Assisi",
    (11, 1): "All Saints", (12, 8): "Immaculate Conception",
    (12, 25): "Christmas",
}


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from safe_json import load_json as _safe_load


def load_json(filename):
    return _safe_load(os.path.join(DATA_DIR, filename))


def generate_briefing(user_id):
    today = datetime.now()
    print(f"Good Morning! Here's your daily briefing")
    print(f"{today.strftime('%A, %B %d, %Y')}")
    print("=" * 40)

    # 1. Recovery streak
    recovery = load_json("recovery_tracker.json").get(user_id, {})
    if recovery:
        start = datetime.fromisoformat(recovery.get("streak_start", today.isoformat()))
        streak = (today - start).days
        resisted = len(recovery.get("resisted_triggers", []))
        print(f"\nRecovery: Day {streak}")
        if streak > 0:
            print(f"  Keep going! {resisted} triggers resisted total.")
    else:
        print(f"\nRecovery: Start tracking with 'recovery status'")

    # 2. Mood trend (last 3 days)
    mood = load_json("mood_tracker.json").get(user_id, {})
    if mood and mood.get("entries"):
        cutoff = (today - timedelta(days=3)).strftime("%Y-%m-%d")
        recent = [e for e in mood["entries"] if e.get("date", "") >= cutoff]
        if recent:
            ratings = [e["rating"] for e in recent]
            avg = sum(ratings) / len(ratings)
            trend = "up" if len(ratings) >= 2 and ratings[-1] > ratings[0] else \
                    "down" if len(ratings) >= 2 and ratings[-1] < ratings[0] else "steady"
            print(f"\nMood: {avg:.1f}/10 (trending {trend})")

    # 3. Due flashcards
    cards = load_json("flashcards.json").get(user_id, {})
    if cards and cards.get("cards"):
        now = today.isoformat()
        due = len([c for c in cards["cards"] if c.get("due", "") <= now])
        if due > 0:
            print(f"\nFlashcards: {due} cards due for review")

    # 4. Liturgical info
    key = (today.month, today.day)
    if key in FEASTS:
        print(f"\nFeast Day: {FEASTS[key]}")

    month = today.month
    if (month == 12 and today.day >= 1) or (month == 1 and today.day <= 6):
        season = "Advent/Christmas"
    elif 2 <= month <= 3:
        season = "Lent"
    elif month == 4 and today.day <= 20:
        season = "Holy Week/Easter"
    elif 4 <= month <= 5:
        season = "Easter"
    else:
        season = "Ordinary Time"
    print(f"  Season: {season}")

    # 5. Bible verse
    ref, text = random.choice(MORNING_VERSES)
    print(f"\nVerse of the Day ({ref}):")
    print(f'  "{text}"')

    # 6. Active location reminders
    locations = load_json("location_reminders.json")
    active_lists = []
    for key, val in locations.items():
        if key.startswith(f"{user_id}:"):
            pending = [x["name"] for x in val.get("items", []) if not x.get("completed")]
            if pending:
                active_lists.append(f"{val['location']}: {', '.join(pending[:3])}")
    if active_lists:
        print(f"\nReminders:")
        for l in active_lists[:3]:
            print(f"  - {l}")

    print(f"\n{'=' * 40}")
    print("Have a blessed day!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    args = parser.parse_args()
    generate_briefing(args.user)


if __name__ == "__main__":
    main()
