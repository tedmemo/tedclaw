---
name: liturgical-calendar
description: "Use this skill for Catholic liturgical calendar information, feast days, saints of the day, and seasonal guidance. Handles 'what feast day is today', 'what liturgical season', 'who is the saint of the day', 'what color is today'. Provides daily Catholic context for spiritual conversations."
user_invocable: true
---

# Catholic Liturgical Calendar

Daily liturgical information: season, feast days, saints, liturgical colors.

## Usage

```bash
python3 liturgical_calendar.py today
python3 liturgical_calendar.py season
python3 liturgical_calendar.py saint --date 2026-04-04
```

### Actions

**today** — Full liturgical info for today
```bash
python3 liturgical_calendar.py today
```

**season** — Current liturgical season with guidance
```bash
python3 liturgical_calendar.py season
```

**saint** — Saint of the day
```bash
python3 liturgical_calendar.py saint
```

## Agent Behavior
- Reference liturgical context naturally in conversations
- On feast days, mention the saint and their relevance
- During Lent: encourage fasting, prayer, almsgiving
- During Advent: encourage preparation, anticipation
- During Easter: celebrate joy, renewal
