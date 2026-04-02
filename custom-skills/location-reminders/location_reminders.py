#!/usr/bin/env python3
"""Location-based reminder manager for TedClaw."""
import argparse
import json
import os
import sys
from datetime import datetime

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
DATA_FILE = os.path.join(DATA_DIR, "location_reminders.json")

# Location aliases
ALIASES = {
    "supermarket": "store", "grocery": "store", "groceries": "store",
    "chemist": "pharmacy", "drugstore": "pharmacy",
    "gym": "gym", "fitness": "gym",
    "kids house": "kids house", "kid's house": "kids house",
}


def normalize_location(loc):
    loc = loc.strip().lower()
    return ALIASES.get(loc, loc)


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_items(user_id, location, items_str):
    data = load_data()
    key = f"{user_id}:{normalize_location(location)}"
    if key not in data:
        data[key] = {"location": normalize_location(location), "items": [], "user": user_id}

    items = [i.strip() for i in items_str.split(",") if i.strip()]
    added = []
    for item in items:
        existing = [x["name"] for x in data[key]["items"] if not x.get("completed")]
        if item.lower() not in [e.lower() for e in existing]:
            data[key]["items"].append({
                "name": item, "added_at": datetime.now().isoformat(), "completed": False
            })
            added.append(item)

    save_data(data)
    loc = normalize_location(location)
    if added:
        print(f"Added to {loc}: {', '.join(added)}")
    else:
        print(f"All items already in {loc} list")


def query_location(user_id, location):
    data = load_data()
    key = f"{user_id}:{normalize_location(location)}"
    if key not in data:
        print(f"No items for {normalize_location(location)}")
        return

    pending = [x["name"] for x in data[key]["items"] if not x.get("completed")]
    loc = normalize_location(location)
    if pending:
        print(f"{loc} ({len(pending)} items): {', '.join(pending)}")
    else:
        print(f"No pending items for {loc}")


def complete_items(user_id, location, items_str):
    data = load_data()
    key = f"{user_id}:{normalize_location(location)}"
    if key not in data:
        print(f"No list found for {normalize_location(location)}")
        return

    items = [i.strip().lower() for i in items_str.split(",") if i.strip()]
    completed = []
    for entry in data[key]["items"]:
        if entry["name"].lower() in items and not entry.get("completed"):
            entry["completed"] = True
            entry["completed_at"] = datetime.now().isoformat()
            completed.append(entry["name"])

    save_data(data)
    if completed:
        print(f"Completed: {', '.join(completed)}")
    else:
        print("No matching items found")


def clear_location(user_id, location):
    data = load_data()
    key = f"{user_id}:{normalize_location(location)}"
    if key in data:
        count = len([x for x in data[key]["items"] if not x.get("completed")])
        del data[key]
        save_data(data)
        print(f"Cleared {count} items from {normalize_location(location)}")
    else:
        print(f"No list for {normalize_location(location)}")


def list_all(user_id):
    data = load_data()
    locations = []
    for key, val in data.items():
        if key.startswith(f"{user_id}:"):
            pending = [x["name"] for x in val["items"] if not x.get("completed")]
            if pending:
                locations.append(f"  {val['location']}: {', '.join(pending)}")

    if locations:
        print(f"Your location lists:\n" + "\n".join(locations))
    else:
        print("No active location lists")


def main():
    parser = argparse.ArgumentParser(description="Location reminders")
    parser.add_argument("action", choices=["add", "query", "complete", "clear", "list"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--location", default="")
    parser.add_argument("--items", default="")
    args = parser.parse_args()

    if args.action == "add":
        if not args.location or not args.items:
            print("Error: --location and --items required for add")
            sys.exit(1)
        add_items(args.user, args.location, args.items)
    elif args.action == "query":
        if not args.location:
            print("Error: --location required for query")
            sys.exit(1)
        query_location(args.user, args.location)
    elif args.action == "complete":
        if not args.location or not args.items:
            print("Error: --location and --items required for complete")
            sys.exit(1)
        complete_items(args.user, args.location, args.items)
    elif args.action == "clear":
        if not args.location:
            print("Error: --location required for clear")
            sys.exit(1)
        clear_location(args.user, args.location)
    elif args.action == "list":
        list_all(args.user)


if __name__ == "__main__":
    main()
