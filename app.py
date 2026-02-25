import requests
from flask import Flask, render_template, jsonify, send_from_directory, make_response
import json
from datetime import datetime
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

def format_duration(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h} год {m} хв"

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
                    
                    dev_msg = get_deviation_info(ts, evt == "up")
                    dev_html = ""
                    
                    if dev_msg:
                        # dev_msg already contains the verb and timing info
                        # format: "• Увімкнули пізніше на 10 хв"
                        dev_html = dev_msg.replace("• ", "").strip()
                    
                    next_line = f"Наступне планове: {next_range}"
                    if dev_html:
                        latest_event_text = f"{dev_html}<br>{next_line}"
                    else:
                        latest_event_text = next_line
    except Exception as e:
        print(f"Error reading events: {e}")
        pass
        
    return latest_event_text, recent_events

def get_light_status_api():
    load_state()
    with state_lock:
        status = state.get("status", "unknown")
    
    event_text, recent_events = get_power_events_data()
    
    config_path = os.path.join(DATA_DIR, "config.json")
    if not os.path.exists(config_path):
        config_path = "config.json"
        
    group_name = "36.1"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                cfg = json.load(f)
                groups = cfg.get("settings", {}).get("groups", [])
                if groups: group_name = groups[0].replace("GPV", "")
        except: pass

    res = "on" if status == "up" else "off" if status == "down" else "unknown"
    return {"status": res, "event": event_text, "history": recent_events, "group": group_name}

