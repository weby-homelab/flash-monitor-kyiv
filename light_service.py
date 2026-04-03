import http.server
import socketserver
import threading
import time
import json
import asyncio
import aiofiles
from models import AppConfig, AppState
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
def get_config():
    try:
        config_path = os.path.join(DATA_DIR, "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
            
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                try:
                    return AppConfig(**data) .model_dump(exclude_unset=False, by_alias=True)
                except Exception as e:
                    print(f"Config validation error: {e}")
                    return data
    except:
        pass
    return AppConfig() .model_dump()

def get_admin_chat_id():
    cfg = get_config()
    return str(cfg.get("settings", {}).get("admin_chat_id", "6313526220"))

def get_safety_net_timeout():
    cfg = get_config()
    return int(cfg.get("settings", {}).get("safety_net_timeout", 35))

def get_push_interval():
    cfg = get_config()
    return int(cfg.get("settings", {}).get("push_interval", 30))

def create_backup(label="manual"):
    """Creates a backup of the current configuration and state."""
    backup_dir = os.path.join(DATA_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now(KYIV_TZ).strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}_{label}.json"
    backup_path = os.path.join(backup_dir, backup_name)
    
    config = get_config()
    # We also include state for safety
    state_copy = {}
    state_path = os.path.join(DATA_DIR, "power_monitor_state.json")
    if os.path.exists(state_path):
        try:
            with open(state_path, 'r') as f: state_copy = json.load(f)
        except: pass
        
    backup_data = {
        "timestamp": time.time(),
        "date_str": datetime.datetime.now(KYIV_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "label": label,
        "config": config,
        "state": state_copy
    }
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    # Cleanup old backups (keep last 10)
    try:
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("backup_") and f.endswith(".json")])
        if len(backups) > 10:
            for b in backups[:-10]:
                os.remove(os.path.join(backup_dir, b))
    except: pass
    
    return backup_name

def list_backups():
    backup_dir = os.path.join(DATA_DIR, "backups")
    if not os.path.exists(backup_dir): return []
    res = []
    for f in sorted(os.listdir(backup_dir), reverse=True):
        if f.startswith("backup_") and f.endswith(".json"):
            path = os.path.join(backup_dir, f)
            try:
                with open(path, 'r') as b:
                    data = json.load(b)
                    res.append({
                        "filename": f,
                        "date": data.get("date_str"),
                        "label": data.get("label", "unknown")
                    })
            except: pass
    return res

def restore_backup(filename):
    backup_path = os.path.join(DATA_DIR, "backups", filename)
    if not os.path.exists(backup_path): return False, "Backup not found"
    
    try:
        with open(backup_path, 'r') as f:
            data = json.load(f)
            
        # 1. Backup current config as "pre_restore" just in case
        create_backup("pre_restore")
        
        # 2. Restore config
        config_path = os.path.join(DATA_DIR, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data["config"], f, ensure_ascii=False, indent=2)
            
        # 3. Restore state if available
        if "state" in data:
            state_path = os.path.join(DATA_DIR, "power_monitor_state.json")
            with open(state_path, 'w', encoding='utf-8') as f:
                json.dump(data["state"], f, ensure_ascii=False, indent=2)
        
        return True, "Success"
    except Exception as e:
        return False, str(e)

def prune_old_data():
    """Removes old events and schedule history based on retention settings."""
    try:
        cfg = get_config()
        retention = cfg.get("advanced", {}).get("retention", {})
        log_days = retention.get("event_log_days", 30)
        sched_days = retention.get("schedule_history_days", 14)
        
        now = time.time()
        
        # 1. Prune event_log.json
        if os.path.exists(EVENT_LOG_FILE):
            cutoff = now - (log_days * 86400)
            with open(EVENT_LOG_FILE, 'r') as f:
                logs = json.load(f)
            new_logs = [l for l in logs if l.get('timestamp', 0) > cutoff]
            if len(new_logs) < len(logs):
                with open(EVENT_LOG_FILE, 'w') as f:
                    json.dump(new_logs, f, indent=2)
                print(f"Pruned {len(logs) - len(new_logs)} old events.")

        # 2. Prune schedule_history.json
        if os.path.exists(HISTORY_FILE):
            cutoff_date = (datetime.datetime.now(KYIV_TZ) - datetime.timedelta(days=sched_days)).strftime("%Y-%m-%d")
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
            new_history = {d: v for d, v in history.items() if d >= cutoff_date}
            if len(new_history) < len(history):
                with open(HISTORY_FILE, 'w') as f:
                    json.dump(new_history, f, indent=2)
                print(f"Pruned {len(history) - len(new_history)} old schedule records.")
    except Exception as e:
        print(f"Error during data pruning: {e}")

