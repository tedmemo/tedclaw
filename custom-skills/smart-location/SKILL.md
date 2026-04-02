---
name: smart-location
description: "Use this skill for location-based reminders with GPS tracking, geofences, and proximity alerts. Handles 'remind me when I get to X', 'save this location as Y', 'what do I need at Z', multi-location reminder chains (buy at market, deliver at kid's house). Supports saving locations by name or GPS coordinates, geofence entry/exit detection, and context-aware location reminders."
user_invocable: true
---

# Smart Location System

GPS-based location tracking with geofences, proximity alerts, and context-aware reminders.

## Usage

```bash
python3 smart_location.py <action> --user <user_id> [options]
```

### Actions

**save-location** — Save a named location with coordinates
```bash
python3 smart_location.py save-location --user ted --name "kids house" --lat -37.8136 --lon 144.9631
python3 smart_location.py save-location --user ted --name "Springvale market" --lat -37.9500 --lon 145.1540
python3 smart_location.py save-location --user ted --name "home" --lat -37.8200 --lon 145.0000
```

**add-reminder** — Add a location-triggered reminder
```bash
python3 smart_location.py add-reminder --user ted --location "Springvale market" --action "Buy food for kids" --deliver-to "kids house"
python3 smart_location.py add-reminder --user ted --location "home" --action "Pack kids lunch boxes"
```

**update-gps** — Update current GPS position (from Telegram live location)
```bash
python3 smart_location.py update-gps --user ted --lat -37.9505 --lon 145.1535
```

**check** — Check what reminders are active for current location
```bash
python3 smart_location.py check --user ted --lat -37.9505 --lon 145.1535
```

**list-locations** — Show all saved locations
```bash
python3 smart_location.py list-locations --user ted
```

**list-reminders** — Show all active reminders
```bash
python3 smart_location.py list-reminders --user ted
```

**complete** — Mark a reminder as done
```bash
python3 smart_location.py complete --user ted --reminder-id abc123
```

## Geofence Logic
- Default radius: 200m (configurable per location)
- Entry detection: 2 consecutive GPS samples inside radius
- Cooldown: 30 min between repeat notifications per location
- Haversine formula for distance calculation

## Multi-Location Chains
When a reminder has `deliver-to`, the system creates TWO triggers:
1. Trigger at source location: "Buy food for kids"
2. Trigger at destination: "Give kids their food"

## Agent Behavior
When user shares a Telegram location or mentions a place:
1. Parse the location (GPS coords or place name)
2. If new location, offer to save it
3. If known location, check for active reminders
4. For complex requests, extract multiple locations and actions
