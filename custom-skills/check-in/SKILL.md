---
name: check-in
description: "Use this skill for wellness check-ins, mood tracking, and daily reflection. Handles 'how am I doing', 'log my mood', 'track mood 7', 'show my mood history', 'weekly summary'. Supports mood rating (1-10), notes, and trend analysis."
user_invocable: true
---

# Wellness Check-in & Mood Tracker

Track mood ratings, energy levels, and daily reflections over time.

## Usage

```bash
python3 check_in.py <action> --user <user_id> [options]
```

### Actions

**log** — Log a mood entry (1-10 scale)
```bash
python3 check_in.py log --user ted --rating 7 --note "Good day, productive morning"
```

**history** — Show recent mood entries
```bash
python3 check_in.py history --user ted --days 7
```

**summary** — Weekly/monthly summary with trends
```bash
python3 check_in.py summary --user ted --period week
```

**streak** — Show check-in streak
```bash
python3 check_in.py streak --user ted
```

## Agent Behavior

When doing a check-in, the agent should:
1. Ask how the user is feeling (naturally, not clinically)
2. If user gives a number, log it as mood rating
3. If user describes feelings, estimate a rating and confirm
4. Note any patterns (declining mood, improving streak)
5. Celebrate streaks and improvements