def get_advanced_setting(section, key, default=None):
    cfg = get_config()
    val = cfg.get("advanced", {}).get(section, {}).get(key, default)
    if isinstance(default, bool) and isinstance(val, str):
        if val.lower() in ("false", "0", "no"): return False
        if val.lower() in ("true", "1", "yes"): return True
    return val

def get_telegram_token():
    cfg = get_config()
    return cfg.get("settings", {}).get("telegram_bot_token") or os.environ.get("TELEGRAM_BOT_TOKEN")

def get_telegram_channel_id_cfg():
    cfg = get_config()
    return cfg.get("settings", {}).get("telegram_channel_id") or os.environ.get("TELEGRAM_CHANNEL_ID")

TOKEN = get_telegram_token()
CHAT_ID = get_telegram_channel_id_cfg()
ADMIN_CHAT_ID = get_admin_chat_id()
PORT = 8889
# SECRET_KEY handled in state
STATE_FILE = os.path.join(DATA_DIR, "power_monitor_state.json")
STATE_LOCK_FILE = os.path.join(DATA_DIR, "power_monitor_state.lock")
SCHEDULE_FILE = os.path.join(DATA_DIR, "last_schedules.json")


class SafeStateContextAsync:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._counter = 0
        self._owner = None
        self._flock_file = None
        self.file_lock_path = STATE_LOCK_FILE

    async def __aenter__(self):
        task = asyncio.current_task()
        if self._owner == task:
            self._counter += 1
            return self
            
        await self._lock.acquire()
        self._owner = task
        self._counter = 1
        try:
            def _acquire():
                self._flock_file = open(self.file_lock_path, 'a')
                fcntl.flock(self._flock_file, fcntl.LOCK_EX)
            await asyncio.to_thread(_acquire)
        except Exception as e:
            print(f"Error acquiring file lock: {e}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._owner != asyncio.current_task():
            return
            
        if self._counter > 1:
            self._counter -= 1
            return
            
        try:
            if self._flock_file:
                def _release():
                    try:
                        fcntl.flock(self._flock_file, fcntl.LOCK_UN)
                        self._flock_file.close()
                    except:
                        pass
                await asyncio.to_thread(_release)
                self._flock_file = None
        finally:
            self._counter = 0
            self._owner = None
            self._lock.release()

state_mgr = SafeStateContextAsync()

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
    "safety_net_pending": False, # New: tracking safety net message
    "safety_net_sent_at": 0,    # New: tracking when safety net was sent
    "safety_net_triggered_for": 0, # New: tracking last_seen to avoid re-triggering
    "muted_until": 0,            # New: for "Technical Failure" mute
    "stability_start": time.time(),
    "admin_token": None,
    "last_schedule_hash": None
}

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

