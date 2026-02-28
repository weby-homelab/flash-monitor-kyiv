import json
from datetime import datetime
from zoneinfo import ZoneInfo

kyiv_tz = ZoneInfo("Europe/Kyiv")

# Current time for last_seen
now_ts = datetime.now(kyiv_tz).timestamp()

# Correct events for today based on user input
today_events = [
    {"timestamp": 1772150400.0, "event": "down", "date_str": "2026-02-27 02:00:00"},
    {"timestamp": 1772167200.0, "event": "up", "date_str": "2026-02-27 06:40:00"},
    {"timestamp": 1772188380.0, "event": "down", "date_str": "2026-02-27 12:33:00"}
]

with open('event_log.json', 'r') as f:
    logs = json.load(f)

# Filter out any existing Feb 27 events to avoid duplicates/errors
new_logs = [e for e in logs if not e['date_str'].startswith('2026-02-27')]
new_logs.extend(today_events)
new_logs.sort(key=lambda x: x['timestamp'])

with open('event_log.json', 'w') as f:
    json.dump(new_logs, f, indent=2)

# Update state to reflect current status (DOWN since 12:33)
state = {
    "status": "down",
    "last_seen": now_ts,
    "went_down_at": 1772188380.0,
    "came_up_at": 1772167200.0,
    "secret_key": "DjJWOrGLZ6fgOHYacE-ECg",
    "alert_status": "clear"
}

with open('power_monitor_state.json', 'w') as f:
    json.dump(state, f)

print("Logs and state updated successfully!")
