"""Geofence engine — haversine distance, state machine, enter/leave detection."""
import json
import math
import os
import logging
from datetime import datetime, timedelta

import config

logger = logging.getLogger(__name__)

DATA_FILE = os.path.join(config.DATA_DIR, "smart_locations.json")


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance in meters between two GPS points."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def load_locations(user_id):
    """Load saved locations and reminders for a user."""
    if not os.path.exists(DATA_FILE):
        return {"locations": [], "reminders": [], "geofence_state": {}}
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data.get(user_id, {"locations": [], "reminders": [], "geofence_state": {}})
    except (json.JSONDecodeError, IOError):
        return {"locations": [], "reminders": [], "geofence_state": {}}


def save_user_data(user_id, user_data):
    """Save user data back to the shared JSON file."""
    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = {}

    data[user_id] = user_data
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def check_geofences(user_id, lat, lon):
    """Check GPS against all saved locations. Returns list of triggered notifications."""
    user = load_locations(user_id)
    notifications = []

    for loc in user.get("locations", []):
        dist = haversine_m(lat, lon, loc["lat"], loc["lon"])
        loc_key = loc["name"].lower()
        radius = loc.get("radius", config.DEFAULT_RADIUS_M)

        state = user.get("geofence_state", {}).get(loc_key, {
            "inside": False, "samples": 0, "last_notif": ""
        })

        if dist <= radius:
            # Inside zone
            state["samples"] = state.get("samples", 0) + 1

            if state["samples"] >= 2 and not state.get("inside"):
                # Check cooldown
                last = state.get("last_notif", "")
                if last:
                    try:
                        last_dt = datetime.fromisoformat(last)
                        if datetime.now() - last_dt < timedelta(minutes=config.GEOFENCE_COOLDOWN_MIN):
                            continue
                    except ValueError:
                        pass

                state["inside"] = True
                state["last_notif"] = datetime.now().isoformat()

                # Find active reminders for this location
                active = [r for r in user.get("reminders", [])
                          if r["location"].lower() == loc_key and not r.get("completed")]

                if active:
                    for r in active:
                        r["triggered_count"] = r.get("triggered_count", 0) + 1
                        notifications.append({
                            "type": "enter",
                            "location": loc["name"],
                            "distance": int(dist),
                            "message": f"You're near {loc['name']}! Reminder: {r['action']}",
                        })
                else:
                    notifications.append({
                        "type": "enter",
                        "location": loc["name"],
                        "distance": int(dist),
                        "message": f"You've arrived at {loc['name']} ({int(dist)}m away)",
                    })

                logger.info(f"ENTER: {loc['name']} ({int(dist)}m)")
        else:
            # Outside zone
            if state.get("inside"):
                state["inside"] = False
                state["samples"] = 0
                notifications.append({
                    "type": "exit",
                    "location": loc["name"],
                    "distance": int(dist),
                    "message": f"You've left {loc['name']}",
                })
                logger.info(f"EXIT: {loc['name']} ({int(dist)}m)")
            else:
                state["samples"] = max(0, state.get("samples", 0) - 1)

        user.setdefault("geofence_state", {})[loc_key] = state

    # Save updated state
    save_user_data(user_id, user)
    return notifications
