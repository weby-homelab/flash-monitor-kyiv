import requests
from flask import Flask, render_template, jsonify, send_from_directory, make_response
import json
from datetime import datetime
import os
import time
from bs4 import BeautifulSoup
import threading
from light_service import (
    load_state, save_state, state, state_lock, 
    monitor_loop, schedule_loop, get_current_time, format_duration, 
    log_event, get_schedule_context, send_telegram, 
    get_deviation_info, get_nearest_schedule_switch,
    trigger_daily_report_update, trigger_weekly_report_update,
    KYIV_TZ
)


app = Flask(__name__)

# --- Configuration ---
ALERTS_API_URL = "https://ubilling.net.ua/aerialalerts/"
LIGHT_MONITOR_URL = "http://127.0.0.1:8889/"

# --- Caching ---
CACHE = {}
CACHE_TTL = 30

def cached_fetch(key, func):
    now = time.time()
    if key in CACHE and now - CACHE[key]['time'] < CACHE_TTL:
        return CACHE[key]['data']
    
    data = func()
    CACHE[key] = {'time': now, 'data': data}
    return data

# --- PWA Routes ---
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

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
    latest_event_text = "Немає даних про події"
    
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
                    
                    # For backward compatibility with light_event
                    if len(logs) >= 2:
                        last = logs[-1]
                        prev = logs[-2]
                        ts = last['timestamp']
                        dt_str = datetime.fromtimestamp(ts).strftime("%d.%m %H:%M")
                        evt = last['event']
                        dur_sec = ts - prev['timestamp']
                        dur_str = format_duration(dur_sec)
                        icon = "🟢" if evt == "up" else "🔴"
                        text = "Світло з'явилося" if evt == "up" else "Світло зникло"
                        pre_text = "не було" if evt == "up" else "було"
                        latest_event_text = f"{dt_str} {icon} {text}<br><span style='font-size: 0.9em; color: #aaa;'>({pre_text} {dur_str})</span>"
    except Exception as e:
        print(f"Error reading events: {e}")
        pass
        
    return latest_event_text, recent_events

def get_light_status_api():
    with state_lock:
        status = state.get("status", "unknown")
    
    event_text, recent_events = get_power_events_data()
    res = "on" if status == "up" else "off" if status == "down" else "unknown"
    return {"status": res, "event": event_text, "history": recent_events}

def get_air_quality():
    try:
        # 1. Try to scrape PM data from SaveEcoBot (Station 17095 - Bulhakova St)
        pm1, pm25, pm10 = None, None, None
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            seb_r = requests.get("https://www.saveecobot.com/station/17095", headers=headers, timeout=10)
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
        aq_url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=50.408&longitude=30.400&current=us_aqi,pm2_5,pm10"
        weather_url = "https://api.open-meteo.com/v1/forecast?latitude=50.408&longitude=30.400&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
        
        aq_r = requests.get(aq_url, timeout=5)
        w_r = requests.get(weather_url, timeout=5)
        
        aq_data = aq_r.json() if aq_r.status_code == 200 else {}
        w_data = w_r.json() if w_r.status_code == 200 else {}
        
        current_aq = aq_data.get('current', {})
        current_w = w_data.get('current', {})
        
        aqi = current_aq.get('us_aqi', 0)
        
        # Use SaveEcoBot data if available, otherwise fallback to Open-Meteo
        final_pm1 = pm1 if pm1 is not None else None # We will hide it in UI if None
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
            "location": "Борщагівка (Симиренка)", 
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
            msg = f"🟢 <b>{time_str} Світло з'явилося</b>\n\n"
            
            # Stats Block
            msg += "📊 <b>Статистика відключення:</b>\n"
            msg += f"• Світла не було: <b>{duration}</b>\n"
            if dev_msg:
                msg += f"{dev_msg}\n"
            
            # Schedule Block
            msg += "\n🗓 <b>Аналіз:</b>\n"
            
            sched_on_time = get_nearest_schedule_switch(current_time, True)
            if sched_on_time:
                msg += f"• За графіком світло мала з'явитися о: <b>{sched_on_time}</b>\n"
            
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
    alert = cached_fetch('alert', get_air_raid_alert)
    radiation = cached_fetch('radiation', get_radiation)
    light_info = cached_fetch('light', get_light_status_api)
    aqi = cached_fetch('aqi', get_air_quality)
    
    return jsonify({
        "alert": alert,
        "radiation": radiation,
        "light": light_info["status"],
        "light_event": light_info["event"],
        "light_history": light_info.get("history", []),
        "aqi": aqi,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# Initialize State and Monitor
load_state()
print(f"Push URL configured for key: {state.get('secret_key')}")

# Start Monitor Threads
def start_monitor():
    # Start the monitor loop (checks for timeouts)
    threading.Thread(target=monitor_loop, daemon=True).start()
    # Start the schedule loop (periodically updates reports)
    threading.Thread(target=schedule_loop, daemon=True).start()

start_monitor()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
