from light_service import get_next_scheduled_event
import datetime
from zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")

def debug_search():
    event_time = datetime.datetime(2026, 3, 5, 19, 29, 0, tzinfo=KYIV_TZ)
    current_slot_idx = (event_time.hour * 2) + (1 if event_time.minute >= 30 else 0)
    print("current_slot_idx:", current_slot_idx)
    
    slots = [True]*33 + [False]*7 + [True]*8
    look_for_light = False
    target_idx = -1
    
    # Logic from the file
    for i in range(current_slot_idx + 1, len(slots)):
        if slots[i] == look_for_light:
            # If we are currently in that state according to schedule, we look for NEXT block
            if i > 0 and slots[i-1] != look_for_light:
                print("Found transition at", i)
                target_idx = i
                break
                
    if target_idx == -1:
        for i in range(current_slot_idx + 1, len(slots)):
            if slots[i] == look_for_light:
                print("Found fallback at", i)
                target_idx = i
                break
    
    print("target_idx:", target_idx)
    
debug_search()
