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
            }
        }
    }
}
os.makedirs("data", exist_ok=True)
with open("data/last_schedules.json", "w") as f:
    json.dump(schedule_data, f)
light_service.SCHEDULE_FILE = "data/last_schedules.json"

def debug_slots():
    # Print the slots around 19:30 to see what the indices evaluate to
    now_dt = datetime.datetime(2026, 3, 5, 19, 29, 0, tzinfo=KYIV_TZ)
    current_slot_idx = (now_dt.hour * 2) + (1 if now_dt.minute >= 30 else 0)
    print(f"Current slot idx for 19:29: {current_slot_idx} (Time block: {current_slot_idx//2}:{['00', '30'][current_slot_idx%2]})")
    
    slots = [True]*33 + [False]*7 + [True]*8
    print(f"Slot at idx {current_slot_idx} is: {slots[current_slot_idx]}")
    
    for i in range(35, 42):
        print(f"Slot {i} ({i//2}:{['00', '30'][i%2]}): {slots[i]}")

debug_slots()