def get_today_schedule_text():
    try:
        from zoneinfo import ZoneInfo
        import datetime
        from light_service import get_timezone
        KYIV_TZ = get_timezone()
        DAYS_UA = {0: "Понеділок", 1: "Вівторок", 2: "Середа", 3: "Четвер", 4: "П'ятниця", 5: "Субота", 6: "Неділя"}
        
        config_path = os.path.join(DATA_DIR, "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
            
        target_group = "GPV36.1" # Default
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                cfg = json.load(f)
                groups = cfg.get("settings", {}).get("groups", [])
                if groups: target_group = groups[0]

        schedule_file = os.path.join(DATA_DIR, "last_schedules.json")
        if not os.path.exists(schedule_file):
            return "Немає даних"
            
        with open(schedule_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        now = datetime.datetime.now(KYIV_TZ)
        today_str = now.strftime("%Y-%m-%d")
        
        source_name = ""
        source_data = None
        if data.get('yasno'):
            source_data = data['yasno']
            source_name = "ДТЕК, Yasno"
        elif data.get('github'):
            source_data = data['github']
            source_name = "ДТЕК"
            
        if not source_data:
            return "Немає даних"
            
        # Prioritize target_group, fallback to first available
        if target_group in source_data:
            group_key = target_group
        else:
            group_key = list(source_data.keys())[0]
            
        schedule = source_data[group_key]
        
        if today_str not in schedule or not schedule[today_str].get('slots'):
            return "Графік відсутній"
            
        slots = schedule[today_str]['slots']
        
        intervals = []
        current_state = slots[0]
        start_idx = 0
        
        def format_slot_time(idx):
            mins = idx * 30
            return f"{mins // 60:02d}:{mins % 60:02d}"
            
        for i in range(1, 48):
            if slots[i] != current_state:
                intervals.append({
                    "state": current_state, 
                    "start": format_slot_time(start_idx), 
                    "end": format_slot_time(i), 
                    "duration": (i - start_idx) * 0.5
                })
                start_idx = i
                current_state = slots[i]
        
        intervals.append({
            "state": current_state, 
            "start": format_slot_time(start_idx), 
            "end": "24:00", 
            "duration": (48 - start_idx) * 0.5
        })

        # Merge with tomorrow if continues
        tomorrow_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if tomorrow_str in schedule and schedule[tomorrow_str].get('slots'):
            tomorrow_slots = schedule[tomorrow_str]['slots']
            if tomorrow_slots[0] == current_state:
                tom_end_idx = 48
                for i in range(1, 48):
                    if tomorrow_slots[i] != current_state:
                        tom_end_idx = i
                        break
                tom_dur = tom_end_idx * 0.5
                intervals[-1]['end'] = format_slot_time(tom_end_idx)
                intervals[-1]['duration'] += tom_dur
        else:
             intervals[-1]['end'] = "24:00"

        # Totals for TODAY only
        total_on = sum(1 for s in slots if s) * 0.5
        total_off = 24.0 - total_on
        
        def fmt_dur(hours):
            return f"{hours:g}".replace('.', ',')

        lines = []
        day_str = f"📆  {now.strftime('%d.%m')} ({DAYS_UA[now.weekday()]}) [{source_name}]:"
        lines.append(f"<div style='font-weight:bold; margin-bottom:10px; color: var(--text-primary);'>{day_str}</div>")
        
        for inv in intervals:
            icon = "🔆" if inv['state'] else "✖️"
            lines.append(f"<div style='margin-bottom: 5px; font-size: 15px;'>{icon} {inv['start']} - {inv['end']} … ({fmt_dur(inv['duration'])} год.)</div>")
            
        lines.append("<div style='margin-top:15px; margin-bottom:10px; border-top: 1px dashed var(--border-color); padding-top: 5px;'></div>")
        lines.append(f"<div style='font-size: 15px; margin-bottom: 5px;'>🔆 Світло є: {fmt_dur(total_on)} год.</div>")
        lines.append(f"<div style='font-size: 15px; margin-bottom: 10px;'>✖️ Світла нема: {fmt_dur(total_off)} год.</div>")
        
        file_mtime = os.path.getmtime(schedule_file)
        dt_mtime = datetime.datetime.fromtimestamp(file_mtime, KYIV_TZ)
        lines.append(f"<div style='font-size: 14px; opacity: 0.8;'>🕐 Оновлено: {dt_mtime.strftime('%H:%M')}</div>")
        
        return "".join(lines)
    except Exception as e:
        print(f"Error building schedule text: {e}")
        return "Помилка завантаження графіка"

def get_air_quality():
    try:
        # Load AQI settings from config
        config_path = os.path.join(DATA_DIR, "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
            
        seb_station = "17095" # Default: Symyrenka
        lat, lon = "50.408", "30.400" # Default: Borshchahivka
        loc_name = "Борщагівка (Симиренка)"
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    cfg = json.load(f)
                    aqi_cfg = cfg.get("sources", {}).get("air_quality", {})
                    if aqi_cfg:
                        seb_station = aqi_cfg.get("seb_station", seb_station)
                        lat = aqi_cfg.get("lat", lat)
                        lon = aqi_cfg.get("lon", lon)
                        loc_name = aqi_cfg.get("location_name", loc_name)
            except: pass

        # 1. Try to scrape PM data from SaveEcoBot
        pm1, pm25, pm10 = None, None, None
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            seb_r = requests.get(f"https://www.saveecobot.com/station/{seb_station}", headers=headers, timeout=10)
            if seb_r.status_code == 200:
                soup = BeautifulSoup(seb_r.text, 'html.parser')
                text = soup.get_text()
                
                import re
                pm1_match = re.search(r"PM1:\s*([\d.]+)", text)
                pm25_match = re.search(r"PM2.5:\s*([\d.]+)", text)
                pm10_match = re.search(r"PM10:\s*([\d.]+)", text)
                
                if pm1_match: pm1 = float(pm1_match.group(1))
                if pm25_match: pm25 = float(pm25_match.group(1))
                if pm10_match: pm10 = float(pm10_match.group(1))
        except Exception as e:
            print(f"SaveEcoBot scraping error: {e}")

        # 2. Fetch AQI, Temp, Humidity from Open-Meteo
        aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm2_5,pm10"
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
        
        aq_r = requests.get(aq_url, timeout=5)
        w_r = requests.get(weather_url, timeout=5)
        
        aq_data = aq_r.json() if aq_r.status_code == 200 else {}
        w_data = w_r.json() if w_r.status_code == 200 else {}
        
        current_aq = aq_data.get('current', {})
        current_w = w_data.get('current', {})
        
        aqi = current_aq.get('us_aqi', 0)
        
        # Use SaveEcoBot data if available, otherwise fallback to Open-Meteo
        final_pm1 = pm1 if pm1 is not None else None
        final_pm25 = pm25 if pm25 is not None else current_aq.get('pm2_5', "--")
        final_pm10 = pm10 if pm10 is not None else current_aq.get('pm10', "--")
        
        temp = current_w.get('temperature_2m', "--")
        hum = current_w.get('relative_humidity_2m', "--")
        
        wind_speed = current_w.get('wind_speed_10m', "--")
        wind_dir_deg = current_w.get('wind_direction_10m', None)
        wind_dir = "--"
        if wind_dir_deg is not None:
            dirs = ['Пн', 'Пн-Сх', 'Сх', 'Пд-Сх', 'Пд', 'Пд-Зх', 'Зх', 'Пн-Зх']
            ix = int((wind_dir_deg + 22.5) / 45) % 8
            wind_dir = dirs[ix]
        
        # Determine text status
        if aqi <= 50: status_text = "Відмінне"
        elif aqi <= 100: status_text = "Помірне"
        elif aqi <= 150: status_text = "Шкідливе для чутливих"
        else: status_text = "Шкідливе"
        
        return {
            "aqi": aqi, 
            "pm1": final_pm1,
            "pm25": final_pm25,
            "pm10": final_pm10,
            "temp": temp,
            "hum": hum,
            "wind_speed": wind_speed,
            "wind_dir": wind_dir,
            "text": status_text, 
            "location": loc_name, 
            "status": "ok"
        }
    except Exception as e:
        print(f"AQI/Weather Error: {e}")
    return {
        "aqi": "--", "pm1": None, "pm25": "--", "pm10": "--", 
        "temp": "--", "hum": "--", "wind_speed": "--", "wind_dir": "--",
        "text": "Невідомо", "location": "Симиренка", "status": "error"
    }

@app.route('/')
def index():
    ts = int(time.time())
    response = make_response(render_template('index.html', ts=ts))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/robots.txt')
def robots_txt():
    return "User-agent: *\nAllow: /", 200, {'Content-Type': 'text/plain'}

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def serve_sw():
    return send_from_directory('static', 'service-worker.js')


@app.route('/api/push/<secret_key>', methods=['GET'])
def push_api(secret_key):
    # Reload state to ensure we have the latest status from other workers/monitor
    load_state()
    
    with state_lock:
        if secret_key != state.get('secret_key'):
            return jsonify({"status": "error", "msg": "invalid_key"}), 403
            
        current_time = get_current_time()
        previous_status = state["status"]
        
        # Update heartbeat
        state["last_seen"] = current_time
        
        # Logic: If we were DOWN, and now we get a request -> We are UP
        if previous_status == "down" or previous_status == "unknown":
            state["status"] = "up"
            state["came_up_at"] = current_time
            log_event("up", current_time)
            
            # Calculate outage duration
            if state["went_down_at"] > 0:
                duration = format_duration(current_time - state["went_down_at"])
            else:
                duration = "невідомо"
            
            sched_light_now, current_end, next_range, next_duration = get_schedule_context()
            
            time_str = datetime.fromtimestamp(current_time, KYIV_TZ).strftime("%H:%M")
            dev_msg = get_deviation_info(current_time, True)
            
            # Header
            msg = f"🟢 <b>{time_str} Світло є!</b>\n\n"
            
            # Stats Block
            msg += "📊 <b>Статистика відключення:</b>\n"
            msg += f"• Світла не було: <b>{duration}</b>\n"
            if dev_msg:
                msg += f"{dev_msg}\n"
            
            # Schedule Block
            msg += "\n🗓 <b>Аналіз:</b>\n"
            
            sched_on_time = get_nearest_schedule_switch(current_time, True)
            if sched_on_time:
                msg += f"• За графіком світло мало з'явитися о: <b>{sched_on_time}</b>\n"
            
            if sched_light_now is False: # It appeared while it should be dark
                next_off_time = next_range.split(' - ')[1] if ' - ' in next_range else "час очікується"
                msg += f"• Наступне вимкнення: <b>{next_off_time}</b>"
            else: # It appeared while it should be light
                msg += f"• Наступне вимкнення: <b>{current_end}</b>"
            
            threading.Thread(target=send_telegram, args=(msg,)).start()
            # trigger_daily_report_update() REMOVED FOR QUIET EVENTS
        
        save_state()
    
    return jsonify({"status": "ok", "msg": "heartbeat_received"})

@app.route('/api/status')
def api_status():
    from light_service import get_timezone
    KYIV_TZ = get_timezone()
    
    alert = cached_fetch('alert', get_air_raid_alert)
    radiation = cached_fetch('radiation', get_radiation)
    light_info = cached_fetch('light', get_light_status_api)
    aqi = cached_fetch('aqi', get_air_quality)
    schedule_text = cached_fetch('schedule_text', get_today_schedule_text)
    
    return jsonify({
        "alert": alert,
        "radiation": radiation,
        "light": light_info["status"],
        "light_event": light_info["event"],
        "group": light_info.get("group", "unknown"),
        "schedule_text": schedule_text,
        "aqi": aqi,
        "timestamp": datetime.now(KYIV_TZ).strftime("%H:%M:%S")
    })

# Initialize State
load_state()
print(f"Push URL configured for key: {state.get('secret_key')}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
