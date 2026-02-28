import json
import time
import os
import datetime
from zoneinfo import ZoneInfo
import sys

# Support custom data directory via args, otherwise local
DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "/root/geminicli/flash-monitor-kyiv"
EVENT_FILE = os.path.join(DATA_DIR, "event_log.json")
STATE_FILE = os.path.join(DATA_DIR, "power_monitor_state.json")
LOCK_FILE = os.path.join(DATA_DIR, "power_monitor_state.lock")

# Read current events
if os.path.exists(EVENT_FILE):
    with open(EVENT_FILE, "r") as f:
        events = json.load(f)
else:
    events = []

# Filter out today's events (keep everything before 2026-02-27)
events = [e for e in events if not str(e.get("date_str", "")).startswith("2026-02-27")]

tz = ZoneInfo("Europe/Kyiv")
base_date = "2026-02-27"

def add_event(time_str, event_type):
    dt = datetime.datetime.strptime(f"{base_date} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=tz)
    events.append({
        "timestamp": dt.timestamp(),
        "event": event_type,
        "date_str": f"{base_date} {time_str}"
    })

# Add real events
add_event("02:02:00", "down")
add_event("06:40:00", "up")
add_event("12:33:00", "down")
add_event("16:23:00", "up")

with open(EVENT_FILE, "w") as f:
    json.dump(events, f, indent=2)

print("Updated events:")
for e in events[-5:]:
    print(e)

# Update state
with open(STATE_FILE, "r") as f:
    state = json.load(f)

state["status"] = "up"
state["went_down_at"] = events[-2]["timestamp"]
state["came_up_at"] = events[-1]["timestamp"]
# keep last_seen recent so monitor_loop doesn't trigger "down"
state["last_seen"] = time.time() 
state["alert_status"] = "clear"

with open(STATE_FILE, "w") as f:
    json.dump(state, f)

print(f"Updated state: status={state['status']}, came_up={datetime.datetime.fromtimestamp(state['came_up_at'], tz).strftime('%H:%M:%S')}")
