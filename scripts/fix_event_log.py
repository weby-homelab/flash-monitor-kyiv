import json

with open("data/event_log.json", "r") as f:
    events = json.load(f)

# The false events are:
# "timestamp": 1775079812.2974017, "event": "down", "date_str": "2026-04-02 00:43:32"
# "timestamp": 1775145422.0326595, "event": "up", "date_str": "2026-04-02 18:57:02"

new_events = [e for e in events if e.get("date_str") not in ("2026-04-02 00:43:32", "2026-04-02 18:57:02")]

with open("data/event_log.json", "w") as f:
    json.dump(new_events, f, indent=2)

print("Fixed event_log.json")
