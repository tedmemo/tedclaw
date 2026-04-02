---
name: learning-tracker
description: "Use this skill when the user wants to track learning progress across IT, Health, or Wealth categories. Handles 'I learned X today', 'log learning about Y', 'show my learning history', 'weekly learning digest', 'what did I learn this week'. TedOS learning system for personal growth tracking."
user_invocable: true
---

# Learning Tracker (TedOS)

Track daily learning across three life pillars: IT (tech skills), Health (wellness), Wealth (finance/career).

## Usage

```bash
python3 learning_tracker.py <action> --user <user_id> [options]
```

### Actions

**log** — Log a learning entry
```bash
python3 learning_tracker.py log --user ted --track it --entry "Learned about GoClaw skill system" --url "https://docs.goclaw.sh" --minutes 30
```

**status** — Show current week progress
```bash
python3 learning_tracker.py status --user ted
```

**history** — Show learning history for a track
```bash
python3 learning_tracker.py history --user ted --track it --days 30
```

**digest** — Generate weekly learning digest
```bash
python3 learning_tracker.py digest --user ted
```

### Tracks
- **it** — Technology, programming, tools, systems
- **health** — Exercise, nutrition, mental health, sleep
- **wealth** — Finance, career, investing, business

## Agent Behavior

When user mentions learning something:
1. Identify which track (IT/Health/Wealth)
2. Extract the topic/entry
3. Log it with the appropriate track
4. Encourage consistency — mention streak if applicable