async def log_event(event_type, timestamp):
    """
    Logs an event (up/down) to a JSON file for historical analysis.
    """
    try:
        entry = {
            "timestamp": timestamp,
            "event": event_type,
            "date_str": datetime.datetime.fromtimestamp(timestamp, KYIV_TZ).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        async with state_mgr:
            logs = []
            if os.path.exists(EVENT_LOG_FILE):
                try:
                    async with aiofiles.open(EVENT_LOG_FILE, 'r') as f:
                        file_content = (await f.read()).strip()
                        if file_content:
                            logs = json.loads(file_content)
                            if not isinstance(logs, list):
                                logs = []
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
                
            logs.append(entry)
            if len(logs) > 1000: 
                logs = logs[-1000:]
                
            temp_file = EVENT_LOG_FILE + '.tmp'
            async with aiofiles.open(temp_file, 'w') as f:
                await f.write(json.dumps(logs, indent=2))
            
            def _replace():
                os.replace(temp_file, EVENT_LOG_FILE)
            await asyncio.to_thread(_replace)
                
    except Exception as e:
        print(f"Failed to log event: {e}")

async def load_state():
    global state
    async with state_mgr:
        if os.path.exists(STATE_FILE):
            try:
                async with aiofiles.open(STATE_FILE, 'r') as f:
                    file_content = await f.read()
                    saved_state = json.loads(file_content)
                    state.update(saved_state)
            except Exception as e:
                print(f"Error loading state: {e}")
                
        try:
            validated_state = AppState(**state) .model_dump(exclude_unset=False)
            state.update(validated_state)
        except Exception as e:
            print(f"State validation error: {e}")

    if not state.get("secret_key"):
        async with state_mgr:
            state["secret_key"] = secrets.token_urlsafe(16)
            await save_state()

    if not state.get("admin_token"):
        async with state_mgr:
            state["admin_token"] = secrets.token_urlsafe(16)
            await save_state()

async def save_state():
    async with state_mgr:
        try:
            temp_file = STATE_FILE + '.tmp'
            async with aiofiles.open(temp_file, 'w') as f:
                await f.write(json.dumps(state))
            def _replace():
                os.replace(temp_file, STATE_FILE)
            await asyncio.to_thread(_replace)
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
    cfg = get_config()
    priority_order = ['yasno', 'github']
    user_priority = cfg.get("advanced", {}).get("data_sources", {}).get("priority", "yasno")
    
    if user_priority in ['yasno', 'github']:
        priority_order = [user_priority] + [s for s in priority_order if s != user_priority]
    elif user_priority == 'custom':
        priority_order = ['custom', 'yasno', 'github']

    best_source = None
    is_emergency = False
    
    # 1. Pass: check for any emergency status in any source
    for s_name in priority_order:
        src = data.get(s_name)
        if not src: continue
        group_keys = list(src.keys())
        if not group_keys: continue
        group_key = group_keys[0]
        day_data = src[group_key].get(date_str)
        if day_data and day_data.get('status') == 'emergency':
            is_emergency = True
            if not best_source: best_source = src

    # 2. Pass: prioritize sources with actual slots
    for s_name in priority_order:
        src = data.get(s_name)
        if not src: continue
        group_keys = list(src.keys())
        if not group_keys: continue
        group_key = group_keys[0]
        day_data = src[group_key].get(date_str)
        if day_data and day_data.get('slots'):
            return src, is_emergency
            
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
    cfg = get_config()
    txt = cfg.get("ui", {}).get("text", {})
    
    if is_up:
        header = txt.get("event_up", "🟢 <b>{time} Світло з'явилося</b>").format(time=time_str)
        duration_prefix = txt.get("dur_prefix_up", "Не було")
        wait_prefix = txt.get("next_prefix_down", "❌ Вимкнення через")
        look_for_light = False # Next we wait for OFF
    else:
        header = txt.get("event_down", "🔴 <b>{time} Світло зникло</b>").format(time=time_str)
        duration_prefix = txt.get("dur_prefix_down", "Воно було")
        wait_prefix = txt.get("next_prefix_up", "💡 Очікуємо через")
        look_for_light = True # Next we wait for ON

    # 1. Deviation
    dev_msg = get_deviation_info(event_time, is_up)
    dev_line = ""
    if dev_msg:
        m = re.search(r"(?:Увімкнули|Вимкнули)\s+(раніше|пізніше)\s+на\s+(.+)$", dev_msg)
        if m:
            timing = m.group(1)
            value = m.group(2)
            dev_line = txt.get("dev_shift", "⚡️ На {value} {timing} графіка").format(value=value, timing=timing)
        elif "точно за графіком" in dev_msg:
            dev_line = txt.get("dev_exact", "⚡️ Точно за графіком")

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
        if not source: return (None, None, "Невідомо", None, False)
        
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
        
        if today_str not in schedule_data or not schedule_data[today_str].get('slots'):
            if is_emergency:
                return (None, None, "⚠️ Екстрені відключення", None, True)
            return (None, None, "Графік відсутній", None, False)
            
        slots = list(schedule_data[today_str]['slots'])
        has_tomorrow = False
        if tomorrow_str in schedule_data and schedule_data[tomorrow_str].get('slots'):
            slots.extend(schedule_data[tomorrow_str]['slots'])
            has_tomorrow = True
        else:
            slots.extend([slots[-1]] * 48)
            
        current_slot_idx = (now.hour * 2) + (1 if now.minute >= 30 else 0)
        is_light_now = slots[current_slot_idx]
        
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
            
        return (is_light_now, t_end, next_range, next_duration, is_emergency)
    except Exception as e:
        print(f"Schedule error: {e}")
        return (None, None, "Помилка", None, False)

def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("Telegram configuration missing (TOKEN or CHAT_ID)")
        return
    token_masked = TOKEN[:5] + "..." + TOKEN[-5:]
    print(f"DEBUG: Sending telegram message to {CHAT_ID} via bot {token_masked}")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=5)
        if r.status_code != 200:
            err_msg = r.text.replace(TOKEN, "[REDACTED_TOKEN]")
            print(f"Telegram API Error (Status {r.status_code}): {err_msg}")
    except Exception as e:
        err_str = str(e).replace(TOKEN, "[REDACTED_TOKEN]")
        print(f"Failed to send Telegram message: {err_str}")

