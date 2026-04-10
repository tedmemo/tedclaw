"""Sidecar configuration from environment variables."""
import os

# Telegram bot for location tracking (separate bot from GoClaw's TedBot)
SIDECAR_TELEGRAM_TOKEN = os.environ.get("SIDECAR_TELEGRAM_TOKEN", "")

# Main TedBot token for sending notifications
TEDBOT_TELEGRAM_TOKEN = os.environ.get("GOCLAW_TELEGRAM_TOKEN", "")
TEDANGEL_TELEGRAM_TOKEN = os.environ.get("TEDANGEL_TELEGRAM_TOKEN", "")

# User's Telegram chat ID
TELEGRAM_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID", "1282906958"))

# PostgreSQL
POSTGRES_DSN = os.environ.get(
    "POSTGRES_DSN",
    "postgres://goclaw:tedclaw_secure_2026@localhost:5432/goclaw"
)

# GoClaw WebSocket
GOCLAW_WS_URL = os.environ.get("GOCLAW_WS_URL", "ws://localhost:18790/ws")
GOCLAW_GATEWAY_TOKEN = os.environ.get("GOCLAW_GATEWAY_TOKEN", "")

# Geofence
DEFAULT_RADIUS_M = int(os.environ.get("DEFAULT_RADIUS_M", "200"))
GEOFENCE_COOLDOWN_MIN = int(os.environ.get("GEOFENCE_COOLDOWN_MIN", "30"))

# Scheduler
TIMEZONE = os.environ.get("TZ", "Australia/Melbourne")

# API
API_PORT = int(os.environ.get("API_PORT", "8080"))

# Data file (shared with GoClaw's smart-location skill)
DATA_DIR = os.environ.get("DATA_DIR", "/app/workspace")
