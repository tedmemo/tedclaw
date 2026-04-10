"""Reliable scheduler using APScheduler with PostgreSQL persistence."""
import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

import config
import notifier

logger = logging.getLogger(__name__)

# Melbourne timezone
MELB_TZ = ZoneInfo(config.TIMEZONE)

# In-memory reminder metadata (jobs are in APScheduler/PostgreSQL)
reminder_meta = {}


def init_scheduler():
    """Create and configure APScheduler with PostgreSQL job store."""
    jobstores = {
        "default": SQLAlchemyJobStore(url=config.POSTGRES_DSN.replace("postgres://", "postgresql://"))
    }

    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        timezone=MELB_TZ,
        job_defaults={"coalesce": True, "max_instances": 1},
    )

    logger.info(f"Scheduler initialized (timezone={config.TIMEZONE})")
    return scheduler


async def fire_reminder(chat_id, message, reminder_id=None):
    """Callback when a reminder fires."""
    logger.info(f"Reminder fired: chat={chat_id} msg={message[:50]}...")
    await notifier.notify_reminder(int(chat_id), message)

    # Remove metadata for one-time reminders
    if reminder_id and reminder_id in reminder_meta:
        meta = reminder_meta[reminder_id]
        if meta.get("one_time"):
            del reminder_meta[reminder_id]


def add_one_time_reminder(scheduler, chat_id, message, in_minutes=None, at_time=None):
    """Add a one-time reminder."""
    reminder_id = str(uuid.uuid4())[:8]

    if in_minutes:
        run_time = datetime.now(MELB_TZ) + timedelta(minutes=in_minutes)
    elif at_time:
        run_time = at_time
        if run_time.tzinfo is None:
            run_time = run_time.replace(tzinfo=MELB_TZ)
    else:
        raise ValueError("Either in_minutes or at_time required")

    trigger = DateTrigger(run_date=run_time, timezone=MELB_TZ)

    scheduler.add_job(
        fire_reminder,
        trigger=trigger,
        args=[str(chat_id), message, reminder_id],
        id=f"reminder-{reminder_id}",
        name=f"reminder-{reminder_id}",
        replace_existing=True,
    )

    reminder_meta[reminder_id] = {
        "id": reminder_id,
        "message": message,
        "chat_id": chat_id,
        "run_at": run_time.isoformat(),
        "one_time": True,
        "created": datetime.now(MELB_TZ).isoformat(),
    }

    logger.info(f"One-time reminder created: id={reminder_id} at={run_time.isoformat()}")
    return reminder_id, run_time


def add_recurring_reminder(scheduler, chat_id, message, cron_expr):
    """Add a recurring reminder with cron expression."""
    reminder_id = str(uuid.uuid4())[:8]

    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron: '{cron_expr}'. Need 5 fields: min hour dom mon dow")

    trigger = CronTrigger(
        minute=parts[0], hour=parts[1], day=parts[2],
        month=parts[3], day_of_week=parts[4],
        timezone=MELB_TZ,
    )

    scheduler.add_job(
        fire_reminder,
        trigger=trigger,
        args=[str(chat_id), message, reminder_id],
        id=f"reminder-{reminder_id}",
        name=f"reminder-{reminder_id}",
        replace_existing=True,
    )

    reminder_meta[reminder_id] = {
        "id": reminder_id,
        "message": message,
        "chat_id": chat_id,
        "cron": cron_expr,
        "one_time": False,
        "created": datetime.now(MELB_TZ).isoformat(),
    }

    logger.info(f"Recurring reminder created: id={reminder_id} cron={cron_expr}")
    return reminder_id


def list_reminders():
    """List all active reminders."""
    return list(reminder_meta.values())


def remove_reminder(scheduler, reminder_id):
    """Remove a reminder by ID."""
    job_id = f"reminder-{reminder_id}"
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass
    reminder_meta.pop(reminder_id, None)
    logger.info(f"Reminder removed: {reminder_id}")
    return True
