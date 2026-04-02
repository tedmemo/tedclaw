---
name: location-reminders
description: "Use this skill when the user wants to save items to buy or tasks to do at a specific location. Handles 'remind me to buy X at the store', 'what do I need at the pharmacy', 'add Y to my grocery list', 'going to the store, anything I need?', 'done with store list'. Manages per-location shopping/task lists with add, query, complete, and clear actions."
user_invocable: true
---

# Location Reminders

Manage location-based shopping lists and task reminders. Items are saved per-location and can be queried when the user is heading somewhere.

## Usage

Run the Python script with an action and arguments:

```bash
python3 location_reminders.py <action> --user <user_id> [options]
```

### Actions

**add** — Add items to a location list
```bash
python3 location_reminders.py add --user ted --location store --items "milk, eggs, bread"
```

**query** — Check what's needed at a location
```bash
python3 location_reminders.py query --user ted --location store
```

**complete** — Mark items as done
```bash
python3 location_reminders.py complete --user ted --location store --items "milk"
```

**clear** — Clear all items for a location
```bash
python3 location_reminders.py clear --user ted --location store
```

**list** — Show all locations with pending items
```bash
python3 location_reminders.py list --user ted
```

## Natural Language Patterns

The agent should recognize these patterns and map to actions:
- "Add X to my store list" → add
- "Remind me to get X at the pharmacy" → add
- "What do I need at the store?" → query
- "Going to the store" → query
- "Done with store list" / "Clear store" → clear
- "Got the milk" / "Bought the eggs" → complete
- "What lists do I have?" → list

## Location Aliases

Common aliases are handled automatically:
- supermarket, grocery, groceries → store
- chemist → pharmacy
- gym, fitness → gym
