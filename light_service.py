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
import fcntl
import hashlib
from dotenv import load_dotenv

from parser_service import update_local_schedules

# Load environment variables
load_dotenv()

# --- Configuration ---
DATA_DIR = os.environ.get("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
ADMIN_CHAT_ID = "6313526220"
PORT = 8889
# SECRET_KEY handled in state
STATE_FILE = os.path.join(DATA_DIR, "power_monitor_state.json")
STATE_LOCK_FILE = os.path.join(DATA_DIR, "power_monitor_state.lock")
SCHEDULE_FILE = os.path.join(DATA_DIR, "last_schedules.json")

_process_locks = {}
_process_locks_lock = threading.Lock()

class FileLock:
    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        with _process_locks_lock:
            if self.file_path not in _process_locks:
                # Use 'a' to avoid truncating concurrent readers/writers unexpectedly, 
                # although it's just a lock file.
                f = open(self.file_path, 'a')
                _process_locks[self.file_path] = {'file': f, 'count': 0, 'thread_lock': threading.RLock()}
            lock_info = _process_locks[self.file_path]
            
        lock_info['thread_lock'].acquire()
        if lock_info['count'] == 0:
            fcntl.flock(lock_info['file'], fcntl.LOCK_EX)
        lock_info['count'] += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        lock_info = _process_locks[self.file_path]
        lock_info['count'] -= 1
        if lock_info['count'] == 0:
            fcntl.flock(lock_info['file'], fcntl.LOCK_UN)
        lock_info['thread_lock'].release()
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
    "alert_status": "clear", # clear, active, region
    "quiet_mode": "auto", # auto, forced_on, forced_off
    "quiet_status": "active", # active, quiet
    "pending_confirmation": False,
    "stability_start": time.time(),
    "admin_token": None,
    "last_schedule_hash": None
}

state_lock = threading.RLock()

def trigger_daily_report_update(is_final=False):
    """
    Triggers the generation and update of the daily report chart.
    Runs asynchronously to not block the main thread.
    """
    def run_script():
        try:
            print(f"Triggering daily report update (is_final={is_final})...")
            # Use absolute paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            python_exec = sys.executable
            script_path = os.path.join(base_dir, "generate_daily_report.py")
            
            # Run with --final if requested
            args = [python_exec, script_path]
            if is_final:
                args.append("--final")
            
            subprocess.run(args, check=True, cwd=base_dir)
            
            # Also trigger weekly report update
            trigger_weekly_report_update()
            
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
        
        with FileLock(STATE_LOCK_FILE):
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
                    pass
                
            logs.append(entry)
            if len(logs) > 1000: 
                logs = logs[-1000:]
                
            temp_file = EVENT_LOG_FILE + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(logs, f, indent=2)
            os.replace(temp_file, EVENT_LOG_FILE)
                
    except Exception as e:
        print(f"Failed to log event: {e}")

def load_state():
    global state
    with FileLock(STATE_LOCK_FILE):
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

    if not state.get("admin_token"):
        state["admin_token"] = secrets.token_urlsafe(16)
        save_state()

def save_state():
    with state_lock:
        with FileLock(STATE_LOCK_FILE):
            try:
                temp_file = STATE_FILE + '.tmp'
                with open(temp_file, 'w') as f:
                    json.dump(state, f)
                os.replace(temp_file, STATE_FILE)
            except Exception as e:
                print(f"Error saving state: {e}")

def get_current_time():
    # Returns local time timestamp
    return time.time()

