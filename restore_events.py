import json
import datetime
from zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")

with open('schedule_history.json', 'r') as f:
    history = json.load(f)

with open('event_log.json', 'r') as f:
    existing_events = json.load(f)

days_to_process = ['2026-02-23', '2026-02-24', '2026-02-25']
new_events = []

# To track transitions correctly across day boundaries
# We know 2026-02-22 ended with true
last_state = True

for day_str in days_to_process:
    slots = history.get(day_str)
    if not slots:
        continue
    
    date_obj = datetime.datetime.strptime(day_str, "%Y-%m-%d").date()
    
    for i, state in enumerate(slots):
        if state != last_state:
            # Transition occurred
            event_type = 'up' if state else 'down'
            h = i // 2
            m = 30 if i % 2 else 0
            
            dt = datetime.datetime.combine(date_obj, datetime.time(hour=h, minute=m), tzinfo=KYIV_TZ)
            timestamp = dt.timestamp()
            date_str_fmt = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            new_events.append({
                "timestamp": timestamp,
                "event": event_type,
                "date_str": date_str_fmt
            })
            last_state = state

# Combine and sort
all_events = new_events + existing_events
all_events.sort(key=lambda x: x['timestamp'])

with open('event_log.json', 'w') as f:
    json.dump(all_events, f, indent=2)

print(f"Successfully recovered {len(new_events)} events. Total events: {len(all_events)}")
for e in new_events:
    print(f"  {e['date_str']} - {e['event']}")