def send_admin_confirmation(timestamp):
    msg = "⚠️ Зафіксовано втрату зв'язку! Режим 'Інформаційний спокій' активний. Це вимкнення світла чи збій обладнання?"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": get_admin_chat_id(),
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[{"text": "🔴 Світло зникло", "callback_data": f"confirm_down_{timestamp}"},
                                 {"text": "🟢 Збій / Роботи", "callback_data": f"ignore_down_{timestamp}"}]]
        }
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send admin confirmation: {e}")

def send_safety_net_admin(timestamp):
    msg = "🚨 <b>SAFETY NET: ВТРАТА ПУША!</b>\n\nВже 35 сек немає зв'язку. Що сталося?"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": get_admin_chat_id(),
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🔴 Світло зникло?", "callback_data": f"sn_down_{timestamp}"},
                 {"text": "🛠 Технічний збій?", "callback_data": f"sn_tech_{timestamp}"}],
                [{"text": "🤷‍♂️ Не знаю!", "callback_data": f"sn_dontknow_{timestamp}"}]
            ]
        }
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send safety net admin: {e}")

def get_deviation_info(event_time, is_up):
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
            status_text = "active" if is_alert_city else ("region" if is_alert_region else "clear")
            location = "м. Київ" if is_alert_city else ("Київська область" if is_alert_region else "Тривоги немає")
            return {"city": is_alert_city, "region": is_alert_region, "status": status_text, "location": location}
    except Exception as e:
        print(f"Error fetching alerts: {e}")
    return {"status": "unknown", "location": "Невідомо"}

async def update_quiet_status():
    async with state_mgr:
        q_mode = state.get("quiet_mode", "auto")
        old_status = state.get("quiet_status", "active")
        is_eligible = check_quiet_mode_eligibility()
        new_status = "quiet" if q_mode == "forced_on" else ("active" if q_mode == "forced_off" else ("quiet" if is_eligible else "active"))
        if new_status != old_status:
            state["quiet_status"] = new_status
            if new_status == "quiet":
                state["stability_start"] = time.time()
                # CLEANUP: When entering quiet mode, remove active reports from channel
                print("Entering Quiet Mode. Cleaning up active reports...")
                def run_cleanup():
                    try:
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        python_exec = sys.executable
                        subprocess.run([python_exec, os.path.join(base_dir, "generate_daily_report.py"), "--cleanup"], cwd=base_dir)
                        subprocess.run([python_exec, os.path.join(base_dir, "generate_text_report.py"), "--cleanup"], cwd=base_dir)
                    except: pass
                threading.Thread(target=run_cleanup).start()
            else:
                def trigger_report():
                    try:
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        python_exec = sys.executable
                        script_path = os.path.join(base_dir, "generate_text_report.py")
                        time.sleep(2)
                        subprocess.run([python_exec, script_path, "--force-new"], check=True, cwd=base_dir)
                    except Exception as e:
                        print(f"Failed to trigger text report: {e}")
                threading.Thread(target=trigger_report).start()
            await save_state()
            print(f"Quiet mode status updated to: {new_status}")

