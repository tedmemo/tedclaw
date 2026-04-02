#!/usr/bin/env python3
"""Smart location system with geofences, proximity alerts, and multi-location reminders."""
import argparse
import json
import math
import os
import sys
import uuid
from datetime import datetime, timedelta

DATA_DIR = os.environ.get("GOCLAW_WORKSPACE", "/app/workspace")
DATA_FILE = os.path.join(DATA_DIR, "smart_locations.json")
DEFAULT_RADIUS_M = 200
COOLDOWN_MINUTES = 30


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def haversine_m(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two GPS points."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_user(data, user_id):
    if user_id not in data:
        data[user_id] = {"locations": [], "reminders": [], "last_gps": None, "geofence_state": {}}
    return data[user_id]


def save_location(user_id, name, lat, lon, radius=DEFAULT_RADIUS_M):
    data = load_data()
    user = get_user(data, user_id)
    name_lower = name.strip().lower()

    for loc in user["locations"]:
        if loc["name"].lower() == name_lower:
            loc["lat"] = lat
            loc["lon"] = lon
            loc["radius"] = radius
            save_data(data)
            print(f"Updated location: {name} ({lat}, {lon}) radius={radius}m")
            return

    user["locations"].append({
        "name": name.strip(),
        "lat": lat, "lon": lon,
        "radius": radius,
        "created": datetime.now().isoformat(),
    })
    save_data(data)
    print(f"Saved location: {name} ({lat}, {lon}) radius={radius}m")
    print(f"  Total locations: {len(user['locations'])}")


def add_reminder(user_id, location, action, deliver_to=""):
    data = load_data()
    user = get_user(data, user_id)

    reminder_id = str(uuid.uuid4())[:8]
    reminder = {
        "id": reminder_id,
        "location": location.strip(),
        "action": action,
        "completed": False,
        "created": datetime.now().isoformat(),
        "triggered_count": 0,
    }

    user["reminders"].append(reminder)

    # If deliver-to specified, create a chain reminder
    if deliver_to:
        chain_id = str(uuid.uuid4())[:8]
        chain_reminder = {
            "id": chain_id,
            "location": deliver_to.strip(),
            "action": f"Give/deliver: {action}",
            "completed": False,
            "created": datetime.now().isoformat(),
            "triggered_count": 0,
            "chained_from": reminder_id,
        }
        user["reminders"].append(chain_reminder)
        print(f"Reminder chain created:")
        print(f"  1. At {location}: {action} (ID: {reminder_id})")
        print(f"  2. At {deliver_to}: Give/deliver: {action} (ID: {chain_id})")
    else:
        print(f"Reminder added: At {location} -> {action} (ID: {reminder_id})")

    save_data(data)


def update_gps(user_id, lat, lon):
    data = load_data()
    user = get_user(data, user_id)
    user["last_gps"] = {"lat": lat, "lon": lon, "time": datetime.now().isoformat()}

    # Check geofences
    notifications = []
    for loc in user["locations"]:
        dist = haversine_m(lat, lon, loc["lat"], loc["lon"])
        loc_key = loc["name"].lower()
        state = user["geofence_state"].get(loc_key, {"inside": False, "samples": 0, "last_notif": ""})

        if dist <= loc["radius"]:
            state["samples"] = state.get("samples", 0) + 1
            if state["samples"] >= 2 and not state.get("inside"):
                # Check cooldown
                last = state.get("last_notif", "")
                if last:
                    last_dt = datetime.fromisoformat(last)
                    if datetime.now() - last_dt < timedelta(minutes=COOLDOWN_MINUTES):
                        continue

                state["inside"] = True
                state["last_notif"] = datetime.now().isoformat()

                # Find active reminders for this location
                active = [r for r in user["reminders"]
                          if r["location"].lower() == loc_key and not r["completed"]]
                if active:
                    for r in active:
                        r["triggered_count"] = r.get("triggered_count", 0) + 1
                        notifications.append(f"You're near {loc['name']}! Reminder: {r['action']}")
                else:
                    notifications.append(f"You've arrived at {loc['name']} ({int(dist)}m away)")
        else:
            if state.get("inside"):
                state["inside"] = False
                state["samples"] = 0
            else:
                state["samples"] = max(0, state.get("samples", 0) - 1)

        user["geofence_state"][loc_key] = state

    save_data(data)

    if notifications:
        print("NOTIFICATIONS:")
        for n in notifications:
            print(f"  {n}")
    else:
        nearest = None
        nearest_dist = float("inf")
        for loc in user["locations"]:
            d = haversine_m(lat, lon, loc["lat"], loc["lon"])
            if d < nearest_dist:
                nearest_dist = d
                nearest = loc["name"]
        if nearest:
            print(f"GPS updated. Nearest: {nearest} ({int(nearest_dist)}m)")
        else:
            print(f"GPS updated. No saved locations nearby.")


def check_location(user_id, lat, lon):
    data = load_data()
    user = get_user(data, user_id)

    nearby = []
    for loc in user["locations"]:
        dist = haversine_m(lat, lon, loc["lat"], loc["lon"])
        if dist <= loc["radius"] * 3:  # wider check for "nearby"
            reminders = [r for r in user["reminders"]
                         if r["location"].lower() == loc["name"].lower() and not r["completed"]]
            nearby.append({"name": loc["name"], "dist": int(dist), "reminders": reminders})

    if nearby:
        print("Nearby locations:")
        for n in nearby:
            status = "INSIDE" if n["dist"] <= DEFAULT_RADIUS_M else f"{n['dist']}m away"
            print(f"  {n['name']} ({status})")
            for r in n["reminders"]:
                print(f"    -> {r['action']}")
    else:
        print("No saved locations nearby")


def list_locations(user_id):
    data = load_data()
    user = get_user(data, user_id)

    if not user["locations"]:
        print("No saved locations")
        return

    print(f"Saved locations ({len(user['locations'])}):")
    for loc in user["locations"]:
        print(f"  {loc['name']}: ({loc['lat']}, {loc['lon']}) r={loc['radius']}m")


def list_reminders(user_id):
    data = load_data()
    user = get_user(data, user_id)

    active = [r for r in user["reminders"] if not r["completed"]]
    if not active:
        print("No active reminders")
        return

    print(f"Active reminders ({len(active)}):")
    for r in active:
        chain = f" [chained from {r['chained_from']}]" if r.get("chained_from") else ""
        print(f"  [{r['id']}] At {r['location']}: {r['action']}{chain}")


def complete_reminder(user_id, reminder_id):
    data = load_data()
    user = get_user(data, user_id)

    for r in user["reminders"]:
        if r["id"] == reminder_id:
            r["completed"] = True
            r["completed_at"] = datetime.now().isoformat()
            save_data(data)
            print(f"Completed: {r['action']} at {r['location']}")
            return

    print(f"Reminder {reminder_id} not found")


def main():
    parser = argparse.ArgumentParser(description="Smart location system")
    parser.add_argument("action", choices=[
        "save-location", "add-reminder", "update-gps", "check",
        "list-locations", "list-reminders", "complete"
    ])
    parser.add_argument("--user", required=True)
    parser.add_argument("--name", default="")
    parser.add_argument("--lat", type=float, default=0)
    parser.add_argument("--lon", type=float, default=0)
    parser.add_argument("--radius", type=int, default=DEFAULT_RADIUS_M)
    parser.add_argument("--location", default="")
    parser.add_argument("--action-text", dest="action_text", default="")
    parser.add_argument("--deliver-to", default="")
    parser.add_argument("--reminder-id", default="")
    args = parser.parse_args()

    if args.action == "save-location":
        if not args.name or not args.lat:
            print("Error: --name, --lat, --lon required")
            sys.exit(1)
        save_location(args.user, args.name, args.lat, args.lon, args.radius)
    elif args.action == "add-reminder":
        if not args.location or not args.action_text:
            print("Error: --location and --action-text required")
            sys.exit(1)
        add_reminder(args.user, args.location, args.action_text, args.deliver_to)
    elif args.action == "update-gps":
        if not args.lat:
            print("Error: --lat and --lon required")
            sys.exit(1)
        update_gps(args.user, args.lat, args.lon)
    elif args.action == "check":
        if not args.lat:
            print("Error: --lat and --lon required")
            sys.exit(1)
        check_location(args.user, args.lat, args.lon)
    elif args.action == "list-locations":
        list_locations(args.user)
    elif args.action == "list-reminders":
        list_reminders(args.user)
    elif args.action == "complete":
        if not args.reminder_id:
            print("Error: --reminder-id required")
            sys.exit(1)
        complete_reminder(args.user, args.reminder_id)


if __name__ == "__main__":
    main()
