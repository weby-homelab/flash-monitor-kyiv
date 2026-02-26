import http.server
import socketserver
import threading
import time
import json
import os
import secrets
import datetime
from zoneinfo import ZoneInfo
import requests
import subprocess
from urllib.parse import urlparse, parse_qs
import sys
import re
from dotenv import load_dotenv

from parser_service import update_local_schedules

# Load environment variables
load_dotenv()

# --- Configuration ---
DATA_DIR = os.environ.get("DATA_DIR", ".")
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
PORT = 8889
# SECRET_KEY handled in state
STATE_FILE = os.path.join(DATA_DIR, "power_monitor_state.json")
SCHEDULE_FILE = os.path.join(DATA_DIR, "last_schedules.json")
HISTORY_FILE = os.path.join(DATA_DIR, "schedule_history.json")
EVENT_LOG_FILE = os.path.join(DATA_DIR, "event_log.json")
SCHEDULE_API_URL = os.environ.get("SCHEDULE_API_URL", "")
ALERTS_API_URL = "https://ubilling.net.ua/aerialalerts/"

def get_timezone():
    try:
        config_path = os.path.join(DATA_DIR, "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
            
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                cfg = json.load(f)
                tz_name = cfg.get("settings", {}).get("timezone", "Europe/Kyiv")
                return ZoneInfo(tz_name)
    except:
        pass
    return ZoneInfo("Europe/Kyiv")

KYIV_TZ = get_timezone()

# --- State Management ---
state = {
    "status": "unknown",  # up, down, unknown
    "last_seen": 0,
    "went_down_at": 0,
    "came_up_at": 0,
    "secret_key": None,
    "alert_status": "clear" # clear, active, region
}

state_lock = threading.RLock()

def trigger_daily_report_update():
    """
    Triggers the generation and update of the daily report chart.
    Runs asynchronously to not block the main thread.
    """
    def run_script():
        try:
            print("Triggering daily report update...")
            # Use absolute paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            python_exec = sys.executable
            script_path = os.path.join(base_dir, "generate_daily_report.py")
            
            # Run without --no-send so it updates Telegram
            subprocess.run([python_exec, script_path], check=True, cwd=base_dir)
            
            # Also trigger weekly report update
            trigger_weekly_report_update()
            
            # Trigger text report update - REMOVED, now handled in schedule_loop
            
        except Exception as e:
            print(f"Failed to trigger daily report: {e}")

    threading.Thread(target=run_script).start()

def trigger_text_report_update():
    """
    Triggers the generation and update of the text schedule report in Telegram.
    """
    def run_script():
        try:
            print("Triggering text report update...")
            base_dir = os.path.dirname(os.path.abspath(__file__))
            python_exec = sys.executable
            script_path = os.path.join(base_dir, "generate_text_report.py")
            subprocess.run([python_exec, script_path], check=True, cwd=base_dir)
        except Exception as e:
            print(f"Failed to trigger text report: {e}")

    threading.Thread(target=run_script).start()

def trigger_weekly_report_update():
    """
    Triggers the generation of the weekly report chart for the web.
    """
    def run_script():
        try:
            print("Triggering weekly report update...")
            base_dir = os.path.dirname(os.path.abspath(__file__))
            python_exec = sys.executable
            script_path = os.path.join(base_dir, "generate_weekly_report.py")
            output_path = os.path.join(DATA_DIR, "static", "weekly.png")
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            subprocess.run([python_exec, script_path, "--output", output_path], check=True, cwd=base_dir)
        except Exception as e:
            print(f"Failed to trigger weekly report: {e}")

    threading.Thread(target=run_script).start()

def log_event(event_type, timestamp):
    """
    Logs an event (up/down) to a JSON file for historical analysis.
    """
    try:
        entry = {
            "timestamp": timestamp,
            "event": event_type,
            "date_str": datetime.datetime.fromtimestamp(timestamp, KYIV_TZ).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Read existing logs or create new list
        logs = []
        if os.path.exists(EVENT_LOG_FILE):
            try:
                with open(EVENT_LOG_FILE, 'r') as f:
                    content = f.read().strip()
                    if content:
                        logs = json.loads(content)
                        if not isinstance(logs, list):
                            logs = []
            except (json.JSONDecodeError, FileNotFoundError):
                logs = []
            
        logs.append(entry)
        
        # Keep roughly last ~30 days (assuming ~20 events/day max = 600 events)
        if len(logs) > 1000: 
            logs = logs[-1000:]
            
        with open(EVENT_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
            
    except Exception as e:
        print(f"Failed to log event: {e}")

def load_state():
    global state
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                saved_state = json.load(f)
                state.update(saved_state)
        except Exception as e:
            print(f"Error loading state: {e}")
    
    if not state.get("secret_key"):
        state["secret_key"] = secrets.token_urlsafe(16)
        save_state()

def save_state():
    with state_lock:
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error saving state: {e}")

def get_current_time():
    # Returns local time timestamp
    return time.time()

def format_duration(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    parts = []
    if h > 0: parts.append(f"{h} г")
    if m > 0: parts.append(f"{m} хв")
    return " ".join(parts) if parts else "0 хв"

def get_next_scheduled_event(event_time, look_for_light):
    # look_for_light: True if we want to know when it will be ON, False for OFF
    try:
        if not os.path.exists(SCHEDULE_FILE): return None
        with open(SCHEDULE_FILE, 'r') as f: data = json.load(f)
        
        source = data.get('yasno') or data.get('github')
        if not source: return None
        
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
        
        now_dt = datetime.datetime.fromtimestamp(event_time, KYIV_TZ)
        today_str = now_dt.strftime("%Y-%m-%d")
        tomorrow_str = (now_dt + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        if today_str not in schedule_data: return None
        
        slots = list(schedule_data[today_str]['slots'])
        if tomorrow_str in schedule_data:
            slots.extend(schedule_data[tomorrow_str]['slots'])
        else:
            slots.extend([slots[-1]] * 48)
            
        current_slot_idx = (now_dt.hour * 2) + (1 if now_dt.minute >= 30 else 0)
        
        target_idx = -1
        
        # If the current scheduled state ALREADY matches look_for_light, 
        # we probably want the END of this block? No, we want the START of the NEXT block of this type.
        # But usually we want the nearest future transition to the target state.
        
        # Search for the first transition to look_for_light in the future
        for i in range(current_slot_idx, len(slots)):
            # A transition to look_for_light is when slots[i] == look_for_light
            # AND (i == 0 or slots[i-1] != look_for_light)
            if slots[i] == look_for_light:
                if i == 0 or slots[i-1] != look_for_light:
                    # Found the start of a block of the target type
                    # If this start is in the past or current slot, and we are currently in it,
                    # we should find the NEXT one.
                    if i <= current_slot_idx:
                        continue
                    target_idx = i
                    break
        
        # Fallback: if we are currently in a state that should be the target state 
        # (e.g. looking for LIGHT and it's scheduled to be LIGHT now),
        # then the "next transition to LIGHT" might be far away. 
        # But if the user wants "Expectation", maybe they mean the end of the CURRENT block?
        # Let's look at the user's example again.
        
        if target_idx == -1:
            # Try to find any occurrence if transition search failed
            for i in range(current_slot_idx + 1, len(slots)):
                if slots[i] == look_for_light:
                    target_idx = i
                    break
                    
        if target_idx == -1: return None
        
        # Find end of that block
        end_idx = len(slots)
        for i in range(target_idx + 1, len(slots)):
            if slots[i] != look_for_light:
                end_idx = i
                break
                
        def idx_to_hm(idx):
            rem = idx % 48
            h = rem // 2
            m = 30 if rem % 2 else 0
            return f"{h:02d}:{m:02d}"
            
        start_t = idx_to_hm(target_idx)
        end_t = idx_to_hm(end_idx)
        
        # Calculate time until start_t from event_time
        days_offset = target_idx // 48
        rem_idx = target_idx % 48
        target_dt = now_dt.replace(hour=rem_idx // 2, minute=(30 if rem_idx % 2 else 0), second=0, microsecond=0)
        target_dt += datetime.timedelta(days=days_offset)
        
        diff_sec = (target_dt - now_dt).total_seconds()
        if diff_sec < 0: diff_sec = 0
        
        return {
            "time_left_sec": diff_sec,
            "interval": f"{start_t}-{end_t}"
        }
    except Exception as e:
        print(f"Error in get_next_scheduled_event: {e}")
        return None

def format_event_message(is_up, event_time, prev_event_time):
    time_str = datetime.datetime.fromtimestamp(event_time, KYIV_TZ).strftime("%H:%M")
    
    if is_up:
        header = f"🟢 <b>{time_str} Світло з'явилося</b>"
        duration_prefix = "Не було"
        wait_prefix = "❌ Вимкнення через"
        look_for_light = False # Next we wait for OFF
    else:
        header = f"🔴 <b>{time_str} Світло зникло</b>"
        duration_prefix = "Воно було"
        wait_prefix = "💡 Очікуємо через"
        look_for_light = True # Next we wait for ON

    # 1. Deviation
    dev_msg = get_deviation_info(event_time, is_up)
    # get_deviation_info returns: "• Увімкнули пізніше на 10 хв"
    dev_line = ""
    if dev_msg:
        # Expected: "⚡️ На 10 хв пізніше графіка"
        m = re.search(r"(?:Увімкнули|Вимкнули)\s+(раніше|пізніше)\s+на\s+(.+)$", dev_msg)
        if m:
            timing = m.group(1)
            value = m.group(2)
            dev_line = f"⚡️ На {value} {timing} графіка"
        elif "точно за графіком" in dev_msg:
            dev_line = "⚡️ Точно за графіком"

    # 2. Previous Duration
    if prev_event_time > 0:
        dur_sec = abs(event_time - prev_event_time)
        dur_str = format_duration(dur_sec)
    else:
        dur_str = "невідомо"
    dur_line = f"🕓 {duration_prefix} {dur_str}"
    
    # 3. Next event and Interval
    next_info = get_next_scheduled_event(event_time, look_for_light)
    wait_line = ""
    interval_line = ""
    if next_info:
        wait_dur = format_duration(next_info["time_left_sec"])
        wait_line = f"{wait_prefix} ~ {wait_dur}"
        interval_line = f"🗓 ({next_info['interval']})"
        
    msg = f"{header}\n"
    if dev_line: msg += f"{dev_line}\n"
    msg += f"{dur_line}\n"
    if wait_line: msg += f"{wait_line},\n"
    if interval_line: msg += f"{interval_line}"
    
    return msg.strip()

def get_schedule_context():
    try:
        with open(SCHEDULE_FILE, 'r') as f:
            data = json.load(f)
        
        source = data.get('yasno') or data.get('github')
        if not source: return (None, None, "Невідомо", None)
        
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
        
        now = datetime.datetime.now(KYIV_TZ)
        today_str = now.strftime("%Y-%m-%d")
        tomorrow_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        if today_str not in schedule_data or not schedule_data[today_str].get('slots'):
            return (None, None, "Графік відсутній", None)
            
        # Combine today and tomorrow slots for a 48h view (96 slots)
        slots = list(schedule_data[today_str]['slots'])
        if tomorrow_str in schedule_data and schedule_data[tomorrow_str].get('slots'):
            slots.extend(schedule_data[tomorrow_str]['slots'])
        else:
            # If no tomorrow data, pad with the last state of today
            slots.extend([slots[-1]] * 48)
            
        current_slot_idx = (now.hour * 2) + (1 if now.minute >= 30 else 0)
        
        # True = Light, False = Outage
        is_light_now = slots[current_slot_idx]
        
        # Find end of current block (max 96 slots)
        end_idx = len(slots)
        for i in range(current_slot_idx + 1, len(slots)):
            if slots[i] != is_light_now:
                end_idx = i
                break
        
        # Format end time
        def format_idx_to_time(idx):
            if idx >= 96: return "час очікується"
            day_offset = idx // 48
            rem_idx = idx % 48
            h = rem_idx // 2
            m = 30 if rem_idx % 2 else 0
            
            if day_offset == 0:
                return f"{h:02d}:{m:02d}"
            elif day_offset == 1:
                if h == 0 and m == 0: return "24:00"
                return f"завтра о {h:02d}:{m:02d}"
            else:
                return "післязавтра"

        t_end = format_idx_to_time(end_idx)
        
        # Find next block range
        next_start_idx = end_idx
        next_duration = None
        
        if next_start_idx < len(slots):
            # If we need to show the range of the NEXT block
            # But the next block is in tomorrow and tomorrow is empty/padded
            if next_start_idx >= 48 and (tomorrow_str not in schedule_data or not schedule_data[tomorrow_str].get('slots')):
                next_range = "час очікується"
            else:
                next_end_idx = len(slots)
                for i in range(next_start_idx + 1, len(slots)):
                    if slots[i] == is_light_now:
                        next_end_idx = i
                        break
                
                ns_t = format_idx_to_time(next_start_idx)
                ne_t = format_idx_to_time(next_end_idx)
                next_range = f"{ns_t} - {ne_t}"
                
                # Calculate duration
                dur_h = (next_end_idx - next_start_idx) * 0.5
                next_duration = f"{dur_h:g}".replace('.', ',')
        else:
            next_range = "час очікується"
            
        return (is_light_now, t_end, next_range, next_duration)
            
    except Exception as e:
        print(f"Schedule error: {e}")
        return (None, None, "Помилка", None)

def send_telegram(message):
    # Mask token for logging
    token_masked = TOKEN[:5] + "..." + TOKEN[-5:] if TOKEN else "None"
    print(f"DEBUG: Sending telegram message to {CHAT_ID} via bot {token_masked}")
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        print(f"DEBUG: Telegram Response: {r.status_code} {r.text}")
        if r.status_code != 200:
            print(f"Telegram API Error: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def get_deviation_info(event_time, is_up):
    # event_time: timestamp (float)
    # is_up: True if light appeared, False if disappeared
    
    try:
        if not os.path.exists(SCHEDULE_FILE):
            return ""
            
        with open(SCHEDULE_FILE, 'r') as f:
            data = json.load(f)
        
        # Priority: Yasno -> Github
        source = data.get('yasno') or data.get('github')
        if not source: return ""
        
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
        
        # Localize event time
        dt = datetime.datetime.fromtimestamp(event_time, KYIV_TZ)
        date_str = dt.strftime("%Y-%m-%d")
        
        if date_str not in schedule_data or not schedule_data[date_str].get('slots'):
            return ""
            
        slots = schedule_data[date_str]['slots']
        
        # Find nearest transition of the target type
        best_diff = 9999
        
        for i in range(49):
            state_before = slots[i-1] if i > 0 else (not slots[0])
            state_after = slots[i] if i < 48 else slots[47] 
            
            if state_before != state_after:
                transition_type = 'up' if (not state_before and state_after) else 'down'
                
                expected_type = 'up' if is_up else 'down'
                if transition_type == expected_type:
                    trans_h = i // 2
                    trans_m = 30 if i % 2 else 0
                    
                    trans_dt = dt.replace(hour=trans_h, minute=trans_m, second=0, microsecond=0)
                    diff = (dt - trans_dt).total_seconds() / 60
                    
                    if abs(diff) < abs(best_diff):
                        best_diff = int(diff)

        if abs(best_diff) > 180:
            return ""

        abs_diff = abs(best_diff)
        h = abs_diff // 60
        m = abs_diff % 60
        
        dur_parts = []
        if h > 0:
            dur_parts.append(f"{h} год")
        if m > 0:
            dur_parts.append(f"{m} хв")
        
        dur_str = " ".join(dur_parts) if dur_parts else "0 хв"
        
        action = "Увімкнули" if is_up else "Вимкнули"
        timing = "пізніше" if best_diff > 0 else "раніше"
        
        if best_diff == 0:
            return f"• {action} точно за графіком"
            
        return f"• {action} {timing} на {dur_str}"

    except Exception as e:
        print(f"Error in deviation calc: {e}")
        return ""

def get_nearest_schedule_switch(event_time, target_is_up):
    """
    Finds the nearest scheduled switch time for the given event.
    target_is_up: True if we are looking for ON switch, False for OFF.
    Returns: Formatted time string "HH:MM" or None.
    """
    try:
        if not os.path.exists(SCHEDULE_FILE): return None
        with open(SCHEDULE_FILE, 'r') as f: data = json.load(f)
        
        source = data.get('yasno') or data.get('github')
        if not source: return None
        
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
        
        dt = datetime.datetime.fromtimestamp(event_time, KYIV_TZ)
        date_str = dt.strftime("%Y-%m-%d")
        
        if date_str not in schedule_data or not schedule_data[date_str].get('slots'):
            return None
            
        slots = schedule_data[date_str]['slots']
        
        best_diff = 9999
        best_time_str = None
        
        for i in range(49):
            state_before = slots[i-1] if i > 0 else slots[0]
            state_after = slots[i] if i < 48 else slots[47]
            if i == 0: state_before = not state_after
            
            if state_before != state_after:
                # Check if this transition matches our target
                # OFF->ON (Up) is state_after=True
                # ON->OFF (Down) is state_after=False
                is_up_switch = state_after
                
                if is_up_switch == target_is_up:
                    trans_h = i // 2
                    trans_m = 30 if i % 2 else 0
                    trans_dt = dt.replace(hour=trans_h, minute=trans_m, second=0, microsecond=0)
                    
                    diff = abs((dt - trans_dt).total_seconds())
                    if diff < best_diff:
                        best_diff = diff
                        best_time_str = f"{trans_h:02d}:{trans_m:02d}"
                        
        if best_diff > 10800: # If closest is more than 3 hours away, ignore
            return None
            
        return best_time_str
    except:
        return None



def get_air_raid_alert():
    try:
        r = requests.get(ALERTS_API_URL, timeout=5)
        if r.status_code == 200:
            data = r.json()
            alerts = data.get("states", {})
            is_alert_city = "м. Київ" in alerts and alerts["м. Київ"].get("alertnow", False)
            is_alert_region = "Київська область" in alerts and alerts["Київська область"].get("alertnow", False)
            
            if is_alert_city:
                status_text = "active"
                location = "м. Київ"
            elif is_alert_region:
                status_text = "region"
                location = "Київська область"
            else:
                status_text = "clear"
                location = "Тривоги немає"

            return {
                "city": is_alert_city,
                "region": is_alert_region,
                "status": status_text,
                "location": location
            }
    except Exception as e:
        print(f"Error fetching alerts: {e}")
    return {"status": "unknown", "location": "Невідомо"}

# --- Monitor Loop ---
def monitor_loop():
    print("Monitor loop started...")
    while True:
        time.sleep(60) # Check every minute
        
        # Reload state to sync with other workers/processes
        load_state()
        
        with state_lock:
            current_time = get_current_time()
            last_seen = state["last_seen"]
            status = state["status"]
            
            # Timeout threshold: 3 minutes (180 seconds)
            if status == "up" and (current_time - last_seen) > 180:
                # Timeout detected!
                state["status"] = "down"
                
                # Assume outage happened 1 min after last ping
                down_time_ts = last_seen + 60
                state["went_down_at"] = down_time_ts
                log_event("down", down_time_ts)
                
                # New compact message format
                msg = format_event_message(False, down_time_ts, state.get("came_up_at", 0))

                threading.Thread(target=send_telegram, args=(msg,)).start()
                save_state()

def alerts_loop():
    """
    Polls the air raid alert API every minute and sends Telegram notifications on status changes.
    """
    print("Alerts loop started...")
    while True:
        try:
            current_alert = get_air_raid_alert()
            new_status = current_alert.get("status")
            
            # Reload state to get latest alert_status
            load_state()
            
            with state_lock:
                old_status = state.get("alert_status", "clear")
                
                # We only care about "м. Київ" alerts for Telegram notifications
                # active = м. Київ, region = Київська область, clear = No alert
                
                if new_status != old_status:
                    time_str = datetime.datetime.now(KYIV_TZ).strftime("%H:%M")
                    
                    if new_status == "active":
                        msg = f"🔴 <b>{time_str} ПОВІТРЯНА ТРИВОГА! (м. Київ)</b>\n\n🏠 Будьте в укритті!"
                        threading.Thread(target=send_telegram, args=(msg,)).start()
                    elif old_status == "active" and new_status != "active":
                        msg = f"🟢 <b>{time_str} ВІДБІЙ ТРИВОГИ (м. Київ)</b>\n\n✅ Можна виходити з укриття."
                        threading.Thread(target=send_telegram, args=(msg,)).start()
                    
                    # Update state
                    state["alert_status"] = new_status
                    save_state()
                    
        except Exception as e:
            print(f"Error in alerts loop: {e}")
            
        time.sleep(60)

def sync_schedules():
    """
    Downloads schedule files from the primary project via HTTP.
    If sync fails or URL is not set, falls back to local parsing.
    """
    sync_success = False
    
    if SCHEDULE_API_URL:
        try:
            print(f"Syncing schedules from {SCHEDULE_API_URL}...")
            urls = {
                SCHEDULE_FILE: f"{SCHEDULE_API_URL}/last_schedules.json",
                HISTORY_FILE: f"{SCHEDULE_API_URL}/schedule_history.json"
            }
            for local_file, url in urls.items():
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with open(local_file, "wb") as f:
                        f.write(r.content)
            sync_success = True
            print("Schedules synced successfully.")
        except Exception as e:
            print(f"Failed to sync schedules from API: {e}")

    # Fallback to local parsing if remote sync failed or was skipped
    if not sync_success:
        print("Starting local schedule parsing...")
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        update_local_schedules(config_path, SCHEDULE_FILE)

def schedule_loop():
    """
    Periodically triggers report updates to keep charts and texts fresh.
    - Sync Schedules: every 10 mins
    - Daily Image: every 10 mins
    - Text Report: every 30 mins (handled inside main or by counter)
    - Weekly Telegram: Monday 00:15
    """
    print("Schedule loop started (10 min base interval)...")
    counter = 0
    weekly_sent_date = None
    
    while True:
        # 0. Sync schedules from external API
        sync_schedules()
        
        # 1. Trigger Daily Image Update (every 10 mins)
        try:
            trigger_daily_report_update()
        except: pass
        
        # 2. Trigger Text Report Update (every 30 mins)
        if counter % 3 == 0:
            try:
                trigger_text_report_update()
            except: pass
            
        # 3. Trigger Weekly Telegram Report (Monday around 00:10-00:20)
        now = datetime.datetime.now(KYIV_TZ)
        if now.weekday() == 0 and now.hour == 0 and 10 <= now.minute < 20:
            today_str = now.strftime("%Y-%m-%d")
            if weekly_sent_date != today_str:
                try:
                    print("Triggering weekly Telegram report...")
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    python_exec = sys.executable
                    script_path = os.path.join(base_dir, "generate_weekly_report.py")
                    yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                    subprocess.run([python_exec, script_path, "--date", yesterday], check=True, cwd=base_dir)
                    weekly_sent_date = today_str
                except Exception as e:
                    print(f"Failed to trigger weekly telegram report: {e}")
            
        counter += 1
        time.sleep(600) # 10 minutes

