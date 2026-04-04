---
name: prayer-library
description: "Use this skill when the user asks for a prayer, wants to pray, needs spiritual comfort, or asks for confession preparation. Handles 'give me a prayer for strength', 'I need to pray', 'prayer for my marriage', 'help me prepare for confession', 'rosary guide', 'examination of conscience'. Contains full prayer texts ready to share."
user_invocable: true
---

# Catholic Prayer Library & Confession Prep

Instant access to prayers, confession preparation, and spiritual exercises.

## Usage

```bash
python3 prayer_library.py <action> [options]
```

### Actions

**prayer** — Get a prayer by topic
```bash
python3 prayer_library.py prayer --topic strength
python3 prayer_library.py prayer --topic marriage
python3 prayer_library.py prayer --topic purity
python3 prayer_library.py prayer --topic anxiety
python3 prayer_library.py prayer --topic morning
python3 prayer_library.py prayer --topic evening
python3 prayer_library.py prayer --topic protection
python3 prayer_library.py prayer --topic contrition
python3 prayer_library.py prayer --topic rosary
```

**confession** — Guided examination of conscience
```bash
python3 prayer_library.py confession
```

**verse** — Get a Bible verse by topic
```bash
python3 prayer_library.py verse --topic temptation
python3 prayer_library.py verse --topic hope
python3 prayer_library.py verse --topic anger
python3 prayer_library.py verse --topic marriage
```

**saint** — Get a saint's quote for encouragement
```bash
python3 prayer_library.py saint
```

### Topics for Prayers
strength, purity, marriage, anxiety, morning, evening, protection, contrition, rosary, temptation, peace, forgiveness, family, work, suffering

### Topics for Verses
temptation, hope, anger, marriage, strength, peace, fear, love, suffering, forgiveness, patience, gratitude

## Agent Behavior
When user says "I need a prayer" or "pray with me":
1. Identify the need (strength? purity? anxiety? marriage?)
2. Run the prayer action with matching topic
3. Present the full prayer text warmly
4. Offer to pray together or suggest when to pray it
