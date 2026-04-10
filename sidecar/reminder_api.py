"""Simple REST API for AI agents to create/manage reminders.

Much simpler than GoClaw's cron tool — fewer fields, less room for error.
The AI calls this via web_fetch tool.
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

import config
import scheduler as sched

logger = logging.getLogger(__name__)

app = FastAPI(title="TedClaw Sidecar API", version="1.0.0")

MELB_TZ = ZoneInfo(config.TIMEZONE)

# Will be set by sidecar.py after scheduler init
_scheduler = None


def set_scheduler(s):
    global _scheduler
    _scheduler = s


class ReminderRequest(BaseModel):
    message: str = Field(..., description="Reminder text")
    in_minutes: Optional[int] = Field(None, description="Minutes from now (one-time)")
    cron: Optional[str] = Field(None, description="Cron expression (recurring)")
    chat_id: Optional[int] = Field(None, description="Telegram chat ID")


class LocationRequest(BaseModel):
    name: str
    lat: float
    lon: float
    radius: Optional[int] = 200
    user_id: Optional[str] = None


class LocationReminderRequest(BaseModel):
    location: str
    action: str
    deliver_to: Optional[str] = None
    user_id: Optional[str] = None


@app.get("/health")
async def health():
    return {"status": "ok", "service": "tedclaw-sidecar"}


@app.post("/api/reminder")
async def create_reminder(req: ReminderRequest):
    """Create a reminder. AI calls this via web_fetch."""
    if not _scheduler:
        raise HTTPException(500, "Scheduler not initialized")

    chat_id = req.chat_id or config.TELEGRAM_CHAT_ID

    if req.in_minutes:
        rid, run_at = sched.add_one_time_reminder(_scheduler, chat_id, req.message, in_minutes=req.in_minutes)
        return {
            "ok": True,
            "id": rid,
            "type": "one-time",
            "fires_at": run_at.strftime("%I:%M %p Melbourne time"),
            "fires_at_iso": run_at.isoformat(),
            "message": req.message,
        }
    elif req.cron:
        rid = sched.add_recurring_reminder(_scheduler, chat_id, req.message, req.cron)
        return {
            "ok": True,
            "id": rid,
            "type": "recurring",
            "cron": req.cron,
            "timezone": config.TIMEZONE,
            "message": req.message,
        }
    else:
        raise HTTPException(400, "Either 'in_minutes' or 'cron' is required")


@app.get("/api/reminders")
async def list_reminders():
    """List all active reminders."""
    reminders = sched.list_reminders()
    return {"ok": True, "count": len(reminders), "reminders": reminders}


@app.delete("/api/reminder/{reminder_id}")
async def delete_reminder(reminder_id: str):
    """Delete a reminder."""
    if not _scheduler:
        raise HTTPException(500, "Scheduler not initialized")
    sched.remove_reminder(_scheduler, reminder_id)
    return {"ok": True, "deleted": reminder_id}


@app.post("/api/location")
async def save_location(req: LocationRequest):
    """Save a named location for geofencing."""
    import geofence_engine
    user_id = req.user_id or str(config.TELEGRAM_CHAT_ID)
    user = geofence_engine.load_locations(user_id)

    # Update or add location
    name_lower = req.name.strip().lower()
    found = False
    for loc in user.get("locations", []):
        if loc["name"].lower() == name_lower:
            loc["lat"] = req.lat
            loc["lon"] = req.lon
            loc["radius"] = req.radius
            found = True
            break

    if not found:
        user.setdefault("locations", []).append({
            "name": req.name.strip(),
            "lat": req.lat, "lon": req.lon,
            "radius": req.radius,
            "created": datetime.now(MELB_TZ).isoformat(),
        })

    geofence_engine.save_user_data(user_id, user)
    return {"ok": True, "location": req.name, "lat": req.lat, "lon": req.lon}


@app.post("/api/location-reminder")
async def add_location_reminder(req: LocationReminderRequest):
    """Add a location-triggered reminder."""
    import geofence_engine
    import uuid
    user_id = req.user_id or str(config.TELEGRAM_CHAT_ID)
    user = geofence_engine.load_locations(user_id)

    reminder_id = str(uuid.uuid4())[:8]
    user.setdefault("reminders", []).append({
        "id": reminder_id,
        "location": req.location.strip(),
        "action": req.action,
        "completed": False,
        "created": datetime.now(MELB_TZ).isoformat(),
        "triggered_count": 0,
    })

    geofence_engine.save_user_data(user_id, user)
    return {"ok": True, "id": reminder_id, "location": req.location, "action": req.action}


@app.get("/api/locations")
async def list_locations():
    """List saved locations and active reminders."""
    import geofence_engine
    user_id = str(config.TELEGRAM_CHAT_ID)
    user = geofence_engine.load_locations(user_id)
    return {
        "ok": True,
        "locations": user.get("locations", []),
        "reminders": [r for r in user.get("reminders", []) if not r.get("completed")],
    }


class GPSCheckRequest(BaseModel):
    lat: float
    lon: float
    user_id: Optional[str] = None
    chat_id: Optional[int] = None


@app.post("/api/check-gps")
async def check_gps(req: GPSCheckRequest):
    """Check current GPS against saved geofences.

    The AI agent calls this when user shares location.
    Returns any triggered notifications (enter/leave geofences).
    """
    import geofence_engine
    user_id = req.user_id or str(config.TELEGRAM_CHAT_ID)
    chat_id = req.chat_id or config.TELEGRAM_CHAT_ID

    notifications = geofence_engine.check_geofences(user_id, req.lat, req.lon)

    # Also send Telegram notifications directly
    if notifications:
        await notifier.notify_geofence(chat_id, notifications)

    return {
        "ok": True,
        "lat": req.lat,
        "lon": req.lon,
        "notifications": notifications,
        "count": len(notifications),
    }