def format_duration(seconds):
    d = int(seconds // 86400)
    h = int((seconds % 86400) // 3600)
    m = int((seconds % 3600) // 60)
    parts = []
    if d > 0:
        parts.append(f"{d}д")
        if h > 0: parts.append(f"{h} год")
    else:
        if h > 0: parts.append(f"{h} г")
    if m > 0: parts.append(f"{m} хв")
    return " ".join(parts) if parts else "0 хв"

def get_best_source_internal(data, date_str):
    """Internal helper to find source with slots or fallback to emergency."""
    best_source = None
    is_emergency = False
    for s_name in ['yasno', 'github']:
        src = data.get(s_name)
        if not src: continue
        group_key = list(src.keys())[0]
        day_data = src[group_key].get(date_str)
        if day_data:
            if day_data.get('slots'):
                return src, False
            if day_data.get('status') == 'emergency':
                is_emergency = True
                if not best_source: best_source = src
    return best_source, is_emergency

def get_next_scheduled_event(event_time, look_for_light):
    """
    Finds the next scheduled transition to the target state.
    look_for_light: True if looking for next ON, False for next OFF.
    """
    try:
        if not os.path.exists(SCHEDULE_FILE): return None
        with open(SCHEDULE_FILE, 'r') as f: data = json.load(f)
        
        now_dt = datetime.datetime.fromtimestamp(event_time, KYIV_TZ)
        today_str = now_dt.strftime("%Y-%m-%d")
        tomorrow_str = (now_dt + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        source, is_emergency = get_best_source_internal(data, today_str)
        if not source: return None
        
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
        
        if today_str not in schedule_data or not schedule_data[today_str].get('slots'):
            return None
        
        # Build 48-hour slot list
        slots = list(schedule_data[today_str]['slots'])
        tomorrow_data = schedule_data.get(tomorrow_str)
        if tomorrow_data and isinstance(tomorrow_data, dict) and tomorrow_data.get('slots'):
            slots.extend(tomorrow_data['slots'])
        else:
            slots.extend([slots[-1]] * 48)
            
        current_slot_idx = (now_dt.hour * 2) + (1 if now_dt.minute >= 30 else 0)
        
        target_idx = -1
        
        # Search for transition (prefer point where it *starts* being look_for_light)
        for i in range(current_slot_idx + 1, len(slots)):
            if slots[i] == look_for_light:
                # If we are currently in that state according to schedule, we look for NEXT block
                if i > 0 and slots[i-1] != look_for_light:
                    target_idx = i
                    break
        
        # Fallback search
        if target_idx == -1:
            if slots[current_slot_idx] != look_for_light:
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
        
        # Calculate time until start_t
        days_offset = target_idx // 48
        rem_idx = target_idx % 48
        
        target_dt = now_dt.replace(hour=rem_idx // 2, minute=(30 if rem_idx % 2 else 0), second=0, microsecond=0)
        if days_offset > 0: target_dt += datetime.timedelta(days=days_offset)
        
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
        wait_sec = next_info["time_left_sec"]
        if wait_sec < 60:
            wait_dur = "менше хвилини"
        else:
            wait_dur = format_duration(wait_sec)
        
        wait_line = f"{wait_prefix} ~ {wait_dur}"
        interval_line = f"🗓 ({next_info['interval']})"
    else:
        # Ensure fallback message is user-friendly.
        wait_line = f"{wait_prefix} час невідомий 🤷‍♂️"

    msg = f"{header}\n"
    if dev_line: msg += f"{dev_line}\n"
    msg += f"{dur_line}\n"
    
    msg += f"{wait_line}"
    if interval_line:
        msg += f",\n{interval_line}"
    
    return msg.strip()

def get_schedule_context():
    try:
        with open(SCHEDULE_FILE, 'r') as f:
            data = json.load(f)
        
        now = datetime.datetime.now(KYIV_TZ)
        today_str = now.strftime("%Y-%m-%d")
        tomorrow_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        source, is_emergency = get_best_source_internal(data, today_str)
        if not source: return (None, None, "Невідомо", None)
        
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
        
        if today_str not in schedule_data or not schedule_data[today_str].get('slots'):
            if is_emergency:
                return (None, None, "⚠️ Екстрені відключення", None)
            return (None, None, "Графік відсутній", None)
            
        # Combine today and tomorrow slots for a 48h view (96 slots)
        slots = list(schedule_data[today_str]['slots'])
        has_tomorrow = False
        if tomorrow_str in schedule_data and schedule_data[tomorrow_str].get('slots'):
            slots.extend(schedule_data[tomorrow_str]['slots'])
            has_tomorrow = True
        else:
            slots.extend([slots[-1]] * 48)
            
        current_slot_idx = (now.hour * 2) + (1 if now.minute >= 30 else 0)
        is_light_now = slots[current_slot_idx]
        
        # Find end of current block
        end_idx = len(slots)
        for i in range(current_slot_idx + 1, len(slots)):
            if slots[i] != is_light_now:
                end_idx = i
                break
        
        def format_idx_to_time(idx):
            if idx >= 96:
                return "відключення не плануються 🔆" if has_tomorrow else "час невідомий 🤷‍♂️"
            day_offset = idx // 48
            rem_idx = idx % 48
            h = rem_idx // 2
            m = 30 if rem_idx % 2 else 0
            if day_offset == 0: return f"{h:02d}:{m:02d}"
            elif day_offset == 1:
                if h == 0 and m == 0: return "24:00"
                return f"завтра о {h:02d}:{m:02d}"
            return "післязавтра"

        t_end = format_idx_to_time(end_idx)
        next_start_idx = end_idx
        next_duration = None
        
        if next_start_idx < len(slots):
            if next_start_idx >= 48 and not has_tomorrow:
                next_range = "час невідомий 🤷‍♂️"
            else:
                next_end_idx = len(slots)
                for i in range(next_start_idx + 1, len(slots)):
                    if slots[i] == is_light_now:
                        next_end_idx = i
                        break
                ns_t = format_idx_to_time(next_start_idx)
                ne_t = format_idx_to_time(next_end_idx)
                
                if next_start_idx >= 96 or (next_start_idx >= 48 and next_end_idx >= 96 and is_light_now):
                     next_range = "відключення не плануються 🔆" if has_tomorrow else "час невідомий 🤷‍♂️"
                else:
                     next_range = f"{ns_t} - {ne_t}"
                     
                dur_h = (next_end_idx - next_start_idx) * 0.5
                next_duration = f"{dur_h:g}".replace('.', ',')
        else:
            next_range = "відключення не плануються 🔆" if has_tomorrow else "час невідомий 🤷‍♂️"
            
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

def send_admin_confirmation(timestamp):
    msg = "⚠️ Зафіксовано втрату зв'язку! Режим 'Інформаційний спокій' активний. Це вимкнення світла чи збій обладнання?"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "🔴 Світло зникло", "callback_data": f"confirm_down_{timestamp}"},
                    {"text": "🟢 Збій / Роботи", "callback_data": f"ignore_down_{timestamp}"}
                ]
            ]
        }
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        print(f"DEBUG: Admin Confirmation Response: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Failed to send admin confirmation: {e}")

def get_deviation_info(event_time, is_up):
    # event_time: timestamp (float)
    # is_up: True if light appeared, False if disappeared
    
    try:
        if not os.path.exists(SCHEDULE_FILE): return ""
        with open(SCHEDULE_FILE, 'r') as f: data = json.load(f)
        
        dt = datetime.datetime.fromtimestamp(event_time, KYIV_TZ)
        date_str = dt.strftime("%Y-%m-%d")
        
        source, is_emergency = get_best_source_internal(data, date_str)
        if not source: return ""
        
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
        
        if date_str not in schedule_data or not schedule_data[date_str].get('slots'):
            return ""
            
        slots = schedule_data[date_str]['slots']
        
        best_diff = 9999
        for i in range(49):
            state_before = slots[i-1] if i > 0 else (not slots[0])
            state_after = slots[i] if i < 48 else slots[47] 
            if state_before != state_after:
                transition_type = 'up' if (not state_before and state_after) else 'down'
                expected_type = 'up' if is_up else 'down'
                if transition_type == expected_type:
                    trans_h, trans_m = i // 2, (30 if i % 2 else 0)
                    trans_dt = dt.replace(hour=trans_h, minute=trans_m, second=0, microsecond=0)
                    diff = (dt - trans_dt).total_seconds() / 60
                    if abs(diff) < abs(best_diff): best_diff = int(diff)

        if abs(best_diff) > 180: return ""
        abs_diff = abs(best_diff)
        h, m = abs_diff // 60, abs_diff % 60
        dur_parts = []
        if h > 0: dur_parts.append(f"{h} год")
        if m > 0: dur_parts.append(f"{m} хв")
        dur_str = " ".join(dur_parts) if dur_parts else "0 хв"
        action = "Увімкнули" if is_up else "Вимкнули"
        timing = "пізніше" if best_diff > 0 else "раніше"
        if best_diff == 0: return f"• {action} точно за графіком"
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
        dt = datetime.datetime.fromtimestamp(event_time, KYIV_TZ)
        date_str = dt.strftime("%Y-%m-%d")
        source, is_emergency = get_best_source_internal(data, date_str)
        if not source: return None
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
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
                if state_after == target_is_up:
                    trans_h, trans_m = i // 2, (30 if i % 2 else 0)
                    trans_dt = dt.replace(hour=trans_h, minute=trans_m, second=0, microsecond=0)
                    diff = abs((dt - trans_dt).total_seconds())
                    if diff < best_diff:
                        best_diff = diff
                        best_time_str = f"{trans_h:02d}:{trans_m:02d}"
        if best_diff > 10800: return None
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

                if state.get('quiet_status') == 'quiet':
                    state['pending_confirmation'] = True
                    threading.Thread(target=send_admin_confirmation, args=(down_time_ts,)).start()
                else:
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

            if new_status != "unknown":
                # Reload state to get latest alert_status
                load_state()

                with state_lock:
                    old_status = state.get("alert_status", "clear")

                    # We only care about "м. Київ" alerts for Telegram notifications
                    # active = м. Київ, region = Київська область, clear = No alert

                    if new_status != old_status:
                        time_str = datetime.datetime.now(KYIV_TZ).strftime("%H:%M")

                        if new_status == "active":
                            msg = f"⚠️ <b>{time_str} ПОВІТРЯНА ТРИВОГА! КИЇВ</b>"
                            threading.Thread(target=send_telegram, args=(msg,)).start()
                        elif old_status == "active" and new_status != "active":
                            msg = f"✅ <b>{time_str} ВІДБІЙ ТРИВОГИ</b>"
                            threading.Thread(target=send_telegram, args=(msg,)).start()

                        # Update state
                        state["alert_status"] = new_status
                        save_state()

        except Exception as e:            print(f"Error in alerts loop: {e}")
            
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
        result = update_local_schedules(config_path, SCHEDULE_FILE)
        
        has_changed = False
        if isinstance(result, tuple) and len(result) == 2:
            success, has_changed = result
            
        if has_changed:
            print("Schedule changes detected! Triggering report updates...")
            trigger_daily_report_update()
            trigger_weekly_report_update()
            
            # Send alert ONLY if there are planned outages in the new schedule
            should_alert = False
            try:
                if os.path.exists(SCHEDULE_FILE):
                    with open(SCHEDULE_FILE, 'r') as f:
                        data = json.load(f)
                    
                    # Check both github and yasno for any False slots
                    for s_key in ['github', 'yasno']:
                        sources = data.get(s_key, {})
                        for group_name, days in sources.items():
                            for date_str, day_data in days.items():
                                slots = day_data.get('slots')
                                if slots and any(s is False for s in slots):
                                    should_alert = True
                                    break
                            if should_alert: break
                        if should_alert: break
                    
                    # Deduplicate: Check if effective slots are the same as last alerted
                    if should_alert:
                        # Extract slots structure for hashing (Deduplication v2)
                        # We only care about days that actually have outages.
                        # This prevents alerts when a "pending" day becomes "all-light" (normal).
                        slots_structure = {}
                        for s_key in ['github', 'yasno']:
                            sources = data.get(s_key, {})
                            slots_structure[s_key] = {}
                            for group_name, days in sources.items():
                                day_slots = {}
                                for d, day_data in days.items():
                                    slots = day_data.get('slots')
                                    # Only include the day in hash if it has actual outages (at least one False)
                                    if slots and any(s is False for s in slots):
                                        day_slots[d] = slots
                                if day_slots:
                                    slots_structure[s_key][group_name] = day_slots
                        
                        current_hash = hashlib.md5(json.dumps(slots_structure, sort_keys=True).encode()).hexdigest()
                        last_hash = state.get("last_schedule_hash")
                        
                        with state_lock:
                            if current_hash == last_hash:
                                should_alert = False
                                print(f"Schedule changed in sources, but outages are identical (Hash: {current_hash}). Skipping Telegram alert.")
                            else:
                                print(f"Schedule changed: New Hash {current_hash} (was {last_hash}). Proceeding with alert.")
                                state["last_schedule_hash"] = current_hash
                                save_state()

            except Exception as e:
                print(f"Error checking for outages or deduplicating: {e}")
                should_alert = True # Fallback to alert if check fails

            if should_alert:
                send_telegram("⚠️ <b>Увага!</b>\n<b>Оновлено графіки відключень!</b>\nНові дані вже доступні в каналі та на сайті\n⚡️ FLASH.srvrs.top")
            else:
                print("Schedule updated but alert skipped (deduplicated or no outages).")

def check_quiet_mode_eligibility():
    """
    Checks if the system is eligible for Quiet Mode.
    Past 24 hours must have no 'down' events in event_log.json.
    Future 24 hours from now in last_schedules.json must have no 'False' slots.
    """
    now = time.time()
    cutoff_24h_ago = now - (24 * 3600)
    
    # 1. Check History (Past 24h)
    try:
        if os.path.exists(EVENT_LOG_FILE):
            with open(EVENT_LOG_FILE, 'r') as f:
                logs = json.load(f)
                if isinstance(logs, list):
                    for entry in logs:
                        if entry.get("event") == "down" and entry.get("timestamp", 0) >= cutoff_24h_ago:
                            print(f"Quiet Mode: Ineligible due to past outage at {entry.get('date_str')}")
                            return False
    except Exception as e:
        print(f"Error checking event log for quiet mode: {e}")
        return False

    # 2. Check Schedule (Future 24h)
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r') as f:
                data = json.load(f)
            
            now_dt = datetime.datetime.fromtimestamp(now, KYIV_TZ)
            today_str = now_dt.strftime("%Y-%m-%d")
            tomorrow_str = (now_dt + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            current_slot_idx = (now_dt.hour * 2) + (1 if now_dt.minute >= 30 else 0)
            
            found_outage = False
            for s_key in ['github', 'yasno']:
                sources = data.get(s_key, {})
                for group_name, days in sources.items():
                    # Construct a list of slots for today and tomorrow to look ahead 24h (48 slots)
                    all_slots = []
                    today_data = days.get(today_str)
                    if today_data and today_data.get('slots'):
                        all_slots.extend(today_data['slots'])
                    else:
                        all_slots.extend([True] * 48) # Assume light if no data
                        
                    tomorrow_data = days.get(tomorrow_str)
                    if tomorrow_data and tomorrow_data.get('slots'):
                        all_slots.extend(tomorrow_data['slots'])
                    else:
                        # If no tomorrow schedule yet, we only check until end of today
                        all_slots.extend([True] * 48)

                    # Check next 48 slots starting from current
                    look_ahead_limit = min(current_slot_idx + 48, len(all_slots))
                    for i in range(current_slot_idx, look_ahead_limit):
                        if all_slots[i] is False:
                            print(f"Quiet Mode: Ineligible due to planned outage in the next 24h in {s_key}/{group_name}")
                            found_outage = True
                            break
                    if found_outage: break
                if found_outage: break
            
            if found_outage:
                return False
        else:
            return False 
    except Exception as e:
        print(f"Error checking schedule for quiet mode: {e}")
        return False

    return True

def schedule_loop():
    """
    Periodically triggers report updates to keep charts and texts fresh.
    - Sync Schedules: every 10 mins
    - Daily Image: every 10 mins (plus special 00:01 final and 00:10 start)
    - Text Report: every 10 mins
    - Weekly Telegram: Monday 00:15
    """
    print("Schedule loop started (60 sec precision)...")
    weekly_sent_date = None
    
    while True:
        now = datetime.datetime.now(KYIV_TZ)
        hour = now.hour
        minute = now.minute

        # 1. Special Midnight Logic
        if hour == 0 and minute == 1:
            # Final summary for yesterday as a NEW message
            trigger_daily_report_update(is_final=True)
            time.sleep(65) # Avoid double trigger in the same minute
            continue
            
        if hour == 0 and minute == 10:
            # Start of today's monitoring
            trigger_daily_report_update(is_final=False)
            time.sleep(65)
            continue

        # 2. Regular 10-minute tasks (at 0, 10, 20, 30, 40, 50 minutes, except 00:10)
        if minute % 10 == 0:
            sync_schedules()
            trigger_daily_report_update(is_final=False)
            trigger_text_report_update()

            # Quiet Mode Logic (every 10 mins)
            with state_lock:
                q_mode = state.get("quiet_mode", "auto")
                old_status = state.get("quiet_status", "active")
                is_eligible = check_quiet_mode_eligibility()
                
                new_status = old_status
                if q_mode == "forced_on":
                    new_status = "quiet"
                elif q_mode == "forced_off":
                    new_status = "active"
                else: # auto
                    new_status = "quiet" if is_eligible else "active"
                
                if new_status != old_status:
                    state["quiet_status"] = new_status
                    if new_status == "quiet":
                        msg = "🔇 Система перейшла в режим інформаційного спокою"
                        state["stability_start"] = time.time()
                    else:
                        msg = "🔊 Увага! Виявлено зміни в графіку або фактичні відключення. Режим спокою вимкнено."
                        
                        # Trigger detailed text report generation
                        def trigger_report():
                            try:
                                base_dir = os.path.dirname(os.path.abspath(__file__))
                                python_exec = sys.executable
                                script_path = os.path.join(base_dir, "generate_text_report.py")
                                # Wait a bit for state to save and then run
                                time.sleep(2)
                                subprocess.run([python_exec, script_path, "--force-new"], check=True, cwd=base_dir)
                            except Exception as e:
                                print(f"Failed to trigger text report after quiet mode exit: {e}")
                        
                        threading.Thread(target=trigger_report).start()
                    
                    threading.Thread(target=send_telegram, args=(msg,)).start()
                    save_state()
            
        # 3. Weekly Telegram Report (Monday around 00:15)
        if now.weekday() == 0 and hour == 0 and 15 <= minute < 25:
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
            
        time.sleep(60)

