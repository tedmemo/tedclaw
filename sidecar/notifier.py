"""Send notifications via Telegram bot API directly."""
import logging
import httpx

import config

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"


async def send_telegram_message(chat_id, text, token=None):
    """Send a message via Telegram Bot API."""
    bot_token = token or config.TEDBOT_TELEGRAM_TOKEN
    url = f"{TELEGRAM_API}/bot{bot_token}/sendMessage"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            })
            if resp.status_code == 200:
                logger.info(f"Notification sent to {chat_id}: {text[:50]}...")
            else:
                logger.error(f"Telegram API error: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")


async def notify_geofence(chat_id, notifications):
    """Send geofence notifications to user."""
    for n in notifications:
        emoji = "\U0001f4cd" if n["type"] == "enter" else "\U0001f6b6"
        text = f"{emoji} <b>{n['message']}</b>"
        await send_telegram_message(chat_id, text)


async def notify_reminder(chat_id, message):
    """Send a scheduled reminder."""
    text = f"\u23f0 <b>Reminder:</b> {message}"
    await send_telegram_message(chat_id, text)
