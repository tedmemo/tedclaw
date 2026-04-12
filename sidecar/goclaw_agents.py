"""Read and manage GoClaw agent context files (prompts, knowledge) from PostgreSQL."""
import logging
import psycopg2
import psycopg2.extras

import config

logger = logging.getLogger(__name__)


def get_conn():
    dsn = config.POSTGRES_DSN
    return psycopg2.connect(dsn)


def list_agents():
    """List all agents with their models."""
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, agent_key, display_name, provider, model, agent_type, status FROM agents ORDER BY agent_key")
        agents = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": str(a["id"]), "key": a["agent_key"], "display_name": a["display_name"],
                 "provider": a["provider"], "model": a["model"], "type": a["agent_type"],
                 "status": a["status"]} for a in agents]
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        return []


def get_agent_files(agent_key):
    """Get all context files for an agent."""
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT f.file_name, f.content, length(f.content) as chars
            FROM agent_context_files f
            JOIN agents a ON a.id = f.agent_id
            WHERE a.agent_key = %s AND length(f.content) > 0
            ORDER BY f.file_name
        """, (agent_key,))
        files = cur.fetchall()
        cur.close()
        conn.close()
        return [{"name": f["file_name"], "content": f["content"], "chars": f["chars"]} for f in files]
    except Exception as e:
        logger.error(f"Failed to get agent files for {agent_key}: {e}")
        return []


def update_agent_file(agent_key, file_name, content):
    """Update an agent context file."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            UPDATE agent_context_files SET content = %s
            WHERE agent_id = (SELECT id FROM agents WHERE agent_key = %s)
            AND file_name = %s
        """, (content, agent_key, file_name))
        updated = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        return updated > 0
    except Exception as e:
        logger.error(f"Failed to update {file_name} for {agent_key}: {e}")
        return False
