#!/usr/bin/env python3
"""Spaced repetition flashcard system using SM-2 algorithm."""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
DATA_FILE = os.path.join(DATA_DIR, "flashcards.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def sm2(quality, repetitions, easiness, interval):
    """SM-2 algorithm: calculate next review interval."""
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * easiness)
        repetitions += 1

    easiness = max(1.3, easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return repetitions, easiness, interval


def add_card(user_id, front, back, track="general"):
    data = load_data()
    if user_id not in data:
        data[user_id] = {"cards": []}

    card_id = str(uuid.uuid4())[:8]
    card = {
        "id": card_id,
        "front": front,
        "back": back,
        "track": track,
        "created": datetime.now().isoformat(),
        "due": datetime.now().isoformat(),
        "repetitions": 0,
        "easiness": 2.5,
        "interval": 0,
    }
    data[user_id]["cards"].append(card)
    save_data(data)
    print(f"Card added [{track}]: {front[:50]}")
    print(f"  ID: {card_id}")
    total = len(data[user_id]["cards"])
    print(f"  Total cards: {total}")


def get_quiz(user_id):
    data = load_data()
    if user_id not in data or not data[user_id]["cards"]:
        print("No flashcards yet. Add some with: add --front 'question' --back 'answer'")
        return

    now = datetime.now().isoformat()
    due = [c for c in data[user_id]["cards"] if c["due"] <= now]

    if not due:
        next_due = min(data[user_id]["cards"], key=lambda c: c["due"])
        due_dt = datetime.fromisoformat(next_due["due"])
        diff = due_dt - datetime.now()
        if diff.total_seconds() < 3600:
            print(f"No cards due now. Next card in {int(diff.total_seconds()/60)} minutes.")
        else:
            print(f"No cards due now. Next card due: {due_dt.strftime('%b %d %H:%M')}")
        return

    card = due[0]
    print(f"QUESTION [{card['track']}]:")
    print(f"  {card['front']}")
    print(f"  (Card ID: {card['id']})")
    print(f"  ({len(due)} cards due)")


def answer_card(user_id, card_id, quality):
    data = load_data()
    if user_id not in data:
        print("No cards found")
        return

    quality = max(1, min(5, quality))
    for card in data[user_id]["cards"]:
        if card["id"] == card_id:
            reps, ease, interval = sm2(
                quality, card["repetitions"], card["easiness"], card["interval"]
            )
            card["repetitions"] = reps
            card["easiness"] = ease
            card["interval"] = interval
            card["due"] = (datetime.now() + timedelta(days=interval)).isoformat()
            card["last_reviewed"] = datetime.now().isoformat()

            save_data(data)
            print(f"ANSWER: {card['back']}")
            print(f"  Quality: {quality}/5")
            if interval == 1:
                print(f"  Next review: tomorrow")
            else:
                print(f"  Next review: in {interval} days")
            return

    print(f"Card {card_id} not found")


def show_stats(user_id):
    data = load_data()
    if user_id not in data or not data[user_id]["cards"]:
        print("No flashcards yet")
        return

    cards = data[user_id]["cards"]
    now = datetime.now().isoformat()
    due = len([c for c in cards if c["due"] <= now])
    tracks = {}
    for c in cards:
        t = c.get("track", "general")
        tracks[t] = tracks.get(t, 0) + 1

    mature = len([c for c in cards if c["interval"] >= 21])
    learning = len([c for c in cards if 0 < c["interval"] < 21])
    new = len([c for c in cards if c["repetitions"] == 0])

    print(f"Flashcard Stats:")
    print(f"  Total cards: {len(cards)}")
    print(f"  Due now: {due}")
    print(f"  New: {new} | Learning: {learning} | Mature: {mature}")
    print(f"  Tracks: {', '.join(f'{k}({v})' for k, v in tracks.items())}")


def show_due(user_id):
    data = load_data()
    if user_id not in data or not data[user_id]["cards"]:
        print("No flashcards yet")
        return

    now = datetime.now().isoformat()
    due = [c for c in data[user_id]["cards"] if c["due"] <= now]
    print(f"Cards due: {len(due)}")
    for c in due[:5]:
        print(f"  [{c['track']}] {c['front'][:50]}")
    if len(due) > 5:
        print(f"  ...and {len(due)-5} more")


def main():
    parser = argparse.ArgumentParser(description="Spaced repetition")
    parser.add_argument("action", choices=["add", "quiz", "answer", "stats", "due"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--front", default="")
    parser.add_argument("--back", default="")
    parser.add_argument("--track", default="general")
    parser.add_argument("--card-id", default="")
    parser.add_argument("--quality", type=int, default=3)
    args = parser.parse_args()

    if args.action == "add":
        if not args.front or not args.back:
            print("Error: --front and --back required")
            sys.exit(1)
        add_card(args.user, args.front, args.back, args.track)
    elif args.action == "quiz":
        get_quiz(args.user)
    elif args.action == "answer":
        if not args.card_id:
            print("Error: --card-id required")
            sys.exit(1)
        answer_card(args.user, args.card_id, args.quality)
    elif args.action == "stats":
        show_stats(args.user)
    elif args.action == "due":
        show_due(args.user)


if __name__ == "__main__":
    main()
