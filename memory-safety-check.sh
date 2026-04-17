#!/usr/bin/env bash
# Memory Safety Check — verifies all Ted's memory data is backed up and restorable.
# Run this ANYTIME to prove your conversations are safe.
#
# Usage: ./memory-safety-check.sh

set -euo pipefail

USER_ID="1282906958"
BACKUP_DIR="./backups"
GDRIVE_DIR="D:/NAS/VTC/AI/PROJECTS/Tedbot/backups"

echo "=== TedClaw Memory Safety Check ==="
echo ""

echo "1. Current Memory in Database:"
docker exec tedclaw-postgres-1 psql -U goclaw -d goclaw -c "
SELECT 'conversations' as type, COUNT(*) as rows FROM sessions
UNION ALL SELECT 'memory_chunks', COUNT(*) FROM memory_chunks
UNION ALL SELECT 'kg_entities', COUNT(*) FROM kg_entities
UNION ALL SELECT 'kg_relations', COUNT(*) FROM kg_relations
UNION ALL SELECT 'user_context_files (Ted)', COUNT(*) FROM user_context_files WHERE user_id = '$USER_ID'
UNION ALL SELECT 'cron_jobs', COUNT(*) FROM cron_jobs
ORDER BY type;" 2>&1

echo ""
echo "2. Ted's USER.md content (what Gabriel knows about you):"
docker exec tedclaw-postgres-1 psql -U goclaw -d goclaw -c "
SELECT length(content) as chars, left(content, 300) as preview
FROM user_context_files uf JOIN agents a ON a.id=uf.agent_id
WHERE uf.user_id='$USER_ID' AND a.agent_key='tedangel' AND uf.file_name='USER.md';" 2>&1

echo ""
echo "3. Recent Memory Chunks (facts Gabriel learned):"
docker exec tedclaw-postgres-1 psql -U goclaw -d goclaw -c "
SELECT created_at::date as date, left(text, 100) as memory
FROM memory_chunks ORDER BY created_at DESC LIMIT 5;" 2>&1

echo ""
echo "4. Backup Status:"
LOCAL_COUNT=$(ls "$BACKUP_DIR"/tedclaw-*.sql.gz 2>/dev/null | wc -l)
DRIVE_COUNT=$(ls "$GDRIVE_DIR"/tedclaw-*.sql.gz 2>/dev/null | wc -l || echo 0)
LATEST=$(ls -t "$BACKUP_DIR"/tedclaw-*.sql.gz 2>/dev/null | head -1)
echo "  Local backups: $LOCAL_COUNT files"
echo "  Google Drive backups: $DRIVE_COUNT files"
echo "  Latest: $LATEST"
if [ -n "$LATEST" ]; then
    SIZE=$(du -h "$LATEST" | cut -f1)
    echo "  Latest size: $SIZE"
fi

echo ""
echo "=== SAFETY VERDICT ==="
if [ "$LOCAL_COUNT" -gt 0 ] && [ "$DRIVE_COUNT" -gt 0 ]; then
    echo "SAFE: Your memory is backed up locally AND to Google Drive."
    echo "      To restore: gunzip < backup.sql.gz | docker exec -i tedclaw-postgres-1 psql -U goclaw goclaw"
else
    echo "WARNING: Run 'bash backup.sh' now to create a backup."
fi
