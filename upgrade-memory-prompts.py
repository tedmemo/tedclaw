#!/usr/bin/env python3
"""Upgrade agent AGENTS.md with knowledge management best practices from LLM Wiki research."""
import websocket
import json

ws = websocket.create_connection("ws://localhost:18790/ws")
ws.send(json.dumps({"type": "req", "id": "1", "method": "connect", "params": {
    "token": "451d82e03bd74e24b2119378ff316d03", "user_id": "ted"
}}))
json.loads(ws.recv())

# Add memory upgrade section to TedBot AGENTS.md
tedbot_addition = """

## Advanced Memory Protocol (Knowledge Upgrade)

### Categorize Before Storing
When storing a memory about the user, mentally categorize it:
- **preferences**: likes, dislikes, habits (food, tools, routines)
- **people**: family, friends, colleagues (names, relationships)
- **locations**: home, work, kids house, regular places
- **schedule**: recurring events, work hours, routines
- **goals**: active goals, aspirations, plans
- **health**: wellness data, mood patterns, sleep, exercise

This helps retrieve the right memory faster.

### Contradiction Check
Before storing a new fact:
- Search memory for existing facts on the same topic
- If a new fact contradicts an old one, acknowledge the change:
  "I notice you mentioned X before but now Y — I'll update that."
- Never silently overwrite — acknowledge updates naturally.

### Context Efficiency
- For quick questions, use concise responses (2-3 sentences)
- Only search deep memory when the topic requires personal context
- Reference past conversations sparingly — only when genuinely relevant"""

# Get current TedBot AGENTS.md
ws.send(json.dumps({"type": "req", "id": "get-bot", "method": "agents.files.get", "params": {
    "agentId": "tedbot", "name": "AGENTS.md"
}}))
r = json.loads(ws.recv())
current_bot = r.get("payload", {}).get("content", "")

if "Advanced Memory Protocol" not in current_bot:
    ws.send(json.dumps({"type": "req", "id": "set-bot", "method": "agents.files.set", "params": {
        "agentId": "tedbot", "name": "AGENTS.md", "content": current_bot + tedbot_addition
    }}))
    r = json.loads(ws.recv())
    print(f"TedBot AGENTS.md: {'UPDATED' if r.get('ok') else r.get('error', {}).get('message', '')}")
else:
    print("TedBot AGENTS.md: already has memory protocol")

# Add to TedAngel AGENTS.md
tedangel_addition = """

## Advanced Memory Protocol (Knowledge Upgrade)

### Categorize Before Storing
Tag memories by topic for better retrieval:
- **recovery**: streak, triggers, relapses, victories, patterns
- **faith**: prayer habits, confession frequency, spiritual growth, doubts
- **marriage**: relationship status, communication patterns, issues, wins
- **family**: kids details, parenting moments, family events
- **work**: job situation, stress sources, colleagues, goals
- **emotions**: mood patterns, emotional triggers, coping successes

### Contradiction Check
Before storing a new fact about the user:
- Check if it contradicts something you already know
- If yes, acknowledge naturally: "Last time you mentioned X — has that changed?"
- Preserve history: old facts aren't wrong, they're past state

### Temporal Awareness
- Track WHEN things happened, not just WHAT
- "You've been struggling with this since [date]"
- "Last week you were feeling better about [topic]"
- Recovery streaks are time-sensitive — always reference current day count

### Build Trust Through Memory
- Reference past conversations naturally: "Remember when you told me about...?"
- Celebrate progress over time: "Three weeks ago you were struggling with X, look how far you've come"
- Never make the user repeat themselves — if you know it, show it"""

ws.send(json.dumps({"type": "req", "id": "get-angel", "method": "agents.files.get", "params": {
    "agentId": "tedangel", "name": "AGENTS.md"
}}))
r = json.loads(ws.recv())
current_angel = r.get("payload", {}).get("content", "")

if "Advanced Memory Protocol" not in current_angel:
    ws.send(json.dumps({"type": "req", "id": "set-angel", "method": "agents.files.set", "params": {
        "agentId": "tedangel", "name": "AGENTS.md", "content": current_angel + tedangel_addition
    }}))
    r = json.loads(ws.recv())
    print(f"TedAngel AGENTS.md: {'UPDATED' if r.get('ok') else r.get('error', {}).get('message', '')}")
else:
    print("TedAngel AGENTS.md: already has memory protocol")

ws.close()
print("Memory upgrade complete!")
