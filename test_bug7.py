import datetime
from zoneinfo import ZoneInfo
import json
import os
import light_service
from light_service import get_next_scheduled_event

KYIV_TZ = ZoneInfo("Europe/Kyiv")

schedule_data = {
    "github": {
        "GPV36.1": {
            "2026-03-05": {
                "slots": [True]*33 + [False]*7 + [True]*8
            },
            "2026-03-06": {
                "slots": [True]*48
            }
        }
    }
}
os.makedirs("data", exist_ok=True)
with open("data/last_schedules.json", "w") as f:
    json.dump(schedule_data, f)
light_service.SCHEDULE_FILE = "data/last_schedules.json"

event_time = datetime.datetime(2026, 3, 5, 19, 29, 0, tzinfo=KYIV_TZ).timestamp()
res = get_next_scheduled_event(event_time, look_for_light=False)
print("Result for 19:29 looking for outage (False):", res)

event_time_2 = datetime.datetime(2026, 3, 5, 16, 29, 0, tzinfo=KYIV_TZ).timestamp()
res_2 = get_next_scheduled_event(event_time_2, look_for_light=False)
print("Result for 16:29 looking for outage (False):", res_2)

