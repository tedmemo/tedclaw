"""Simple REST API for AI agents to create/manage reminders.

Much simpler than GoClaw's cron tool — fewer fields, less room for error.
The AI calls this via web_fetch tool.
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional

import config
import scheduler as sched
import goclaw_cron
import goclaw_agents
import notifier

logger = logging.getLogger(__name__)

app = FastAPI(title="TedClaw Sidecar API", version="1.0.0")

MELB_TZ = ZoneInfo(config.TIMEZONE)

# Will be set by sidecar.py after scheduler init
_scheduler = None


def set_scheduler(s):
    global _scheduler
    _scheduler = s


## GoClaw Cron Management Endpoints

@app.get("/api/goclaw-crons")
async def list_goclaw_crons():
    """List all GoClaw cron jobs (system check-ins + bot-created)."""
    jobs = goclaw_cron.list_goclaw_crons()
    return {"ok": True, "count": len(jobs), "jobs": jobs}


@app.delete("/api/goclaw-cron/{job_id}")
async def delete_goclaw_cron(job_id: str):
    """Delete a GoClaw cron job by UUID."""
    ok = goclaw_cron.delete_goclaw_cron(job_id)
    return {"ok": ok, "deleted": job_id if ok else None}


@app.post("/api/goclaw-cron/{job_id}/toggle")
async def toggle_goclaw_cron(job_id: str, enabled: bool = True):
    """Enable or disable a GoClaw cron job."""
    ok = goclaw_cron.toggle_goclaw_cron(job_id, enabled)
    return {"ok": ok, "job_id": job_id, "enabled": enabled}


## Agent Prompt Management Endpoints

@app.get("/api/agents")
async def list_agents():
    """List all agents."""
    agents = goclaw_agents.list_agents()
    return {"ok": True, "agents": agents}


@app.get("/api/agents/{agent_key}/files")
async def get_agent_files(agent_key: str):
    """Get all context files for an agent."""
    files = goclaw_agents.get_agent_files(agent_key)
    return {"ok": True, "agent": agent_key, "files": files}


class FileUpdateRequest(BaseModel):
    content: str


@app.put("/api/agents/{agent_key}/files/{file_name}")
async def update_agent_file(agent_key: str, file_name: str, req: FileUpdateRequest):
    """Update an agent context file (prompt/knowledge)."""
    ok = goclaw_agents.update_agent_file(agent_key, file_name, req.content)
    return {"ok": ok, "agent": agent_key, "file": file_name, "chars": len(req.content)}


class ReminderRequest(BaseModel):
    message: str = Field(..., description="Reminder text")
    in_minutes: Optional[int] = Field(None, description="Minutes from now (one-time)")
    cron: Optional[str] = Field(None, description="Cron expression (recurring)")
    chat_id: Optional[int] = Field(None, description="Telegram chat ID")


class LocationRequest(BaseModel):
    name: str
    lat: float
    lon: float
    radius: Optional[int] = 200
    user_id: Optional[str] = None


class LocationReminderRequest(BaseModel):
    location: str
    action: str
    deliver_to: Optional[str] = None
    user_id: Optional[str] = None


@app.get("/health")
async def health():
    return {"status": "ok", "service": "tedclaw-sidecar"}


@app.post("/api/reminder")
async def create_reminder(req: ReminderRequest):
    """Create a reminder. AI calls this via web_fetch."""
    if not _scheduler:
        raise HTTPException(500, "Scheduler not initialized")

    chat_id = req.chat_id or config.TELEGRAM_CHAT_ID

    if req.in_minutes:
        rid, run_at = sched.add_one_time_reminder(_scheduler, chat_id, req.message, in_minutes=req.in_minutes)
        return {
            "ok": True,
            "id": rid,
            "type": "one-time",
            "fires_at": run_at.strftime("%I:%M %p Melbourne time"),
            "fires_at_iso": run_at.isoformat(),
            "message": req.message,
        }
    elif req.cron:
        rid = sched.add_recurring_reminder(_scheduler, chat_id, req.message, req.cron)
        return {
            "ok": True,
            "id": rid,
            "type": "recurring",
            "cron": req.cron,
            "timezone": config.TIMEZONE,
            "message": req.message,
        }
    else:
        raise HTTPException(400, "Either 'in_minutes' or 'cron' is required")


@app.get("/api/reminders")
async def list_reminders():
    """List all active reminders."""
    reminders = sched.list_reminders()
    return {"ok": True, "count": len(reminders), "reminders": reminders}


@app.delete("/api/reminder/{reminder_id}")
async def delete_reminder(reminder_id: str):
    """Delete a reminder."""
    if not _scheduler:
        raise HTTPException(500, "Scheduler not initialized")
    sched.remove_reminder(_scheduler, reminder_id)
    return {"ok": True, "deleted": reminder_id}


@app.post("/api/location")
async def save_location(req: LocationRequest):
    """Save a named location for geofencing."""
    import geofence_engine
    user_id = req.user_id or str(config.TELEGRAM_CHAT_ID)
    user = geofence_engine.load_locations(user_id)

    # Update or add location
    name_lower = req.name.strip().lower()
    found = False
    for loc in user.get("locations", []):
        if loc["name"].lower() == name_lower:
            loc["lat"] = req.lat
            loc["lon"] = req.lon
            loc["radius"] = req.radius
            found = True
            break

    if not found:
        user.setdefault("locations", []).append({
            "name": req.name.strip(),
            "lat": req.lat, "lon": req.lon,
            "radius": req.radius,
            "created": datetime.now(MELB_TZ).isoformat(),
        })

    geofence_engine.save_user_data(user_id, user)
    return {"ok": True, "location": req.name, "lat": req.lat, "lon": req.lon}


@app.post("/api/location-reminder")
async def add_location_reminder(req: LocationReminderRequest):
    """Add a location-triggered reminder."""
    import geofence_engine
    import uuid
    user_id = req.user_id or str(config.TELEGRAM_CHAT_ID)
    user = geofence_engine.load_locations(user_id)

    reminder_id = str(uuid.uuid4())[:8]
    user.setdefault("reminders", []).append({
        "id": reminder_id,
        "location": req.location.strip(),
        "action": req.action,
        "completed": False,
        "created": datetime.now(MELB_TZ).isoformat(),
        "triggered_count": 0,
    })

    geofence_engine.save_user_data(user_id, user)
    return {"ok": True, "id": reminder_id, "location": req.location, "action": req.action}


@app.get("/api/openrouter-usage")
async def openrouter_usage():
    """Get OpenRouter API usage and costs."""
    import httpx
    key = config.GOCLAW_GATEWAY_TOKEN  # We'll use the OpenRouter key from env
    or_key = ""
    try:
        import os
        or_key = os.environ.get("GOCLAW_OPENROUTER_API_KEY", "")
    except Exception:
        pass
    if not or_key:
        return {"ok": False, "error": "No OpenRouter key"}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://openrouter.ai/api/v1/auth/key",
                                 headers={"Authorization": f"Bearer {or_key}"})
            d = r.json().get("data", {})
            return {
                "ok": True,
                "total": round(d.get("usage", 0), 4),
                "today": round(d.get("usage_daily", 0), 4),
                "week": round(d.get("usage_weekly", 0), 4),
                "month": round(d.get("usage_monthly", 0), 4),
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/locations")
async def list_locations():
    """List saved locations and active reminders."""
    import geofence_engine
    user_id = str(config.TELEGRAM_CHAT_ID)
    user = geofence_engine.load_locations(user_id)
    return {
        "ok": True,
        "locations": user.get("locations", []),
        "reminders": [r for r in user.get("reminders", []) if not r.get("completed")],
    }


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Management dashboard — view and manage reminders, locations, cron jobs."""
    import geofence_engine
    user_id = str(config.TELEGRAM_CHAT_ID)

    reminders = sched.list_reminders()
    user = geofence_engine.load_locations(user_id)
    locations = user.get("locations", [])
    loc_reminders = [r for r in user.get("reminders", []) if not r.get("completed")]

    # Build reminders HTML
    rem_rows = ""
    for r in reminders:
        rtype = "One-time" if r.get("one_time") else "Recurring"
        when = r.get("run_at", r.get("cron", ""))
        rem_rows += f"<tr><td>{r['id']}</td><td>{r['message']}</td><td>{rtype}</td><td>{when}</td>"
        rem_rows += f'<td><button onclick="del_reminder(\'{r["id"]}\')">Delete</button></td></tr>'

    if not rem_rows:
        rem_rows = '<tr><td colspan="5">No active reminders</td></tr>'

    # Build locations HTML
    loc_rows = ""
    for l in locations:
        loc_rows += f"<tr><td>{l['name']}</td><td>{l['lat']:.4f}</td><td>{l['lon']:.4f}</td><td>{l.get('radius', 200)}m</td></tr>"

    if not loc_rows:
        loc_rows = '<tr><td colspan="4">No saved locations</td></tr>'

    # Build location reminders HTML
    locrem_rows = ""
    for r in loc_reminders:
        locrem_rows += f"<tr><td>{r.get('id','')}</td><td>{r['location']}</td><td>{r['action']}</td><td>{r.get('triggered_count',0)}</td></tr>"

    if not locrem_rows:
        locrem_rows = '<tr><td colspan="4">No location reminders</td></tr>'

    return f"""<!DOCTYPE html>
<html><head>
<title>TedClaw Sidecar</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #e0e0e0; }}
  h1 {{ color: #00d4ff; }} h2 {{ color: #7c83ff; border-bottom: 1px solid #333; padding-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0 30px; }}
  th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #333; }}
  th {{ background: #16213e; color: #00d4ff; }}
  tr:hover {{ background: #16213e; }}
  button {{ background: #e74c3c; color: white; border: none; padding: 5px 12px; border-radius: 4px; cursor: pointer; }}
  button:hover {{ background: #c0392b; }}
  .btn-add {{ background: #27ae60; }} .btn-add:hover {{ background: #219a52; }}
  input, select {{ padding: 6px 10px; border: 1px solid #444; border-radius: 4px; background: #16213e; color: #e0e0e0; margin: 4px; }}
  .form-row {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 10px 0; }}
  .status {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
  .ok {{ background: #27ae60; }} .warn {{ background: #f39c12; }}
  #msg {{ padding: 10px; margin: 10px 0; border-radius: 4px; display: none; }}
</style>
</head><body>
<h1>TedClaw Sidecar Dashboard</h1>
<p><span class="status ok">ONLINE</span> Melbourne time: {datetime.now(ZoneInfo('Australia/Melbourne')).strftime('%I:%M %p %a %d %b')}</p>
<div id="cost-display" style="display:flex;gap:20px;background:#16213e;padding:10px;border-radius:6px;margin:10px 0">
  <span>Loading costs...</span>
</div>

<div id="msg"></div>

<h2>Time Reminders ({len(reminders)})</h2>
<table><tr><th>ID</th><th>Message</th><th>Type</th><th>When</th><th>Action</th></tr>{rem_rows}</table>

<div class="form-row">
  <input id="rem-msg" placeholder="Reminder message" size="30">
  <input id="rem-min" type="number" placeholder="Minutes" size="8">
  <button class="btn-add" onclick="add_reminder()">Add Reminder</button>
</div>

<h2>Saved Locations ({len(locations)})</h2>
<table><tr><th>Name</th><th>Lat</th><th>Lon</th><th>Radius</th></tr>{loc_rows}</table>

<div class="form-row">
  <input id="loc-name" placeholder="Location name" size="20">
  <input id="loc-lat" type="number" step="0.0001" placeholder="Latitude">
  <input id="loc-lon" type="number" step="0.0001" placeholder="Longitude">
  <button class="btn-add" onclick="add_location()">Save Location</button>
</div>

<h2>Location Reminders ({len(loc_reminders)})</h2>
<table><tr><th>ID</th><th>Location</th><th>Action</th><th>Triggered</th></tr>{locrem_rows}</table>

<div class="form-row">
  <input id="locrem-loc" placeholder="Location name" size="20">
  <input id="locrem-action" placeholder="What to remind" size="30">
  <button class="btn-add" onclick="add_loc_reminder()">Add Location Reminder</button>
</div>

<h2>GoClaw Cron Jobs (System Check-ins)</h2>
<div id="goclaw-crons">Loading...</div>

<h2>Agent Prompts & Knowledge</h2>
<div class="form-row">
  <select id="agent-select" onchange="loadAgentFiles()">
    <option value="">Select agent...</option>
  </select>
  <span id="agent-info" style="color:#888"></span>
</div>
<div id="agent-files"></div>

<script>
function show(msg, ok) {{
  const el = document.getElementById('msg');
  el.textContent = msg;
  el.style.display = 'block';
  el.style.background = ok ? '#27ae60' : '#e74c3c';
  setTimeout(() => el.style.display = 'none', 3000);
}}

async function del_reminder(id) {{
  const r = await fetch('/api/reminder/' + id, {{method:'DELETE'}});
  const j = await r.json();
  show(j.ok ? 'Deleted!' : 'Error', j.ok);
  if (j.ok) location.reload();
}}

async function add_reminder() {{
  const msg = document.getElementById('rem-msg').value;
  const min = parseInt(document.getElementById('rem-min').value);
  if (!msg || !min) {{ show('Fill message + minutes', false); return; }}
  const r = await fetch('/api/reminder', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{message:msg,in_minutes:min}})}});
  const j = await r.json();
  show(j.ok ? 'Reminder set for ' + j.fires_at : 'Error', j.ok);
  if (j.ok) location.reload();
}}

async function add_location() {{
  const name = document.getElementById('loc-name').value;
  const lat = parseFloat(document.getElementById('loc-lat').value);
  const lon = parseFloat(document.getElementById('loc-lon').value);
  if (!name || isNaN(lat) || isNaN(lon)) {{ show('Fill all fields', false); return; }}
  const r = await fetch('/api/location', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{name,lat,lon}})}});
  const j = await r.json();
  show(j.ok ? 'Location saved!' : 'Error', j.ok);
  if (j.ok) location.reload();
}}

async function add_loc_reminder() {{
  const loc = document.getElementById('locrem-loc').value;
  const action = document.getElementById('locrem-action').value;
  if (!loc || !action) {{ show('Fill all fields', false); return; }}
  const r = await fetch('/api/location-reminder', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{location:loc,action}})}});
  const j = await r.json();
  show(j.ok ? 'Location reminder added!' : 'Error', j.ok);
  if (j.ok) location.reload();
}}

// GoClaw Cron Management
async function loadGoclawCrons() {{
  const el = document.getElementById('goclaw-crons');
  try {{
    const r = await fetch('/api/goclaw-crons');
    const j = await r.json();
    if (!j.ok || !j.jobs.length) {{ el.innerHTML = '<p>No GoClaw cron jobs found.</p>'; return; }}

    let html = '<table><tr><th>Name</th><th>Schedule</th><th>Channel</th><th>Status</th><th>Message</th><th>Actions</th></tr>';
    for (const c of j.jobs) {{
      const sched = c.cron_expression || (c.interval_ms ? `every ${{c.interval_ms/60000}}m` : c.schedule_kind);
      const status = c.enabled ? '<span class="status ok">ON</span>' : '<span class="status warn">OFF</span>';
      const lastRun = c.last_run_at ? c.last_run_at.substring(0,16) : 'never';
      html += `<tr>
        <td>${{c.name}}</td>
        <td>${{sched}}</td>
        <td>${{c.deliver_channel}}</td>
        <td>${{status}}</td>
        <td>${{c.message.substring(0,50)}}${{c.message.length>50?'...':''}}</td>
        <td>
          <button onclick="toggleCron('${{c.id}}', ${{!c.enabled}})">${{c.enabled ? 'Disable' : 'Enable'}}</button>
          <button onclick="if(confirm('Delete ${{c.name}}?'))delCron('${{c.id}}')">Delete</button>
        </td>
      </tr>`;
    }}
    html += '</table>';
    html += `<p style="color:#888">${{j.count}} jobs total</p>`;
    el.innerHTML = html;
  }} catch(e) {{ el.innerHTML = '<p style="color:#e74c3c">Failed to load crons: ' + e.message + '</p>'; }}
}}

async function delCron(id) {{
  const r = await fetch('/api/goclaw-cron/' + id, {{method:'DELETE'}});
  const j = await r.json();
  show(j.ok ? 'Cron deleted!' : 'Error', j.ok);
  loadGoclawCrons();
}}

async function toggleCron(id, enabled) {{
  const r = await fetch('/api/goclaw-cron/' + id + '/toggle?enabled=' + enabled, {{method:'POST'}});
  const j = await r.json();
  show(j.ok ? (enabled ? 'Enabled!' : 'Disabled!') : 'Error', j.ok);
  loadGoclawCrons();
}}

// Agent Prompts Management
let agentsData = [];

async function loadAgents() {{
  const r = await fetch('/api/agents');
  const j = await r.json();
  agentsData = j.agents || [];
  const sel = document.getElementById('agent-select');
  for (const a of agentsData) {{
    const opt = document.createElement('option');
    opt.value = a.key;
    opt.textContent = `${{a.key}} (${{a.model}})`;
    sel.appendChild(opt);
  }}
}}

async function loadAgentFiles() {{
  const key = document.getElementById('agent-select').value;
  const el = document.getElementById('agent-files');
  const info = document.getElementById('agent-info');
  if (!key) {{ el.innerHTML = ''; info.textContent = ''; return; }}

  const agent = agentsData.find(a => a.key === key);
  info.textContent = agent ? `${{agent.provider}} / ${{agent.model}} / ${{agent.type}}` : '';

  const r = await fetch(`/api/agents/${{key}}/files`);
  const j = await r.json();
  if (!j.ok || !j.files.length) {{ el.innerHTML = '<p>No context files.</p>'; return; }}

  let html = '';
  for (const f of j.files) {{
    const id = `file-${{key}}-${{f.name.replace(/[^a-z0-9]/gi,'_')}}`;
    html += `<div style="margin:15px 0">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <strong style="color:#7c83ff">${{f.name}}</strong>
        <span style="color:#888">${{f.chars}} chars</span>
      </div>
      <textarea id="${{id}}" style="width:100%;height:200px;margin-top:5px;background:#0d1117;color:#e0e0e0;border:1px solid #333;border-radius:4px;padding:8px;font-family:monospace;font-size:12px;resize:vertical">${{f.content.replace(/</g,'&lt;')}}</textarea>
      <button class="btn-add" onclick="saveFile('${{key}}','${{f.name}}','${{id}}')" style="margin-top:5px">Save ${{f.name}}</button>
    </div>`;
  }}
  el.innerHTML = html;
}}

async function saveFile(agentKey, fileName, textareaId) {{
  const content = document.getElementById(textareaId).value;
  const r = await fetch(`/api/agents/${{agentKey}}/files/${{fileName}}`, {{
    method:'PUT', headers:{{'Content-Type':'application/json'}},
    body:JSON.stringify({{content}})
  }});
  const j = await r.json();
  show(j.ok ? `Saved ${{fileName}} (${{j.chars}} chars)` : 'Error saving', j.ok);
}}

// Cost display
async function loadCosts() {{
  try {{
    const r = await fetch('/api/openrouter-usage');
    const j = await r.json();
    if (j.ok) {{
      document.getElementById('cost-display').innerHTML = `
        <span>Total: <strong style="color:#00d4ff">\${{j.total}}</strong></span>
        <span>Today: <strong>\${{j.today}}</strong></span>
        <span>Week: <strong>\${{j.week}}</strong></span>
        <span>Month: <strong>\${{j.month}}</strong></span>
      `;
    }}
  }} catch(e) {{}}
}}

// Load on page open
loadCosts();
loadGoclawCrons();
loadAgents();
</script>
</body></html>"""


class GPSCheckRequest(BaseModel):
    lat: float
    lon: float
    user_id: Optional[str] = None
    chat_id: Optional[int] = None


@app.post("/api/check-gps")
async def check_gps(req: GPSCheckRequest):
    """Check current GPS against saved geofences.

    The AI agent calls this when user shares location.
    Returns any triggered notifications (enter/leave geofences).
    """
    import geofence_engine
    user_id = req.user_id or str(config.TELEGRAM_CHAT_ID)
    chat_id = req.chat_id or config.TELEGRAM_CHAT_ID

    notifications = geofence_engine.check_geofences(user_id, req.lat, req.lon)

    # Also send Telegram notifications directly
    if notifications:
        await notifier.notify_geofence(chat_id, notifications)

    return {
        "ok": True,
        "lat": req.lat,
        "lon": req.lon,
        "notifications": notifications,
        "count": len(notifications),
    }
