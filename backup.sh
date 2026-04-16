#!/usr/bin/env bash
# TedClaw backup script — backs up PostgreSQL + copies to Google Drive
# Backs up: all agents, memory, conversations, skills config, cron jobs
#
# Usage: ./backup.sh
# Restore: gunzip < backup.sql.gz | docker exec -i tedclaw-postgres-1 psql -U goclaw goclaw

set -euo pipefail

BACKUP_DIR="./backups"
GDRIVE_DIR="D:/NAS/VTC/AI/PROJECTS/Tedbot/backups"
DATE=$(date +%Y%m%d-%H%M)
BACKUP_FILE="${BACKUP_DIR}/tedclaw-${DATE}.sql.gz"

mkdir -p "$BACKUP_DIR"
mkdir -p "$GDRIVE_DIR"

echo "Backing up TedClaw database..."
docker exec tedclaw-postgres-1 pg_dump -U goclaw goclaw | gzip > "$BACKUP_FILE"

SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup saved: $BACKUP_FILE ($SIZE)"

# Copy to Google Drive sync folder
cp "$BACKUP_FILE" "$GDRIVE_DIR/"
echo "Copied to Google Drive: $GDRIVE_DIR/"

# Keep last 30 local backups
ls -t "$BACKUP_DIR"/tedclaw-*.sql.gz 2>/dev/null | tail -n +31 | xargs -r rm

# Keep last 10 Drive backups (save space)
ls -t "$GDRIVE_DIR"/tedclaw-*.sql.gz 2>/dev/null | tail -n +11 | xargs -r rm

echo "Cleanup done (local: 30, Drive: 10)"