async def monitor_loop():
    print("Monitor loop started...")
    while True:
        await asyncio.sleep(5)
        await load_state()
        async with state_mgr:
            current_time = get_current_time()
            last_seen = state["last_seen"]
            status = state["status"]
            if state.get("muted_until", 0) > current_time: continue
            safety_net_timeout = get_safety_net_timeout()
            if status == "up" and (current_time - last_seen) > safety_net_timeout and \
               not state.get("safety_net_pending") and state.get("safety_net_triggered_for") != last_seen:
                if (current_time - last_seen) < 180:
                    state["safety_net_pending"] = True
                    state["safety_net_sent_at"] = current_time
                    state["safety_net_triggered_for"] = last_seen
                    await save_state()
                    threading.Thread(target=send_safety_net_admin, args=(current_time,)).start()
            sent_at = state.get("safety_net_sent_at", 0)
            if state.get("safety_net_pending") and (current_time - sent_at) > 30:
                state["safety_net_pending"] = False
                await save_state()
            if status == "up" and (current_time - last_seen) > 180:
                state["status"] = "down"
                state["safety_net_pending"] = False
                down_time_ts = last_seen + get_push_interval()
                state["went_down_at"] = down_time_ts
                await log_event("down", down_time_ts)
                msg = format_event_message(False, down_time_ts, state.get("came_up_at", 0))
                if state.get('quiet_status') == 'quiet':
                    state['pending_confirmation'] = True
                    threading.Thread(target=send_admin_confirmation, args=(down_time_ts,)).start()
                else:
                    threading.Thread(target=send_telegram, args=(msg,)).start()
                await save_state()

            # Auto-confirmation fallback (5 minutes)
            if state.get('pending_confirmation') and (current_time - state.get('went_down_at', 0)) > 300:
                print("Safety Net auto-confirming outage after 5 minutes of no response.")
                state['pending_confirmation'] = False
                state['quiet_status'] = 'active' # Wake up from quiet mode
                down_time_ts = state.get('went_down_at', time.time())
                msg = format_event_message(False, down_time_ts, state.get("came_up_at", 0))
                threading.Thread(target=send_telegram, args=(msg,)).start()
                await save_state()

async def alerts_loop():
    print("Alerts loop started...")
    while True:
        try:
            current_alert = get_air_raid_alert()
            new_status = current_alert.get("status")
            if new_status != "unknown":
                await load_state()
                async with state_mgr:
                    old_status = state.get("alert_status", "clear")
                    if new_status != old_status:
                        now_dt = datetime.datetime.now(KYIV_TZ)
                        time_str = now_dt.strftime("%H:%M")
                        
                        # Check config for air raid notifications
                        cfg = get_config()
                        can_notify = cfg.get("advanced", {}).get("notifications", {}).get("telegram_air_raid_alerts", True)
                        if str(can_notify).lower() in ("false", "0", "no"):
                            can_notify = False
                        else:
                            can_notify = bool(can_notify)

                        if new_status == "active":
                            state["alert_start_time"] = now_dt.timestamp()
                            if can_notify:
                                msg = f"⚠️ <b>{time_str} ПОВІТРЯНА ТРИВОГА! КИЇВ</b>"
                                threading.Thread(target=send_telegram, args=(msg,)).start()
                        elif old_status == "active" and new_status != "active":
                            start_ts = state.get("alert_start_time")
                            duration_str = ""
                            if start_ts:
                                duration_sec = int(now_dt.timestamp() - start_ts)
                                hours, mins = duration_sec // 3600, (duration_sec % 3600) // 60
                                duration_str = f"\nяка тривала {hours} год {mins} хв" if hours > 0 else f"\nяка тривала {mins} хв"
                            
                            if can_notify:
                                msg = f"✅ <b>{time_str} ВІДБІЙ ТРИВОГИ</b>{duration_str}"
                                threading.Thread(target=send_telegram, args=(msg,)).start()
                        state["alert_status"] = new_status
                        await save_state()
        except Exception as e: print(f"Error in alerts loop: {e}")
        await asyncio.sleep(60)

