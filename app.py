import requests
from flask import Flask, render_template, jsonify, send_from_directory, make_response
import json
from datetime import datetime, timedelta
import os
import time
import re
from bs4 import BeautifulSoup
import threading
from light_service import (
    load_state, save_state, state, state_lock, 
    monitor_loop, schedule_loop, get_current_time, format_duration, 
    log_event, get_schedule_context, send_telegram, 
    get_deviation_info, get_nearest_schedule_switch,
    format_event_message, get_next_scheduled_event,
    trigger_daily_report_update, trigger_weekly_report_update,
    get_air_raid_alert,
    KYIV_TZ
)


app = Flask(__name__, static_folder=None)

# --- Configuration ---
DATA_DIR = os.environ.get("DATA_DIR", ".")
LIGHT_MONITOR_URL = "http://127.0.0.1:8889/"

# --- Paths ---
LIGHT_STATE_FILE = os.path.join(DATA_DIR, "power_monitor_state.json")
EVENT_LOG_FILE = os.path.join(DATA_DIR, "event_log.json")

# --- Caching ---
CACHE = {}
CACHE_TTL = 60
cache_lock = threading.Lock()

def cached_fetch(key, func):
    with cache_lock:
        now = time.time()
        if key in CACHE and now - CACHE[key]['time'] < CACHE_TTL:
            return CACHE[key]['data']
        
        # If we are here, we need to update
        try:
            data = func()
            CACHE[key] = {'time': now, 'data': data}
            return data
        except Exception as e:
            print(f"Cache update error for {key}: {e}")
            return CACHE.get(key, {}).get('data') # Return stale data on error

# --- PWA Routes ---
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

