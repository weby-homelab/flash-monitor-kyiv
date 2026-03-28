import requests
from flask import Flask, render_template, jsonify, send_from_directory, make_response, request
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import time
import re
from bs4 import BeautifulSoup
import threading
import subprocess
import secrets

# Запуск ініціалізації для нових користувачів
import bootstrap
bootstrap.perform_cold_start_if_needed()

from light_service import (
    load_state, save_state, state, state_mgr,
    monitor_loop, schedule_loop, get_current_time, format_duration,
    log_event, get_schedule_context, send_telegram,
    get_deviation_info, get_nearest_schedule_switch,
    format_event_message, get_next_scheduled_event,
    trigger_daily_report_update, trigger_weekly_report_update,
    get_air_raid_alert, get_push_interval, get_advanced_setting,
    update_quiet_status, sync_schedules,
    create_backup, list_backups, restore_backup,
    TOKEN, CHAT_ID, ADMIN_CHAT_ID,
    KYIV_TZ, STATE_LOCK_FILE, DATA_DIR, EVENT_LOG_FILE
)


app = Flask(__name__, static_folder=None)

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

from werkzeug.exceptions import NotFound

@app.route('/static/<path:filename>')
def serve_static(filename):
    # Try data dir first (for generated charts), then code dir
    data_static = os.path.join(DATA_DIR, 'static')
    
    try:
        response = make_response(send_from_directory(data_static, filename))
    except NotFound:
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

