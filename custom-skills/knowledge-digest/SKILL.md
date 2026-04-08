---
name: knowledge-digest
description: "Use this skill to generate daily or weekly summaries of captured knowledge, show topic growth, and suggest organization. Handles 'what did I save this week', 'knowledge digest', 'show my captures', 'knowledge stats'. Surfaces patterns in saved URLs and bookmarks."
user_invocable: true
---

# Knowledge Digest

Periodic summary of captured knowledge — what was saved, topic growth, and suggestions.

## Usage

```bash
python3 knowledge_digest.py <action> --user <user_id> [options]
```

### Actions

**daily** — Today's capture summary
```bash
python3 knowledge_digest.py daily --user ted
```

**weekly** — This week's digest with topic analysis
```bash
python3 knowledge_digest.py weekly --user ted
```

**topics** — Show all topics and their growth
```bash
python3 knowledge_digest.py topics --user ted
```

## Agent Behavior
- Can be triggered by weekly cron (Sunday) or user asking "what did I save"
- Highlight growing topics and suggest organization
- Note connections between items