async def sync_schedules():
    sync_success = False
    if SCHEDULE_API_URL:
        try:
            print(f"Syncing schedules from {SCHEDULE_API_URL}...")
            urls = {SCHEDULE_FILE: f"{SCHEDULE_API_URL}/last_schedules.json", HISTORY_FILE: f"{SCHEDULE_API_URL}/schedule_history.json"}
            for local_file, url in urls.items():
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with open(local_file, "wb") as f: f.write(r.content)
            sync_success = True
        except Exception as e: print(f"Failed to sync schedules: {e}")
    if not sync_success:
        print("Starting local schedule parsing...")
        start_time = time.time()
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        result = await update_local_schedules(config_path, SCHEDULE_FILE)
        
        try:
            from app import PARSING_DURATION
            PARSING_DURATION.observe(time.time() - start_time)
        except ImportError:
            pass
            
        has_changed = result[1] if isinstance(result, tuple) and len(result) == 2 else False
        if has_changed:
            trigger_daily_report_update()
            trigger_weekly_report_update()
            should_alert = False
            try:
                if os.path.exists(SCHEDULE_FILE):
                    with open(SCHEDULE_FILE, 'r') as f: data = json.load(f)
                    for s_key in ['github', 'yasno']:
                        sources = data.get(s_key, {})
                        for group_name, days in sources.items():
                            for d, day_data in days.items():
                                if day_data.get('slots') and any(s is False for s in day_data['slots']):
                                    should_alert = True; break
                            if should_alert: break
                        if should_alert: break
                    if should_alert:
                        slots_structure = {s_key: {gn: {d: day_data['slots'] for d, day_data in days.items() if day_data.get('slots') and any(s is False for s in day_data['slots'])} for gn, days in data.get(s_key, {}).items()} for s_key in ['github', 'yasno']}
                        current_hash = hashlib.md5(json.dumps(slots_structure, sort_keys=True).encode()).hexdigest()
                        async with state_mgr:
                            if current_hash == state.get("last_schedule_hash"): 
                                should_alert = False
                            else: 
                                state["last_schedule_hash"] = current_hash
                                await save_state()
                                # Trigger immediate Telegram notification for the new schedule
                                print("Schedule changed! Triggering immediate Telegram alert...")
                                if should_alert:
                                    state["quiet_status"] = "active"
                                    await save_state()
                                trigger_text_report_update()
            except Exception as e: 
                print(f"Error checking schedule changes: {e}")
                should_alert = True

def check_quiet_mode_eligibility():
    now = time.time()
    cutoff_24h_ago = now - (24 * 3600)
    try:
        if os.path.exists(EVENT_LOG_FILE):
            with open(EVENT_LOG_FILE, 'r') as f:
                logs = json.load(f)
                if any(entry.get("event") == "down" and entry.get("timestamp", 0) >= cutoff_24h_ago for entry in logs): return False
    except: return False
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r') as f: data = json.load(f)
            now_dt = datetime.datetime.fromtimestamp(now, KYIV_TZ)
            today_str, tomorrow_str = now_dt.strftime("%Y-%m-%d"), (now_dt + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            current_slot_idx = (now_dt.hour * 2) + (1 if now_dt.minute >= 30 else 0)
            for s_key in ['github', 'yasno']:
                for gn, days in data.get(s_key, {}).items():
                    all_slots = (days.get(today_str, {}).get('slots') or ([True]*48)) + (days.get(tomorrow_str, {}).get('slots') or ([True]*48))
                    if any(all_slots[i] is False for i in range(current_slot_idx, min(current_slot_idx + 48, len(all_slots)))): return False
        else: return False
    except: return False
    return True

async def schedule_loop():
    print("Schedule loop started...")
    weekly_sent_date = None
    last_prune_date = None
    
    while True:
        now = datetime.datetime.now(KYIV_TZ)
        now_str = now.strftime("%H:%M")
        today_date = now.strftime("%Y-%m-%d")
        
        # 1. Daily maintenance (at 00:01)
        if now.hour == 0 and now.minute == 1:
            trigger_daily_report_update(is_final=True)
            if last_prune_date != today_date:
                prune_old_data()
                create_backup("daily_auto")
                last_prune_date = today_date
            await asyncio.sleep(65)
            continue

        # 2. Dynamic report times from config
        cfg = get_config()
        report_times = cfg.get("advanced", {}).get("notifications", {}).get("report_times", [])
        if now_str in report_times:
            print(f"Triggering scheduled report at {now_str}...")
            trigger_daily_report_update(is_final=False)
            await asyncio.sleep(65)
            continue

        # 3. Regular sync and status updates every 10 mins
        if now.minute % 10 == 0:
            await sync_schedules()
            trigger_daily_report_update(is_final=False)
            trigger_text_report_update()
            await update_quiet_status()
            
        # 4. Weekly report (Monday morning)
        if now.weekday() == 0 and now.hour == 0 and 15 <= now.minute < 25:
            if weekly_sent_date != today_date:
                try:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    subprocess.run([sys.executable, os.path.join(base_dir, "generate_weekly_report.py"), "--date", (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")], check=True, cwd=base_dir)
                    weekly_sent_date = today_date
                except: pass
        
        await asyncio.sleep(60)
