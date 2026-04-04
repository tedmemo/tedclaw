#!/usr/bin/env python3
"""Simple expense tracker with category analysis."""
import argparse
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
DATA_FILE = os.path.join(DATA_DIR, "expenses.json")

CATEGORIES = ["groceries", "food", "transport", "bills", "kids", "health",
              "entertainment", "clothing", "household", "other"]

# Auto-categorization hints
AUTO_CAT = {
    "coles": "groceries", "woolworths": "groceries", "aldi": "groceries",
    "woolies": "groceries", "iga": "groceries",
    "mcdonald": "food", "kfc": "food", "subway": "food", "uber eats": "food",
    "doordash": "food", "menulog": "food", "cafe": "food", "restaurant": "food",
    "petrol": "transport", "shell": "transport", "bp": "transport",
    "7eleven": "transport", "myki": "transport", "opal": "transport",
    "uber": "transport", "taxi": "transport",
    "pharmacy": "health", "chemist": "health", "doctor": "health",
    "dentist": "health", "gym": "health",
    "netflix": "entertainment", "spotify": "entertainment", "cinema": "entertainment",
    "kmart": "household", "bunnings": "household", "ikea": "household",
    "big w": "kids", "target": "kids", "toy": "kids",
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


def auto_categorize(note):
    note_lower = note.lower()
    for keyword, cat in AUTO_CAT.items():
        if keyword in note_lower:
            return cat
    return "other"


def add_expense(user_id, amount, category, note):
    data = load_data()
    if user_id not in data:
        data[user_id] = {"expenses": []}

    if not category or category not in CATEGORIES:
        category = auto_categorize(note)

    data[user_id]["expenses"].append({
        "amount": round(amount, 2),
        "category": category,
        "note": note,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
    })
    save_data(data)

    # Today's total
    today = datetime.now().strftime("%Y-%m-%d")
    today_total = sum(e["amount"] for e in data[user_id]["expenses"] if e["date"] == today)

    print(f"Logged: ${amount:.2f} [{category}]")
    if note:
        print(f"  Note: {note}")
    print(f"  Today's total: ${today_total:.2f}")


def show_today(user_id):
    data = load_data()
    if user_id not in data:
        print("No expenses logged yet.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    expenses = [e for e in data[user_id]["expenses"] if e["date"] == today]

    if not expenses:
        print("No expenses today.")
        return

    total = sum(e["amount"] for e in expenses)
    print(f"Today's expenses: ${total:.2f}")
    for e in expenses:
        note = f" — {e['note']}" if e.get("note") else ""
        print(f"  ${e['amount']:.2f} [{e['category']}]{note}")


def show_week(user_id):
    data = load_data()
    if user_id not in data:
        print("No expenses logged yet.")
        return

    start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    expenses = [e for e in data[user_id]["expenses"] if e["date"] >= start]

    if not expenses:
        print("No expenses this week.")
        return

    total = sum(e["amount"] for e in expenses)
    by_cat = defaultdict(float)
    for e in expenses:
        by_cat[e["category"]] += e["amount"]

    print(f"This week: ${total:.2f} ({len(expenses)} expenses)")
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = (amt / total * 100) if total > 0 else 0
        print(f"  {cat}: ${amt:.2f} ({pct:.0f}%)")


def show_month(user_id):
    data = load_data()
    if user_id not in data:
        print("No expenses logged yet.")
        return

    month_start = datetime.now().strftime("%Y-%m-01")
    expenses = [e for e in data[user_id]["expenses"] if e["date"] >= month_start]

    if not expenses:
        print("No expenses this month.")
        return

    total = sum(e["amount"] for e in expenses)
    by_cat = defaultdict(float)
    for e in expenses:
        by_cat[e["category"]] += e["amount"]

    days_in = datetime.now().day
    daily_avg = total / days_in if days_in > 0 else 0
    projected = daily_avg * 30

    print(f"This month: ${total:.2f} ({len(expenses)} expenses)")
    print(f"  Daily average: ${daily_avg:.2f}")
    print(f"  Projected monthly: ${projected:.2f}")
    print(f"\n  By category:")
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"    {cat}: ${amt:.2f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["add", "today", "week", "month"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--amount", type=float, default=0)
    parser.add_argument("--category", default="")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    if args.action == "add":
        if args.amount <= 0:
            print("Error: --amount required (positive number)")
        else:
            add_expense(args.user, args.amount, args.category, args.note)
    elif args.action == "today":
        show_today(args.user)
    elif args.action == "week":
        show_week(args.user)
    elif args.action == "month":
        show_month(args.user)


if __name__ == "__main__":
    main()