@app.route('/static/<path:filename>')
def serve_static(filename):
    # Try data dir first (for generated charts), then code dir
    data_static = os.path.join(DATA_DIR, 'static')
    full_path = os.path.join(data_static, filename)
    
    if os.path.exists(full_path):
        response = make_response(send_from_directory(data_static, filename))
    else:
        response = make_response(send_from_directory('static', filename))
    
    # Disable caching for images to ensure they refresh in PWA/Mobile
    if filename.endswith('.png'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response

def get_radiation():
    # Return stable background value
    import random
    val = round(0.10 + random.uniform(0, 0.02), 2)
    return {
        "level": val,
        "unit": "мкЗв/год",
        "status": "normal"
    }

LIGHT_STATE_FILE = "power_monitor_state.json"
EVENT_LOG_FILE = "event_log.json"

def get_power_events_data(limit=5):
    recent_events = []
    
    # Default schedule info
    sched_light_now, current_end, next_range, next_duration = get_schedule_context()
    latest_event_text = f"Наступне планове: {next_range}"
    
    try:
        if os.path.exists(EVENT_LOG_FILE):
            with open(EVENT_LOG_FILE, "r") as f:
                logs = json.load(f)
                
                if len(logs) >= 1:
                    # Calculate durations
                    for i in range(len(logs)):
                        if i > 0:
                            logs[i]['duration_prev'] = logs[i]['timestamp'] - logs[i-1]['timestamp']
                        else:
                            logs[i]['duration_prev'] = None
                            
                    last_logs = logs[-limit:][::-1]
                    
                    for log in last_logs:
                        ts = log.get('timestamp', 0)
                        evt = log.get('event', 'unknown')
                        dur_sec = log.get('duration_prev')
                        
                        dt_str = datetime.fromtimestamp(ts).strftime("%d.%m %H:%M")
                        icon = "🟢" if evt == "up" else "🔴"
                        text = "Світло з'явилося" if evt == "up" else "Світло зникло"
                        pre_text = "не було" if evt == "up" else "було"
                        
                        dur_str = format_duration(dur_sec) if dur_sec else ""
                        
                        recent_events.append({
                            "time": dt_str,
                            "icon": icon,
                            "text": text,
                            "desc": f"({pre_text} {dur_str})" if dur_str else ""
                        })
                    
                    # Construct current status text
                    load_state()
                    with state_lock:
                        status = state.get("status", "unknown")
                    
                    target_evt = "up" if status == "up" else "down"
                    
                    # Find the latest log entry that matches current status
                    last_match = None
                    for log in reversed(logs):
                        if log.get('event') == target_evt:
                            last_match = log
                            break
                    
                    if not last_match:
                        last_match = logs[-1]
                        
                    ts = last_match['timestamp']
                    evt = last_match['event']
                    
                    # --- NEW TEXT LOGIC ---
                    dev_msg = get_deviation_info(ts, evt == "up")
                    dev_line = ""
                    if dev_msg:
                        # Expected: "На 10 хв пізніше графіка"
                        m = re.search(r"(?:Увімкнули|Вимкнули)\s+(раніше|пізніше)\s+на\s+(.+)$", dev_msg)
                        if m:
                            timing = m.group(1)
                            value = m.group(2)
                            dev_line = f"На {value} {timing} графіка"
                        elif "точно за графіком" in dev_msg:
                            dev_line = "Точно за графіком"
                    
                    # Next event prediction
                    look_for_light = (evt != "up") # If currently UP, look for OFF (False)
                    next_info = get_next_scheduled_event(ts, look_for_light)
                    wait_line = ""
                    if next_info:
                        next_time = next_info["interval"].split('-')[0]
                        wait_prefix = "Вимкнення о" if evt == "up" else "Очікуємо о"
                        wait_line = f"{wait_prefix} {next_time}"
                    
                    if dev_line and wait_line:
                        latest_event_text = f"{dev_line}<br>{wait_line}"
                    elif dev_line:
                        latest_event_text = f"{dev_line}"
                    elif wait_line:
                        latest_event_text = f"{wait_line}"
                    else:
                        latest_event_text = f"Наступне планове: {next_range}"
                    
    except Exception as e:
        print(f"Error reading events: {e}")
        pass
        
    return latest_event_text, recent_events

DAYS_UA = {0: "Понеділок", 1: "Вівторок", 2: "Середа", 3: "Четвер", 4: "П'ятниця", 5: "Субота", 6: "Неділя"}

def render_day_schedule_html(slots, date_obj):
    if not slots: return ""
    
    intervals_on = []
    intervals_off = []
    current_state = slots[0]
    start_idx = 0
    
    def format_slot_time(idx):
        mins = idx * 30
        h, m = mins // 60, mins % 60
        return f"{h:02d}:{m:02d}"
        
    for i in range(1, 48):
        if slots[i] != current_state:
            inv = {"state": current_state, "start": format_slot_time(start_idx), "end": format_slot_time(i), "duration": (i - start_idx) * 0.5}
            if current_state: intervals_on.append(inv)
            else: intervals_off.append(inv)
            start_idx = i
            current_state = slots[i]
    
    # Last interval
    inv = {"state": current_state, "start": format_slot_time(start_idx), "end": "24:00", "duration": (48 - start_idx) * 0.5}
    if current_state: intervals_on.append(inv)
    else: intervals_off.append(inv)

    total_on = sum(1 for s in slots if s) * 0.5
    total_off = 24.0 - total_on

    MONTHS_UA = {1: "Січня", 2: "Лютого", 3: "Березня", 4: "Квітня", 5: "Травня", 6: "Червня", 7: "Липня", 8: "Серпня", 9: "Вересня", 10: "Жовтня", 11: "Листопада", 12: "Грудня"}
    day_title = f"{date_obj.day} {MONTHS_UA[date_obj.month]} ({DAYS_UA[date_obj.weekday()]})"
    
    def fmt_dur(hours):
        return f"{hours:g}".replace('.', ',')

    res = []
    res.append(f"<div class='schedule-date'>{day_title}</div>")
    res.append("<div class='schedule-columns'>")
    
    # Column ON
    res.append("<div class='schedule-col'>")
    res.append(f"<div class='col-header on'>Увімкнення 🔆 {fmt_dur(total_on)}</div>")
    for inv in intervals_on:
        res.append(f"<div class='schedule-line on'><span class='schedule-time'>{inv['start']}</span><span class='time-sep'>-</span><span class='schedule-time'>{inv['end']}</span><span class='schedule-duration'>({fmt_dur(inv['duration'])})</span></div>")
    res.append("</div>")

    # Column OFF
    res.append("<div class='schedule-col'>")
    res.append(f"<div class='col-header off'>Вимкнення ✖️ {fmt_dur(total_off)}</div>")
    for inv in intervals_off:
        res.append(f"<div class='schedule-line off'><span class='schedule-time'>{inv['start']}</span><span class='time-sep'>-</span><span class='schedule-time'>{inv['end']}</span><span class='schedule-duration'>({fmt_dur(inv['duration'])})</span></div>")
    res.append("</div>")
    res.append("</div>")
    return "".join(res)

def get_today_schedule_text():
    try:
        config_path = "config.json"
        data_dir = os.environ.get("DATA_DIR", ".")
        schedule_file = os.path.join(data_dir, "last_schedules.json")
        if not os.path.exists(schedule_file):
            return "Графік відсутній"
            
        with open(schedule_file, 'r') as f:
            data = json.load(f)
            
        source = data.get('yasno') or data.get('github')
        if not source: return "Дані не знайдені"
        
        group_key = list(source.keys())[0]
        schedule_data = source[group_key]
        
        now = datetime.now(KYIV_TZ)
        today_str = now.strftime("%Y-%m-%d")
        tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        
        output = []
        
        # Today
        if today_str in schedule_data and schedule_data[today_str].get('slots'):
            output.append(render_day_schedule_html(schedule_data[today_str]['slots'], now))
        
        # Tomorrow
        if tomorrow_str in schedule_data and schedule_data[tomorrow_str].get('slots'):
            # Only show tomorrow if it has actual data (not just pending)
            slots = schedule_data[tomorrow_str]['slots']
            if slots and any(s is not None for s in slots):
                output.append("<div class='schedule-divider'></div>")
                output.append(render_day_schedule_html(slots, now + timedelta(days=1)))
            
        file_mtime = os.path.getmtime(schedule_file)
        dt_mtime = datetime.fromtimestamp(file_mtime, KYIV_TZ)
        output.append(f"<div class='updated-time'>Оновлено: {dt_mtime.strftime('%H:%M')}</div>")
        
        return "".join(output)
    except Exception as e:
        print(f"Error building schedule text: {e}")
        return "Помилка завантаження графіка"

def get_air_quality():
    try:
        config_path = "config.json"
        if not os.path.exists(config_path):
            return {"status": "error", "text": "Config missing"}
            
        with open(config_path, 'r') as f:
            cfg = json.load(f)
            
        aq_cfg = cfg.get("sources", {}).get("air_quality", {})
        if not aq_cfg:
            return {"status": "error", "text": "AQ source disabled"}

        # OpenMeteo for PM2.5/PM10
        lat = aq_cfg.get("lat", "50.45")
        lon = aq_cfg.get("lon", "30.52")
        om_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm10,pm2_5"
        
        # SaveEcoBot for Station-specific (Station 17095)
        seb_id = aq_cfg.get("seb_station", "17095")
        seb_url = f"https://www.saveecobot.com/platform/api/v1/stations/{seb_id}"
        
        # Weather for Temp/Hum
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"

        def fetch_all():
            pm_data = requests.get(om_url, timeout=5).json()
            w_data = requests.get(w_url, timeout=5).json()
            
            pm25 = pm_data.get('current', {}).get('pm2_5', 0)
            pm10 = pm_data.get('current', {}).get('pm10', 0)
            
            # Simple AQI calculation based on PM2.5 (standard European scale approx)
            aqi = int(pm25 * 3) # rough proxy for simplified dashboard
            
            status = "ok"
            status_text = "Низький"
            if aqi > 50: 
                status = "warning"
                status_text = "Помірне"
            if aqi > 100: 
                status = "danger"
                status_text = "Високе"

            return {
                "aqi": aqi,
                "status": status,
                "text": status_text,
                "pm25": pm25,
                "pm10": pm10,
                "pm1": None,
                "temp": w_data.get('current', {}).get('temperature_2m'),
                "hum": w_data.get('current', {}).get('relative_humidity_2m'),
                "wind_speed": w_data.get('current', {}).get('wind_speed_10m'),
                "wind_dir": get_wind_label(w_data.get('current', {}).get('wind_direction_10m')),
                "location": aq_cfg.get("location_name", "Київ")
            }

        return cached_fetch("air_quality", fetch_all)
    except Exception as e:
        print(f"AQ Error: {e}")
        return {"status": "error", "text": "Дані відсутні"}

def get_wind_label(deg):
    if deg is None: return "-"
    labels = ["Пн", "ПнСх", "Сх", "ПдСх", "Пд", "ПдЗх", "Зх", "ПнЗх"]
    return labels[int((deg + 22.5) % 360 / 45)]

@app.route('/')
def index():
    # Force dark theme preference for the dashboard
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    load_state()
    with state_lock:
        current_status = state.get("status", "unknown")
        # Ensure we return strictly "on" or "off" for UI icons
        ui_light_state = "on" if current_status == "up" else "off"
        
    latest_event_text, recent_events = get_power_events_data()
    schedule_text = get_today_schedule_text()
    aq_data = get_air_quality()
    alert_data = get_air_raid_alert()
    
    # Extract group name
    config_path = "config.json"
    group_name = "---"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            cfg = json.load(f)
            groups = cfg.get("settings", {}).get("groups", [])
            if groups:
                group_name = groups[0].replace('GPV', '')

    return jsonify({
        "light": ui_light_state,
        "light_event": latest_event_text,
        "recent_events": recent_events,
        "schedule_text": schedule_text,
        "aqi": aq_data,
        "radiation": get_radiation(),
        "alert": alert_data,
        "group": group_name
    })

@app.route('/api/push/<key>')
def push_api(key):
    load_state()
    # Support multiple keys if needed, but here we check the one from state
    if key != state.get('secret_key'):
        return jsonify({"status": "error", "msg": "invalid_key"}), 403
        
    current_time = time.time()
    
    with state_lock:
        previous_status = state.get("status", "unknown")
        state["last_seen"] = current_time
        
        if previous_status == "down" or previous_status == "unknown":
            state["status"] = "up"
            state["came_up_at"] = current_time
            log_event("up", current_time)
            
            # New compact message format
            # Use went_down_at before it might get updated (though push only sets came_up)
            msg = format_event_message(True, current_time, state.get("went_down_at", 0))
            
            threading.Thread(target=send_telegram, args=(msg,)).start()
            # trigger_daily_report_update() REMOVED FOR QUIET EVENTS
            
        save_state()
        
    return jsonify({
        "status": "ok", 
        "msg": "heartbeat_received",
        "timestamp": datetime.now(KYIV_TZ).strftime("%H:%M:%S")
    })

# Initialize State
load_state()
print(f"Push URL configured for key: {state.get('secret_key')}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