def get_power_events_data(limit=5):
    recent_events = []
    
    # Default schedule info
    sched_light_now, current_end, next_range, next_duration, is_emergency = get_schedule_context()
    if is_emergency:
        latest_event_text = "• ‼️‼️ можливі аварійні відключення"
    else:
        latest_event_text = f"• Наступне планове: {next_range}"
    
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
                    with state_mgr:
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
                        # get_deviation_info format: "• Увімкнули пізніше на 10 хв"
                        m = re.search(r"(?:Увімкнули|Вимкнули)\s+(раніше|пізніше)\s+на\s+(.+)$", dev_msg)
                        
                        if status == "up":
                            if m:
                                timing = m.group(1)
                                value = m.group(2)
                                dev_line = f"• З'явилося на {value} {timing}"
                            elif "точно за графіком" in dev_msg:
                                dev_line = "• З'явилося Точно за графіком"
                        else:
                            if m:
                                timing = m.group(1)
                                value = m.group(2)
                                dev_line = f"• на {value} {timing}"
                            elif "точно за графіком" in dev_msg:
                                dev_line = "• Точно за графіком"
                    
                    # Next event prediction
                    current_ts = time.time()
                    look_for_light = (status != "up") # If currently UP, look for OFF (False)
                    next_info = get_next_scheduled_event(current_ts, look_for_light)
                    wait_line = ""
                    if next_info:
                        if status == "up":
                            next_time = next_info["interval"].split('-')[0]
                            wait_line = f"• Вимкнення о {next_time}"
                        else:
                            wait_line = f"• Очікуємо о {next_info['interval']}"
                    
                    if is_emergency:
                        latest_event_text = "• ‼️‼️ можливі аварійні відключення"
                    elif dev_line and wait_line:
                        latest_event_text = f"{dev_line}<br>{wait_line}"
                    elif dev_line:
                        latest_event_text = f"{dev_line}"
                    elif wait_line:
                        latest_event_text = f"{wait_line}"
                    elif sched_light_now and (next_range == "відключення не плануються 🔆" or next_range == "відключення не плануються ✅" or next_range == "час невідомий 🤷‍♂️" or next_range == "час очікується"):
                        latest_event_text = "• відключення не плануються 🔆"
                    else:
                        latest_event_text = f"• Наступне планове: {next_range}"
                    
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
        config_path = os.path.join(DATA_DIR, "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
        data_dir = os.environ.get("DATA_DIR", ".")
        schedule_file = os.path.join(data_dir, "last_schedules.json")
        if not os.path.exists(schedule_file):
            return "Графік відсутній"

        with open(schedule_file, 'r') as f:
            data = json.load(f)

        now = datetime.now(KYIV_TZ)
        today_str = now.strftime("%Y-%m-%d")
        tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

        # --- SMART SOURCE MERGE ---
        # We collect slots from all sources and merge them: False (outage) always wins over True (light).
        today_slots = None
        tomorrow_slots = None
        emergency_sources = []

        for s_name in ['yasno', 'github']:
            src = data.get(s_name)
            if not src: continue

            grp = list(src.keys())[0]
            name = "YASNO" if s_name == 'yasno' else "ДТЕК"

            # Today
            day_data = src[grp].get(today_str)
            if day_data:
                if day_data.get('status') == 'emergency':
                    if name not in emergency_sources: emergency_sources.append(name)

                s = day_data.get('slots')
                if s:
                    if today_slots is None:
                        today_slots = list(s)
                    else:
                        for i in range(min(len(today_slots), len(s))):
                            if s[i] is False: today_slots[i] = False

            # Tomorrow
            tm_data = src[grp].get(tomorrow_str)
            if tm_data:
                s = tm_data.get('slots')
                if s:
                    if tomorrow_slots is None:
                        tomorrow_slots = list(s)
                    else:
                        for i in range(min(len(tomorrow_slots), len(s))):
                            if s[i] is False: tomorrow_slots[i] = False

        if today_slots is None and not emergency_sources: 
            return "Дані не знайдені"

        output = []

        if emergency_sources:
            output.append("<div class='emergency-banner'>")
            output.append("<div class='emergency-title'>⚠️ Екстрені відключення!</div>")
            output.append("<div class='emergency-desc'>Графіки наразі не діють. Час увімкнення невідомий.</div>")
            output.append(f"<div class='source-label'>Джерело: {', '.join(emergency_sources)}</div>")
            output.append("</div>")

        # Render Today
        if today_slots:
            output.append(render_day_schedule_html(today_slots, now))

        # Render Tomorrow
        if tomorrow_slots:
            if any(s is not None for s in tomorrow_slots):
                output.append("<div class='schedule-divider'></div>")
                output.append(render_day_schedule_html(tomorrow_slots, now + timedelta(days=1)))

        file_mtime = os.path.getmtime(schedule_file)
        dt_mtime = datetime.fromtimestamp(file_mtime, KYIV_TZ)

        # Collect list of sources that actually provided SLOTS for today
        active_sources = []

        gh = data.get('github', {})
        if gh:
            g_gh = list(gh.keys())[0]
            if gh[g_gh].get(today_str, {}).get('slots'):
                active_sources.append("ДТЕК")

        ys = data.get('yasno', {})
        if ys:
            g_ys = list(ys.keys())[0]
            if ys[g_ys].get(today_str, {}).get('slots'):
                active_sources.append("YASNO")

        sources_str = f" [{', '.join(active_sources)}]" if active_sources else ""

        output.append(f"<div class='updated-time'>Оновлено: {dt_mtime.strftime('%H:%M')}{sources_str}</div>")

        return "".join(output)
    except Exception as e:
        print(f"Error building schedule text: {e}")
        return "Помилка завантаження графіка"

def get_air_quality():
    try:
        config_path = os.path.join(DATA_DIR, "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
        if not os.path.exists(config_path):
            return {"status": "error", "text": "Config missing"}
            
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            
        aq_cfg = cfg.get("sources", {}).get("air_quality", {})
        if not aq_cfg:
            return {"status": "error", "text": "AQ source disabled"}

        # OpenMeteo for PM2.5/PM10
        lat = aq_cfg.get("lat", "50.45")
        lon = aq_cfg.get("lon", "30.52")
        om_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm10,pm2_5&hourly=pm2_5&past_days=1"
        
        # SaveEcoBot for Station-specific (Station 17095)
        seb_id = aq_cfg.get("seb_station", "17095")
        seb_url = f"https://www.saveecobot.com/platform/api/v1/stations/{seb_id}"
        
        # Weather for Temp/Hum
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m&hourly=temperature_2m,relative_humidity_2m&past_days=1"

        def fetch_all():
            pm_data = requests.get(om_url, timeout=5).json()
            w_data = requests.get(w_url, timeout=5).json()

            pm25 = pm_data.get('current', {}).get('pm2_5', 0)
            pm10 = pm_data.get('current', {}).get('pm10', 0)

            history_hourly = []
            history_times = []
            temp_history = []
            hum_history = []
            try:
                pm25_hourly = pm_data.get('hourly', {}).get('pm2_5', [])
                time_hourly = pm_data.get('hourly', {}).get('time', [])

                temp_hourly = w_data.get('hourly', {}).get('temperature_2m', [])
                hum_hourly = w_data.get('hourly', {}).get('relative_humidity_2m', [])
                w_time_hourly = w_data.get('hourly', {}).get('time', [])

                if time_hourly:
                    now_iso = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:00")
                    try:
                        idx = time_hourly.index(now_iso)
                    except ValueError:
                        idx = len(time_hourly) - 1

                    if idx >= 23:
                        recent = pm25_hourly[idx-23:idx+1]
                        recent_times = time_hourly[idx-23:idx+1]
                    else:
                        recent = pm25_hourly[:idx+1]
                        recent_times = time_hourly[:idx+1]

                    for i in range(len(recent)):
                        val = recent[i] or 0
                        dt = datetime.fromisoformat(recent_times[i]).replace(tzinfo=ZoneInfo("UTC")).astimezone(KYIV_TZ)
                        history_hourly.append(int(val * 3))
                        history_times.append(dt.strftime("%H:%M"))

                if w_time_hourly:
                    now_iso = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:00")
                    try:
                        idx = w_time_hourly.index(now_iso)
                    except ValueError:
                        idx = len(w_time_hourly) - 1

                    if idx >= 11:
                        recent_temp = temp_hourly[idx-11:idx+1]
                        recent_hum = hum_hourly[idx-11:idx+1]
                    else:
                        recent_temp = temp_hourly[:idx+1]
                        recent_hum = hum_hourly[:idx+1]

                    for i in range(len(recent_temp)):
                        t_val = recent_temp[i] if recent_temp[i] is not None else 0
                        h_val = recent_hum[i] if recent_hum[i] is not None else 0
                        temp_history.append(t_val)
                        hum_history.append(h_val)

            except Exception as e:
                print(f"AQ History Error: {e}")

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
                "history_hourly": history_hourly,
                "history_times": history_times,
                "temp_history": temp_history,
                "hum_history": hum_history,
                "status": status,
                "text": status_text,
                "pm25": pm25,                "pm10": pm10,
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

@app.route('/admin')
def admin_panel():
    # Support token in URL params OR in X-Admin-Token header
    token = request.args.get('t') or request.headers.get('X-Admin-Token')
    if token and token == state.get('admin_token'):
        return render_template('admin.html')
    return "Access Denied", 403

@app.route('/api/status')
def api_status():
    load_state()
    with state_mgr:
        current_status = state.get("status", "unknown")
        # Ensure we return strictly "on" or "off" for UI icons
        ui_light_state = "on" if current_status == "up" else "off"
        
    latest_event_text, recent_events = get_power_events_data()
    schedule_text = get_today_schedule_text()
    
    # Dashboard toggles
    show_aq = get_advanced_setting("dashboard", "show_aq", True)
    show_rad = get_advanced_setting("dashboard", "show_radiation", True)
    show_graphs = get_advanced_setting("dashboard", "show_temp_graph", True)
    show_charts = get_advanced_setting("dashboard", "show_charts", True)
    
    aq_data = get_air_quality() if show_aq else None
    rad_data = get_radiation() if show_rad else None
    alert_data = get_air_raid_alert()
    
    # Extract group name
    config_path = os.path.join(DATA_DIR, "config.json")
    if not os.path.exists(config_path):
        config_path = "config.json"
    group_name = "---"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            groups = cfg.get("settings", {}).get("groups", [])
            if groups:
                group_name = groups[0].replace('GPV', '')

    # Extra: get raw slots for graph bar
    from datetime import timedelta
    now = datetime.now(KYIV_TZ)
    date_str = now.strftime("%Y-%m-%d")
    slots = [True] * 48
    data_dir = os.environ.get("DATA_DIR", "data")
    sched_file = os.path.join(data_dir, "last_schedules.json")
    if os.path.exists(sched_file):
        try:
            with open(sched_file, 'r') as f:
                s_data = json.load(f)
                merged = None
                for src in ['github', 'yasno']:
                    s = s_data.get(src)
                    if not s: continue
                    g_key = list(s.keys())[0]
                    day_data = s.get(g_key, {}).get(date_str, {}).get('slots')
                    if day_data:
                        if merged is None: merged = list(day_data)
                        else:
                            for i in range(min(len(merged), len(day_data))):
                                if day_data[i] is False: merged[i] = False
                if merged: slots = merged
        except: pass

    return jsonify({
        "light": ui_light_state,
        "light_event": latest_event_text,
        "recent_events": recent_events,
        "schedule_text": schedule_text,
        "schedule_slots": slots,
        "aqi": aq_data,
        "radiation": rad_data,
        "alert": alert_data,
        "group": group_name,
        "show_graphs": show_graphs,
        "show_charts": show_charts,
        "timestamp": datetime.now(KYIV_TZ).strftime("%H:%M:%S")
    })

@app.route('/api/push/<key>')
def push_api(key):
    # Support key in path OR X-Secret-Key header
    secret_key = request.headers.get('X-Secret-Key') or key
    if secret_key != state.get('secret_key'):
        return jsonify({"status": "error", "msg": "invalid_key"}), 403
        
    current_time = time.time()
    
    with state_mgr:
            load_state()  # Reload to get latest changes from other workers
            previous_status = state.get("status", "unknown")
            state["last_seen"] = current_time
            state["safety_net_pending"] = False # Reset on heartbeat
            state["safety_net_sent_at"] = 0     # Reset on heartbeat
            state["safety_net_triggered_for"] = 0 # Reset on heartbeat
            
            if (previous_status == "down" or previous_status == "unknown") and state.get("status") == "unknown": # Skip if already up
                pass
            
            if previous_status == "down" or previous_status == "unknown":
                state["status"] = "up"
                state["came_up_at"] = current_time
                log_event("up", current_time)
                
                # Quiet Mode check: skip message if status is 'quiet'
                if state.get("quiet_status") == "quiet":
                    print("Quiet mode active: Skipping 'Light Up' Telegram message.")
                else:
                    msg = format_event_message(True, current_time, state.get("went_down_at", 0))
                    threading.Thread(target=send_telegram, args=(msg,)).start()
                
            save_state()
        
    return jsonify({
        "status": "ok", 
        "msg": "heartbeat_received",
        "timestamp": datetime.now(KYIV_TZ).strftime("%H:%M:%S")
    })

@app.route('/api/down/<key>')
def down_api(key):
    # Support key in path OR X-Secret-Key header
    secret_key = request.headers.get('X-Secret-Key') or key
    if secret_key != state.get('secret_key'):
        return jsonify({"status": "error", "msg": "invalid_key"}), 403
        
    current_time = time.time()
    
    with state_mgr:
            load_state()
            previous_status = state.get("status", "unknown")
            
            if previous_status == "up" or previous_status == "unknown":
                state["status"] = "down"
                state["went_down_at"] = current_time
                log_event("down", current_time)
                
                # Quiet Mode check
                if state.get("quiet_status") == "quiet":
                    print("Quiet mode active: Skipping 'Light Down' Telegram message from API.")
                else:
                    msg = format_event_message(False, current_time, state.get("came_up_at", 0))
                    threading.Thread(target=send_telegram, args=(msg,)).start()
                
            save_state()
        
    return jsonify({
        "status": "ok", 
        "msg": "manual_down_received",
        "timestamp": datetime.now(KYIV_TZ).strftime("%H:%M:%S")
    })

@app.route('/api/tg/webhook', methods=['POST'])
def tg_webhook():
    data = request.get_json()
    if not data: return "OK"
    
    if 'callback_query' in data:
        cb = data['callback_query']
        cb_data = cb.get('data', '')
        msg_id = cb.get('message', {}).get('message_id')
        chat_id = cb.get('message', {}).get('chat', {}).get('id')
        
        if cb_data.startswith('confirm_down_'):
            load_state()
            with state_mgr:
                state['quiet_status'] = 'active'
                state['pending_confirmation'] = False
                state['safety_net_pending'] = False

                # Send the public Telegram alert
                try:
                    timestamp = float(cb_data.split('_')[-1])
                except:
                    timestamp = time.time()

                msg = format_event_message(False, timestamp, state.get("came_up_at", 0))
                threading.Thread(target=send_telegram, args=(msg,)).start()

                # Update status
                state["status"] = "down"
                state["went_down_at"] = timestamp
                log_event("down", timestamp)
                save_state()

            # Answer callback
            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={
                "callback_query_id": cb['id'],
                "text": "🔴 Підтверджено"
            })

            # Edit message
            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": "🔴 Світло зникло (Підтверджено)"
            })

        elif cb_data.startswith('ignore_down_'):
            load_state()
            with state_mgr:
                state['pending_confirmation'] = False
                save_state()

            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={
                "callback_query_id": cb['id'],
                "text": "🟢 Ігноровано"
            })

            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": "🟢 Збій / Роботи (Ігноровано)"
            })

        elif cb_data.startswith('sn_tech_'):
            # Show mute options
            timestamp = cb_data.split('_')[-1]
            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": "🛠 На скільки часу вимкнути моніторинг?",
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {"text": "5 хв", "callback_data": f"mute_5_{timestamp}"},
                            {"text": "15 хв", "callback_data": f"mute_15_{timestamp}"},
                            {"text": "30 хв", "callback_data": f"mute_30_{timestamp}"}
                        ],
                        [
                            {"text": "1 год", "callback_data": f"mute_60_{timestamp}"},
                            {"text": "2 год", "callback_data": f"mute_120_{timestamp}"}
                        ],
                        [
                            {"text": "⬅️ Назад", "callback_data": f"sn_back_{timestamp}"}
                        ]
                    ]
                }
            })

        elif cb_data.startswith('mute_'):
            parts = cb_data.split('_')
            minutes = int(parts[1])
            load_state()
            with state_mgr:
                state['muted_until'] = time.time() + (minutes * 60)
                state['safety_net_pending'] = False
                save_state()

            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={
                "callback_query_id": cb['id'],
                "text": f"🛠 Моніторинг вимкнено на {minutes} хв"
            })

            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": f"🛠 Технічний збій. Моніторинг призупинено до {datetime.fromtimestamp(state['muted_until'], KYIV_TZ).strftime('%H:%M')}"
            })

        elif cb_data.startswith('sn_dontknow_'):
            load_state()
            with state_mgr:
                state['safety_net_pending'] = False
                save_state()

            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={
                "callback_query_id": cb['id'],
                "text": "🤷‍♂️ Чекаємо 3 хв"
            })

            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": "🤷‍♂️ Невідомо. Чекаємо стандартний таймаут 3 хвилини."
            })

        elif cb_data.startswith('sn_down_'):
            # Confirm DOWN instantly
            load_state()
            with state_mgr:
                state['safety_net_pending'] = False
                state['quiet_status'] = 'active'
                state["status"] = "down"
                
                # Apply standard correction (last_seen + configured interval)
                last_seen = state.get("last_seen", time.time())
                down_time_ts = last_seen + get_push_interval()
                
                state["went_down_at"] = down_time_ts
                log_event("down", down_time_ts)
                
                msg = format_event_message(False, down_time_ts, state.get("came_up_at", 0))
                threading.Thread(target=send_telegram, args=(msg,)).start()
                save_state()

            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={
                "callback_query_id": cb['id'],
                "text": "🔴 Підтверджено зникнення"
            })

            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": "🔴 Світло зникло (Підтверджено адміном)"
            })

        elif cb_data.startswith('sn_back_'):
            timestamp = cb_data.split('_')[-1]
            # Restore safety net buttons
            msg = "🚨 <b>SAFETY NET: ВТРАТА ПУША!</b>\n\nВже 35 сек немає зв'язку. Що сталося?"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": msg,
                "parse_mode": "HTML",
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {"text": "🔴 Світло зникло?", "callback_data": f"sn_down_{timestamp}"},
                            {"text": "🛠 Технічний збій?", "callback_data": f"sn_tech_{timestamp}"}
                        ],
                        [
                            {"text": "🤷‍♂️ Не знаю!", "callback_data": f"sn_dontknow_{timestamp}"}
                        ]
                    ]
                }
            })
            
            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={
                "callback_query_id": cb['id'],
                "text": "Назад"
            })
            
    return "OK"

