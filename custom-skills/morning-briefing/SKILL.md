---
name: morning-briefing
description: "Use this skill to generate a personalized morning briefing with recovery streak, mood trend, due flashcards, today's liturgical info, and a Bible verse. Handles 'morning briefing', 'daily digest', 'what's my day look like', 'morning summary'."
user_invocable: true
---

# Morning Briefing

Personalized daily digest combining all tracked data into one morning message.

## Usage

```bash
python3 morning_briefing.py --user <user_id>
```

## Briefing Contents
1. Recovery streak status
2. Mood trend (last 3 days)
3. Due flashcards count
4. Today's liturgical info (season, feast day, saint)
5. A Bible verse for the day
6. Any active location reminders

## Agent Behavior
Can be triggered by morning cron or user asking "morning briefing" or "what's my day".
