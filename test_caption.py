from datetime import datetime
import pytz
from generate_daily_report import KYIV_TZ, get_schedule_intervals, format_duration
# Just testing what plan_up_sec_now produces
now = datetime.now(KYIV_TZ)
slots = [True]*10 + [False]*10 + [True]*28
day_start = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=KYIV_TZ)

plan_up_sec_now = 0
for i, s in enumerate(slots):
    if s:
        slot_start = day_start + __import__('datetime').timedelta(minutes=30 * i)
        slot_end = slot_start + __import__('datetime').timedelta(minutes=30)
        if slot_end <= now:
            plan_up_sec_now += 1800
        elif slot_start < now:
            plan_up_sec_now += (now - slot_start).total_seconds()
print("Plan now sec:", plan_up_sec_now)
print("Plan now fmt:", format_duration(plan_up_sec_now))
