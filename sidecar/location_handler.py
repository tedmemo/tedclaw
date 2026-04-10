"""Telegram live location handler — processes edited_message with GPS updates."""
import logging
from telegram import Update
from telegram.ext import (
    Application, MessageHandler, filters, ContextTypes
)

import config
import geofence_engine
import notifier

logger = logging.getLogger(__name__)


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle both initial and live location updates."""
    msg = update.effective_message
    if not msg or not msg.location:
        return

    lat = msg.location.latitude
    lon = msg.location.longitude
    user_id = str(msg.from_user.id) if msg.from_user else str(config.TELEGRAM_CHAT_ID)
    chat_id = msg.chat_id

    logger.info(f"GPS update: user={user_id} lat={lat:.6f} lon={lon:.6f}")

    # Check geofences
    notifications = geofence_engine.check_geofences(user_id, lat, lon)

    if notifications:
        await notifier.notify_geofence(chat_id, notifications)


async def handle_edited_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle live location updates (edited_message with location).
    This is the key feature GoClaw misses — it skips edited_message entirely."""
    msg = update.edited_message
    if not msg or not msg.location:
        return

    lat = msg.location.latitude
    lon = msg.location.longitude
    user_id = str(msg.from_user.id) if msg.from_user else str(config.TELEGRAM_CHAT_ID)
    chat_id = msg.chat_id

    logger.info(f"Live GPS update: user={user_id} lat={lat:.6f} lon={lon:.6f}")

    # Check geofences on every live update
    notifications = geofence_engine.check_geofences(user_id, lat, lon)

    if notifications:
        await notifier.notify_geofence(chat_id, notifications)


def create_location_bot():
    """Create Telegram bot application for location tracking."""
    if not config.SIDECAR_TELEGRAM_TOKEN:
        logger.warning("SIDECAR_TELEGRAM_TOKEN not set — location tracking disabled")
        return None

    app = Application.builder().token(config.SIDECAR_TELEGRAM_TOKEN).build()

    # Handle initial location shares
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Handle live location updates (edited_message) — THE KEY FEATURE
    app.add_handler(MessageHandler(
        filters.UpdateType.EDITED_MESSAGE & filters.LOCATION,
        handle_edited_location
    ))

    logger.info("Location bot created — handles both initial and live GPS updates")
    return app
