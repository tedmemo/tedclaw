"""Read and manage GoClaw cron jobs directly from PostgreSQL."""
import logging
import psycopg2
import psycopg2.extras

import config

logger = logging.getLogger(__name__)


def get_conn():
    """Get PostgreSQL connection using GoClaw's DSN."""
    dsn = config.POSTGRES_DSN
    return psycopg2.connect(dsn)


def list_goclaw_crons():
    """List all GoClaw cron jobs."""
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT id, name, schedule_kind, cron_expression, interval_ms,
                   timezone, enabled, deliver, deliver_channel, deliver_to,
                   next_run_at, last_run_at, last_status, last_error,
                   payload::text as payload
            FROM cron_jobs ORDER BY name
        """)
        jobs = cur.fetchall()
        cur.close()
        conn.close()

        result = []
        for j in jobs:
            # Extract message from payload JSON
            import json
            msg = ""
            try:
                p = json.loads(j["payload"]) if j["payload"] else {}
                msg = p.get("message", "")
            except (json.JSONDecodeError, TypeError):
                pass

            result.append({
                "id": str(j["id"]),
                "name": j["name"],
                "schedule_kind": j["schedule_kind"],
                "cron_expression": j["cron_expression"] or "",
                "interval_ms": j["interval_ms"],
                "timezone": j["timezone"] or "UTC",
                "enabled": j["enabled"],
                "deliver_channel": j["deliver_channel"] or "",
                "deliver_to": j["deliver_to"] or "",
                "next_run_at": str(j["next_run_at"]) if j["next_run_at"] else "",
                "last_run_at": str(j["last_run_at"]) if j["last_run_at"] else "",
                "last_status": j["last_status"] or "",
                "last_error": j["last_error"] or "",
                "message": msg[:100],
            })
        return result
    except Exception as e:
        logger.error(f"Failed to list GoClaw crons: {e}")
        return []


def delete_goclaw_cron(job_id):
    """Delete a GoClaw cron job by ID."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM cron_jobs WHERE id = %s", (job_id,))
        deleted = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        return deleted > 0
    except Exception as e:
        logger.error(f"Failed to delete GoClaw cron {job_id}: {e}")
        return False


def toggle_goclaw_cron(job_id, enabled):
    """Enable or disable a GoClaw cron job."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE cron_jobs SET enabled = %s WHERE id = %s", (enabled, job_id))
        updated = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        return updated > 0
    except Exception as e:
        logger.error(f"Failed to toggle GoClaw cron {job_id}: {e}")
        return False
