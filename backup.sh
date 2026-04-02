#!/usr/bin/env bash
# TedClaw backup script — run daily via cron or manually
# Backs up: PostgreSQL (all agents, memory, conversations, skills config)
#
# Usage: ./backup.sh
# Restore: cat backup-YYYYMMDD.sql | docker exec -i tedclaw-postgres-1 psql -U goclaw goclaw

set -euo pipefail

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d-%H%M)
BACKUP_FILE="${BACKUP_DIR}/tedclaw-${DATE}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "Backing up TedClaw database..."
docker exec tedclaw-postgres-1 pg_dump -U goclaw goclaw | gzip > "$BACKUP_FILE"

SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup saved: $BACKUP_FILE ($SIZE)"

# Keep only last 30 backups
ls -t "$BACKUP_DIR"/tedclaw-*.sql.gz 2>/dev/null | tail -n +31 | xargs -r rm
echo "Old backups cleaned (keeping last 30)"

# Optional: commit to git for offsite backup
if [ "${1:-}" = "--git" ]; then
    git add "$BACKUP_DIR"/*.sql.gz
    git commit -m "backup: tedclaw database $(date +%Y-%m-%d)"
    echo "Committed to git"
fi
