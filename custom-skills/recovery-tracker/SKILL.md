---
name: recovery-tracker
description: "Use this skill to track addiction recovery streaks, log relapses, record triggers, and view recovery milestones. Handles 'how many days clean', 'I relapsed', 'log trigger', 'recovery stats', 'milestone check'. Celebrates victories at 7, 14, 30, 60, 90 days. Tracks trigger patterns over time."
user_invocable: true
---

# Recovery Streak Tracker

Track consecutive clean days, log relapses with trigger analysis, celebrate milestones, and identify patterns.

## Usage

```bash
python3 recovery_tracker.py <action> --user <user_id> [options]
```

### Actions

**status** — Show current streak and stats
```bash
python3 recovery_tracker.py status --user ted
```

**relapse** — Log a relapse (resets streak, records trigger)
```bash
python3 recovery_tracker.py relapse --user ted --trigger "boredom" --note "Late night, phone in bed"
```

**trigger** — Log a trigger that was RESISTED (victory!)
```bash
python3 recovery_tracker.py trigger --user ted --trigger "stress" --note "Resisted after work argument"
```

**milestones** — Show achieved and upcoming milestones
```bash
python3 recovery_tracker.py milestones --user ted
```

**patterns** — Analyze trigger patterns over time
```bash
python3 recovery_tracker.py patterns --user ted
```

**history** — Show recovery history (streaks and relapses)
```bash
python3 recovery_tracker.py history --user ted --days 90
```

### Trigger Categories
- boredom, stress, loneliness, late_night, phone_in_bed
- anger, argument, sadness, anxiety, fatigue
- visual_trigger, environmental, social_pressure

### Milestones
- Day 1: First step
- Day 7: One week — brain starting to adjust
- Day 14: Two weeks — flatline may be ending
- Day 30: One month — significant rewiring
- Day 60: Two months — new habits forming
- Day 90: Three months — major milestone, new baseline
- Day 180: Six months — deep recovery
- Day 365: One year — transformation

## Agent Behavior
- Check streak during every check-in
- Celebrate milestones enthusiastically
- After relapse: compassion first, trigger analysis second, plan third
- Reference past victories when user is struggling
- Track patterns: "Your highest risk times are..."
