import json
import os
import datetime
from zoneinfo import ZoneInfo
import requests
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
DATA_DIR = os.environ.get("DATA_DIR", ".")
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
CONFIG_FILE = "config.json" # Config usually stays with code
SCHEDULE_FILE = os.path.join(DATA_DIR, "last_schedules.json")
TEXT_REPORT_ID_FILE = os.path.join(DATA_DIR, "text_report_id.json")
def get_timezone():
    try:
        config_path = os.path.join(DATA_DIR, "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                cfg = json.load(f)
                tz_name = cfg.get("settings", {}).get("timezone", "Europe/Kyiv")
                return ZoneInfo(tz_name)
    except: pass
    return ZoneInfo("Europe/Kyiv")

KYIV_TZ = get_timezone()

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
            intervals.append({"state": current_state, "start": format_slot_time(start_idx), "end": format_slot_time(i), "duration": (i - start_idx) * 0.5})
            start_idx = i
            current_state = slots[i]
    intervals.append({"state": current_state, "start": format_slot_time(start_idx), "end": "24:00", "duration": (48 - start_idx) * 0.5})
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
    total_on, total_off = 0, 0
    for inv in intervals:
        icon = cfg['ui']['icons']['on'] if inv['state'] else cfg['ui']['icons']['off']
        lines.append(f"{icon} {inv['start']} - {inv['end']} … ({format_duration(inv['duration'])} год.)")
        if inv['state']: total_on += inv['duration']
        else: total_off += inv['duration']
    lines.append("---\n" + f"{cfg['ui']['icons']['on']} Світло є: {format_duration(total_on)} год.\n" + f"{cfg['ui']['icons']['off']} Світла нема: {format_duration(total_off)} год.\n---")
    return "\n".join(lines)

def get_report_state():
    if os.path.exists(TEXT_REPORT_ID_FILE):
        try:
            with open(TEXT_REPORT_ID_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {}

def save_report_state(msg_id, date_str, content_hash):
    with open(TEXT_REPORT_ID_FILE, "w") as f:
        json.dump({"message_id": msg_id, "date": date_str, "hash": content_hash}, f)

def main():
    now = datetime.datetime.now(KYIV_TZ)
    
    # 1. Time Restriction (06:00 - 22:30)
    current_time = now.time()
    if not (datetime.time(6, 0) <= current_time <= datetime.time(22, 30)):
        print(f"Skipping text report: current time {now.strftime('%H:%M')} is outside 06:00-22:30")
        return

    cfg = load_config()
    if not os.path.exists(SCHEDULE_FILE): return
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Safe access to icons and formatting
    ui_cfg = cfg.get('ui', {})
    icons = ui_cfg.get('icons', {'calendar': '📆', 'pending': '⏳', 'on': '🔆', 'off': '✖️'})
    format_cfg = ui_cfg.get('format', {'header_template': "🔆 Графік групи {group} 🔆", 'footer_template': "🕐 Оновлено: {time}\n© 2026 Weby Homelab"})
    
    header = format_cfg.get('header_template', "🔆 Графік групи {group} 🔆").format(group=group.replace("GPV", ""))
    
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    report_sections = []
    # Build core content for hash comparison (without footer time)
    for d_str in [today_str, tomorrow_str]:
        dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
        day_title = f"{icons.get('calendar', '📆')}  {dt.strftime('%d.%m')} ({DAYS_UA[dt.weekday()]})"
        source_texts = []
        for s_key in ['github', 'yasno']:
            s_data = data.get(s_key, {}).get(group, {})
            if d_str in s_data and s_data[d_str].get('slots'):
                source_name = cfg.get('sources', {}).get(s_key, {}).get('name', s_key.capitalize())
                source_texts.append((source_name, generate_text_for_day(d_str, s_data, cfg)))
        
        if not source_texts:
            pending_text = ui_cfg.get('text', {}).get('pending', 'Графік очікується')
            report_sections.append(f"{day_title}:\n\n{icons.get('pending', '⏳')} {pending_text}")
        elif len(source_texts) == 2 and source_texts[0][1] == source_texts[1][1]:
            report_sections.append(f"{day_title} [{source_texts[0][0]}, {source_texts[1][0]}]:\n\n{source_texts[0][1]}")
        else:
            for i, (name, txt) in enumerate(source_texts):
                sep = f"\n{cfg['ui']['format']['separator_source']}\n" if i > 0 else ""
                report_sections.append(f"{sep}{day_title} [{name}]:\n\n{txt}")

    core_content = "\n".join(report_sections)
    content_hash = hashlib.md5(core_content.encode()).hexdigest()
    
    clock_icon = icons.get('clock', '🕐')
    updated_text = ui_cfg.get('text', {}).get('updated', 'Оновлено')
    footer = f"\n{clock_icon} {updated_text}: {now.strftime('%H:%M')} (Київ)\n© 2026 Weby Homelab"
    full_text = f"<b>{header}</b>\n\n{core_content}\n\n---\n{footer}"
    
    state = get_report_state()
    last_id = state.get("message_id")
    last_date = state.get("date")
    last_hash = state.get("hash")

    # 2. Logic: One day one graph, edit only on change
    if last_id and last_date == today_str:
        if last_hash == content_hash:
            print("No changes in schedule data. Skipping edit.")
            return
        
        # Data changed, try to edit
        url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
        payload = {"chat_id": CHAT_ID, "message_id": last_id, "text": full_text, "parse_mode": "HTML", "disable_web_page_preview": True}
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            save_report_state(last_id, today_str, content_hash)
            print("Text report updated (data changed).")
            return

    # 3. Send new message (new day or failed edit)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": full_text, "parse_mode": "HTML", "disable_web_page_preview": True}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        new_id = r.json()['result']['message_id']
        save_report_state(new_id, today_str, content_hash)
        print("New daily text report sent.")

if __name__ == "__main__":
    main()
