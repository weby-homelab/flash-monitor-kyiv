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
CONFIG_FILE = "config.json"
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

def format_slot_time(slot_idx, is_end=False):
    idx = slot_idx % 48
    mins = idx * 30
    h, m = mins // 60, mins % 60
    if h == 0 and m == 0 and is_end and slot_idx > 0: return "24:00"
    return f"{h:02d}:{m:02d}"

def get_all_intervals(slots):
    if not slots: return []
    intervals = []
    current_state = slots[0]
    start_idx = 0
    for i in range(1, len(slots)):
        if slots[i] != current_state:
            intervals.append({
                "state": current_state, 
                "start_idx": start_idx, 
                "end_idx": i,
                "duration": (i - start_idx) * 0.5
            })
            start_idx = i
            current_state = slots[i]
    intervals.append({
        "state": current_state, 
        "start_idx": start_idx, 
        "end_idx": len(slots),
        "duration": (len(slots) - start_idx) * 0.5
    })
    return intervals

def format_duration(hours):
    if hours == int(hours): return str(int(hours))
    return f"{hours:g}".replace('.', ',')

def generate_day_block(is_today, intervals, cfg):
    lines = []
    total_on, total_off = 0, 0
    day_start = 0 if is_today else 48
    day_end = 48 if is_today else 96
    
    day_intervals = []
    for inv in intervals:
        if inv['end_idx'] <= day_start or inv['start_idx'] >= day_end:
            continue
        
        disp_start = max(inv['start_idx'], day_start)
        disp_end = min(inv['end_idx'], day_end)
        disp_dur = (disp_end - disp_start) * 0.5
        
        if inv['state']: total_on += disp_dur
        else: total_off += disp_dur
        
        start_str = format_slot_time(disp_start, is_end=False)
        end_str = format_slot_time(disp_end, is_end=True)
             
        icon = cfg.get('ui', {}).get('icons', {}).get('on', '🔆')
        off_icon = cfg.get('ui', {}).get('icons', {}).get('off', '✖️')
        icon_to_use = icon if inv['state'] else off_icon
        
        duration_text = f"({format_duration(disp_dur)} год.)"
        
        line = f"{icon_to_use} {start_str} - {end_str} {duration_text:>10}"
        day_intervals.append(line)
    
    lines.append("---")
    lines.extend(day_intervals)
    lines.append("---")
    
    on_icon = cfg.get('ui', {}).get('icons', {}).get('on', '🔆')
    off_icon = cfg.get('ui', {}).get('icons', {}).get('off', '✖️')
    lines.append(f"{on_icon} Світло є: {format_duration(total_on)} год.")
    lines.append(f"{off_icon} Світла нема: {format_duration(total_off)} год.")
    lines.append("---")
    
    return "\n".join(lines)

def get_report_state():
    if os.path.exists(TEXT_REPORT_ID_FILE):
        try:
            with open(TEXT_REPORT_ID_FILE, "r") as f:
                data = json.load(f)
                if "message_id" in data and "date" in data:
                    return {data["date"]: {"message_id": data["message_id"], "hash": data.get("hash")}}
                return data
        except: pass
    return {}

def save_report_state(state):
    with open(TEXT_REPORT_ID_FILE, "w") as f:
        if len(state) > 3:
            sorted_dates = sorted(state.keys())
            state = {k: state[k] for k in sorted_dates[-3:]}
        json.dump(state, f)

def main():
    now = datetime.datetime.now(KYIV_TZ)
    current_time = now.time()
    
    if not (datetime.time(6, 0) <= current_time <= datetime.time(23, 45)):
        return

    cfg = load_config()
    if not os.path.exists(SCHEDULE_FILE): return
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    groups = cfg.get("settings", {}).get("groups", ["GPV36.1"])
    group = groups[0] if groups else "GPV36.1"
    icons = cfg.get('ui', {}).get('icons', {'calendar': '📆', 'on': '🔆', 'off': '✖️', 'clock': '🕐'})
    
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    report_state = get_report_state()
    
    all_day_contents = []
    
    for d_idx, d_str in enumerate([today_str, tomorrow_str]):
        is_today = (d_idx == 0)
        dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
        
        source_blocks = []
        has_real_tomorrow_data = False
        
        for s_key in ['github', 'yasno']:
            s_data = data.get(s_key, {}).get(group, {})
            
            combined_slots = []
            s_today = s_data.get(today_str, {}).get('slots')
            s_tomorrow = s_data.get(tomorrow_str, {}).get('slots')
            
            if not is_today and s_tomorrow:
                has_real_tomorrow_data = True

            if s_today:
                combined_slots.extend(s_today)
                if s_tomorrow:
                    combined_slots.extend(s_tomorrow)
                else:
                    combined_slots.extend([None] * 48)
            
            if combined_slots and any(x is not None for x in combined_slots):
                clean_slots = [val if val is not None else (True if i < 48 else False) for i, val in enumerate(combined_slots)]
                intervals = get_all_intervals(clean_slots)
                # Ensure source name is fetched from config
                source_cfg = cfg.get('sources', {}).get(s_key, {})
                source_name = source_cfg.get('name', s_key.capitalize())
                source_blocks.append((source_name, generate_day_block(is_today, intervals, cfg)))
        
        if not is_today and not has_real_tomorrow_data:
            continue
            
        if not source_blocks: continue

        day_title = f"{icons.get('calendar', '📆')}  {dt.strftime('%d.%m')} ({DAYS_UA[dt.weekday()]})"
        if len(source_blocks) == 2 and source_blocks[0][1] == source_blocks[1][1]:
            sources_label = f"[{source_blocks[0][0]}, {source_blocks[1][0]}]"
            day_content = f"{day_title}\n{sources_label}\n{source_blocks[0][1]}"
        else:
            blocks = [day_title]
            for name, txt in source_blocks:
                blocks.append(f"[{name}]\n{txt}")
            day_content = "\n".join(blocks)
            
        all_day_contents.append(day_content)

    if not all_day_contents:
        return
        
    group_display = group.replace('GPV', '')
    combined_content = "\n\n".join(all_day_contents)

    updated_text = cfg.get('ui', {}).get('text', {}).get('updated', 'Оновлено')
    footer = f"🕐 {updated_text}: {now.strftime('%H:%M')}"
    full_text = f"📈 <b>Графік групи {group_display}</b>\n\n{combined_content}\n\n{footer}"
    
    content_hash = hashlib.md5(full_text.encode()).hexdigest()
    
    date_info = report_state.get(today_str, {})
    last_id = date_info.get("message_id")
    last_hash = date_info.get("hash")

    if last_id:
        if last_hash != content_hash:
            url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            payload = {"chat_id": CHAT_ID, "message_id": last_id, "text": full_text, "parse_mode": "HTML", "disable_web_page_preview": True}
            r = requests.post(url, json=payload)
            if r.status_code == 200:
                report_state[today_str] = {"message_id": last_id, "hash": content_hash}
                save_report_state(report_state)
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": full_text, "parse_mode": "HTML", "disable_web_page_preview": True}
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            new_id = r.json()['result']['message_id']
            report_state[today_str] = {"message_id": new_id, "hash": content_hash}
            save_report_state(report_state)

if __name__ == "__main__":
    main()
