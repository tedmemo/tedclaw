---
name: gratitude-journal
description: "Use this skill for gratitude journaling, daily reflections, and thankfulness tracking. Handles 'I'm grateful for...', '3 things grateful for today', 'show my gratitude entries', 'gratitude review'. Stores daily gratitude entries and shows weekly patterns."
user_invocable: true
---

# Gratitude Journal

Daily gratitude practice with stored entries and pattern analysis.

## Usage

```bash
python3 gratitude_journal.py <action> --user <user_id> [options]
```

### Actions

**add** — Log gratitude entries
```bash
python3 gratitude_journal.py add --user ted --entries "my kids' laughter, a warm meal, making it through the day"
```

**today** — Show today's entries
```bash
python3 gratitude_journal.py today --user ted
```

**week** — Show this week's gratitude review
```bash
python3 gratitude_journal.py week --user ted
```

**stats** — Show gratitude stats and streaks
```bash
python3 gratitude_journal.py stats --user ted
```
