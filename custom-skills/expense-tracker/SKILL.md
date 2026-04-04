---
name: expense-tracker
description: "Use this skill to track daily expenses, view spending summaries, and manage budgets. Handles 'spent $45 at Coles', 'how much did I spend today', 'weekly spending', 'spending by category'. Simple expense logging via chat."
user_invocable: true
---

# Expense Tracker

Simple expense logging and spending analysis via chat.

## Usage

```bash
python3 expense_tracker.py <action> --user <user_id> [options]
```

### Actions

**add** — Log an expense
```bash
python3 expense_tracker.py add --user ted --amount 45.50 --category groceries --note "Coles weekly shop"
```

**today** — Show today's spending
```bash
python3 expense_tracker.py today --user ted
```

**week** — Show this week's spending by category
```bash
python3 expense_tracker.py week --user ted
```

**month** — Show this month's spending summary
```bash
python3 expense_tracker.py month --user ted
```

### Categories
groceries, food, transport, bills, kids, health, entertainment, clothing, household, other

## Agent Behavior
When user says "spent $X at Y":
1. Parse amount and merchant/note
2. Auto-categorize (Coles/Woolworths → groceries, petrol → transport, etc.)
3. Log with `add` action
4. Show daily running total
