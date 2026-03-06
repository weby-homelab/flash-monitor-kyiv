import datetime
from zoneinfo import ZoneInfo
import json
import os
import light_service
from light_service import get_next_scheduled_event

KYIV_TZ = ZoneInfo("Europe/Kyiv")

# Mock the schedule file
schedule_data = {
    "github": {
        "GPV36.1": {
            "2026-03-05": {
                "slots": [True]*33 + [False]*7 + [True]*8
            }
        }
    }
}
# 33 slots of True = 16.5 hours (00:00 to 16:30)
# 7 slots of False = 3.5 hours (16:30 to 20:00)
# 8 slots of True = 4 hours (20:00 to 24:00)

os.makedirs("data", exist_ok=True)
with open("data/last_schedules.json", "w") as f:
    json.dump(schedule_data, f)

light_service.SCHEDULE_FILE = "data/last_schedules.json"

event_time = datetime.datetime(2026, 3, 5, 19, 29, 0, tzinfo=KYIV_TZ).timestamp()
look_for_light = False # We got light, now we look for next outage

res = get_next_scheduled_event(event_time, look_for_light)
print("Result for 19:29 looking for outage (False):", res)

event_time2 = datetime.datetime(2026, 3, 5, 19, 31, 0, tzinfo=KYIV_TZ).timestamp()
res2 = get_next_scheduled_event(event_time2, look_for_light)
print("Result for 19:31 looking for outage (False):", res2)

