#!/usr/bin/env python3
"""TedClaw Sidecar — location tracking, reliable scheduling, skill execution.

Runs alongside GoClaw to handle what it can't:
- Telegram live location (edited_message GPS updates)
- Geofence enter/leave detection
- Reliable APScheduler-based reminders
- Simple REST API for AI agents
"""
import asyncio
import logging
import threading
import uvicorn

import config
import scheduler
import location_handler
import reminder_api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("sidecar")


def run_api(sched_instance):
    """Run FastAPI in a separate thread."""
    reminder_api.set_scheduler(sched_instance)
    uvicorn.run(
        reminder_api.app,
        host="0.0.0.0",
        port=config.API_PORT,
        log_level="info",
    )


async def main():
    logger.info("TedClaw Sidecar starting...")
    logger.info(f"  Timezone: {config.TIMEZONE}")
    logger.info(f"  API port: {config.API_PORT}")
    logger.info(f"  Chat ID: {config.TELEGRAM_CHAT_ID}")

    # Init scheduler
    sched = scheduler.init_scheduler()
    sched.start()
    logger.info("Scheduler started")

    # Start API server in background thread
    api_thread = threading.Thread(
        target=run_api, args=(sched,), daemon=True
    )
    api_thread.start()
    logger.info(f"API server started on port {config.API_PORT}")

    # Start location bot (if token configured)
    location_app = location_handler.create_location_bot()
    if location_app:
        logger.info("Starting location bot (polling for GPS updates)...")
        await location_app.initialize()
        await location_app.start()
        await location_app.updater.start_polling(
            allowed_updates=["message", "edited_message"],
            drop_pending_updates=True,
        )
        logger.info("Location bot running — listening for GPS updates")
    else:
        logger.warning("No SIDECAR_TELEGRAM_TOKEN — location tracking not active")
        logger.info("Set SIDECAR_TELEGRAM_TOKEN in .env to enable location tracking")

    logger.info("Sidecar fully operational!")

    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        sched.shutdown()
        if location_app:
            await location_app.updater.stop()
            await location_app.stop()
            await location_app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
