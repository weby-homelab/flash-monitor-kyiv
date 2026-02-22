import json
import os
import datetime
from zoneinfo import ZoneInfo
import requests
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
CONFIG_FILE = "config.json"
SCHEDULE_FILE = "last_schedules.json"
TEXT_REPORT_ID_FILE = "text_report_id.json"
KYIV_TZ = ZoneInfo("Europe/Kyiv")

DAYS_UA = {0: "Понеділок", 1: "Вівторок", 2: "Середа", 3: "Четвер", 4: "П'ятниця", 5: "Субота", 6: "Неділя"}

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def format_slot_time(slot_idx):
    mins = slot_idx * 30
    h, m = mins // 60, mins % 60
    return f"{h:02d}:{m:02d}"

def get_intervals(slots):
    if not slots: return []
    intervals = []
    current_state = slots[0]
    start_idx = 0
    
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
    return intervals

def format_duration(hours):
    if hours == int(hours): return str(int(hours))
    return f"{hours:g}".replace('.', ',')

def generate_text_for_day(date_str, source_data, cfg):
    day_data = source_data.get(date_str)
    if not day_data or not day_data.get('slots'):
        return f"{cfg['ui']['icons']['pending']} {cfg['ui']['text']['pending']}"
    
    intervals = get_intervals(day_data['slots'])
    lines = []
    total_on = 0
    total_off = 0
    
    for inv in intervals:
        icon = cfg['ui']['icons']['on'] if inv['state'] else cfg['ui']['icons']['off']
        duration_str = f"({format_duration(inv['duration'])} год.)"
        lines.append(f"{icon} {inv['start']} - {inv['end']} … {duration_str}")
        if inv['state']: total_on += inv['duration']
        else: total_off += inv['duration']
        
    lines.append("---")
    lines.append(f"{cfg['ui']['icons']['on']} Світло є: {format_duration(total_on)} год.")
    lines.append(f"{cfg['ui']['icons']['off']} Світла нема: {format_duration(total_off)} год.")
    lines.append("---")
    
    return "\n".join(lines)

def generate_full_report():
    cfg = load_config()
    if not os.path.exists(SCHEDULE_FILE): return "Скедуль-файл не знайдено."
    
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    group = cfg['settings']['groups'][0]
    header = cfg['ui']['format']['header_template'].format(group=group.replace("GPV36.1", "36.1"))
    
    now = datetime.datetime.now(KYIV_TZ)
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    report_sections = []
    
    for d_str in [today_str, tomorrow_str]:
        dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
        day_title = f"{cfg['ui']['icons']['calendar']}  {dt.strftime('%d.%m')} ({DAYS_UA[dt.weekday()]})"
        
        sources_present = []
        source_texts = {}
        
        for s_key in ['github', 'yasno']:
            s_data = data.get(s_key, {}).get(group, {})
            if d_str in s_data and s_data[d_str].get('slots'):
                txt = generate_text_for_day(d_str, s_data, cfg)
                source_texts[s_key] = txt
                sources_present.append(s_key)
        
        if not sources_present:
            report_sections.append(f"{day_title}:\n\n{cfg['ui']['icons']['pending']} {cfg['ui']['text']['pending']}")
            continue

        if len(sources_present) == 2 and source_texts['github'] == source_texts['yasno']:
            combined_names = f"[{cfg['sources']['github']['name']}, {cfg['sources']['yasno']['name']}]"
            report_sections.append(f"{day_title} {combined_names}:\n\n{source_texts['github']}")
        else:
            for i, s_key in enumerate(sources_present):
                s_name = f"[{cfg['sources'][s_key]['name']}]"
                sep = f"\n{cfg['ui']['format']['separator_source']}\n" if i > 0 else ""
                report_sections.append(f"{sep}{day_title} {s_name}:\n\n{source_texts[s_key]}")

    footer = f"{cfg['ui']['icons']['clock']} {cfg['ui']['text']['updated']}: {now.strftime('%d.%m.%Y %H:%M')} (Київ)"
    day_sep = f"\n{cfg['ui']['format']['separator_day']}\n"
    return f"{header}\n\n" + day_sep.join(report_sections) + f"\n{footer}"

def get_last_msg_id():
    if os.path.exists(TEXT_REPORT_ID_FILE):
        try:
            with open(TEXT_REPORT_ID_FILE, "r") as f:
                return json.load(f).get("message_id")
        except: return None
    return None

def save_msg_id(msg_id):
    with open(TEXT_REPORT_ID_FILE, "w") as f:
        json.dump({"message_id": msg_id}, f)

def send_to_telegram(text):
    last_id = get_last_msg_id()
    if last_id:
        url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
        payload = {"chat_id": CHAT_ID, "message_id": last_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
        r = requests.post(url, json=payload)
        if r.status_code == 200: return
            
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        save_msg_id(r.json()['result']['message_id'])

if __name__ == "__main__":
    report_text = generate_full_report()
    send_to_telegram(report_text)
