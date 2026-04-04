---
name: weekly-report
description: "Use this skill to generate weekly reflection reports, progress summaries, and trend analysis. Handles 'weekly report', 'how was my week', 'weekly summary', 'progress report'. Aggregates mood, recovery streak, learning, gratitude, and trigger data into a comprehensive weekly review."
user_invocable: true
---

# Weekly Reflection Report

Generate comprehensive weekly progress reports aggregating all tracked data.

## Usage

```bash
python3 weekly_report.py report --user <user_id>
python3 weekly_report.py trends --user <user_id> --weeks 4
```

### Actions

**report** — Generate this week's reflection report
```bash
python3 weekly_report.py report --user ted
```

**trends** — Show multi-week trends
```bash
python3 weekly_report.py trends --user ted --weeks 4
```

## Report Contents
- Recovery streak status + milestones
- Mood average + trend (improving/stable/declining)
- Triggers resisted vs relapses
- Learning entries (IT/Health/Wealth)
- Gratitude highlights
- Suggested focus for next week

## Agent Behavior
Sunday evening: run `report` and share with user. Celebrate victories, gently note areas to focus on. End with encouragement and a prayer.