# --- Admin APIs ---

def check_admin_token():
    # Support token in URL params OR in X-Admin-Token header
    t = request.args.get('t') or request.headers.get('X-Admin-Token')
    if not t or t != state.get('admin_token'):
        return False
    return True

@app.route('/api/admin/data')
def admin_data():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403
    
    config_path = os.path.join(DATA_DIR, "config.json")
    if not os.path.exists(config_path):
        config_path = "config.json"
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
    load_state()
    
    logs = []
    if os.path.exists(EVENT_LOG_FILE):
        with open(EVENT_LOG_FILE, 'r') as f:
            logs = json.load(f)
            
    # Get version
    version = "2.4.7"
    version_path = os.path.join(os.path.dirname(__file__), "VERSION")
    if os.path.exists(version_path):
        with open(version_path, 'r') as f:
            version = f.read().strip()

    return jsonify({
        "config": config,
        "state": state,
        "logs": logs[-20:][::-1], # Last 20, newest first
        "version": version,
        "env": {
            "telegram_bot_token": TOKEN,
            "telegram_channel_id": CHAT_ID
        }
    })

@app.route('/api/admin/config', methods=['POST'])
def admin_config_post():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403

    new_config = request.get_json()
    if not new_config:
        return jsonify({"status": "error", "msg": "Invalid JSON"}), 400

    try:
        # Create auto-backup before saving
        create_backup("auto_before_save")

        config_path = os.path.join(DATA_DIR, "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        
        # Clear cache to reflect changes immediately (AQ, etc.)
        with cache_lock:
            CACHE.clear()
            
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/admin/quiet/mode', methods=['POST'])
def admin_quiet_mode():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403
        
    data = request.get_json()
    mode = data.get('mode')
    unmute = data.get('unmute', False)

    if mode not in ['auto', 'forced_on', 'forced_off']:
        return jsonify({"status": "error", "msg": "Invalid mode"}), 400

    with state_mgr:
        load_state()
        state['quiet_mode'] = mode
        if unmute:
            state['muted_until'] = 0
            state['safety_net_pending'] = False
        save_state()
        # Immediately recalculate actual status
        update_quiet_status()
    return jsonify({"status": "ok"})

@app.route('/api/admin/safety_net/react', methods=['POST'])
def admin_safety_net_react():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403

    data = request.get_json()
    action = data.get('action')
    value = data.get('value') # For tech mute duration

    with state_mgr:
        load_state()
        if action == 'down':
            state['safety_net_pending'] = False
            state["status"] = "down"
            # Apply standard correction (last_seen + configured interval)
            last_seen = state.get("last_seen", time.time())
            down_time_ts = last_seen + get_push_interval()
            state["went_down_at"] = down_time_ts
            log_event("down", down_time_ts)
            msg = format_event_message(False, down_time_ts, state.get("came_up_at", 0))
            threading.Thread(target=send_telegram, args=(msg,)).start()
        
        elif action == 'tech':
            minutes = int(value or 30)
            state['muted_until'] = time.time() + (minutes * 60)
            state['safety_net_pending'] = False
            
        elif action == 'dontknow':
            state['safety_net_pending'] = False
            
        save_state()

    return jsonify({"status": "ok"})

@app.route('/api/admin/logs/add', methods=['POST'])
def admin_logs_add():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403
        
    data = request.get_json()
    event = data.get('event')
    timestamp = data.get('timestamp')
    
    if not event or not timestamp:
        return jsonify({"status": "error", "msg": "Missing event or timestamp"}), 400
        
    try:
        log_event(event, float(timestamp))
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/admin/logs/<float:timestamp>', methods=['DELETE'])
def admin_logs_delete(timestamp):
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403
        
    try:
        with state_mgr:
            if os.path.exists(EVENT_LOG_FILE):
                with open(EVENT_LOG_FILE, 'r') as f:
                    logs = json.load(f)
                
                # Filter out the log with given timestamp (within small margin for float)
                new_logs = [log for log in logs if abs(log.get('timestamp', 0) - timestamp) > 0.1]
                
                with open(EVENT_LOG_FILE, 'w') as f:
                    json.dump(new_logs, f, indent=2)
                    
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/admin/service/restart', methods=['POST'])
def admin_service_restart():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403

    try:
        def restart():
            time.sleep(1)
            subprocess.run(["systemctl", "restart", "flash-monitor.service", "flash-background.service"])

        threading.Thread(target=restart).start()
        return jsonify({"status": "ok", "msg": "Services restarting..."})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/admin/schedules/sync', methods=['POST'])
def admin_schedules_sync():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403

    try:
        threading.Thread(target=sync_schedules).start()
        return jsonify({"status": "ok", "msg": "Sync triggered"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/admin/backups', methods=['GET'])
def admin_backups_list():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403
    return jsonify(list_backups())

@app.route('/api/admin/backups/create', methods=['POST'])
def admin_backups_create():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403
    name = create_backup("manual")
    return jsonify({"status": "ok", "name": name})

@app.route('/api/admin/backups/restore', methods=['POST'])
def admin_backups_restore():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403
    data = request.get_json()
    filename = data.get("filename")
    if not filename:
        return jsonify({"status": "error", "msg": "Filename required"}), 400
    
    success, msg = restore_backup(filename)
    if success:
        return jsonify({"status": "ok", "msg": "Restored successfully. Restarting services..."})
    else:
        return jsonify({"status": "error", "msg": msg}), 500

@app.route('/api/admin/security/regen_push_key', methods=['POST'])
def admin_regen_push_key():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403
    
    with state_mgr:
        load_state()
        new_key = secrets.token_urlsafe(16)
        state["secret_key"] = new_key
        save_state()
        
    return jsonify({"status": "ok", "new_key": new_key})

@app.route('/api/admin/security/regen_admin_token', methods=['POST'])
def admin_regen_token():
    if not check_admin_token():
        return jsonify({"status": "error", "msg": "Access Denied"}), 403
    
    with state_mgr:
        load_state()
        new_token = secrets.token_urlsafe(16)
        state["admin_token"] = new_token
        save_state()
        
    return jsonify({"status": "ok", "new_token": new_token})
# Initialize State
load_state()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
