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
TEXT_REPORT_STATE_FILE = os.path.join(DATA_DIR, "text_report_v2_state.json")

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
    idx = slot_idx % 48
    mins = idx * 30
    h, m = mins // 60, mins % 60
    if h == 0 and m == 0 and slot_idx > 0: return "24:00"
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

def generate_day_block_content(is_today, intervals, cfg, is_pending=False):
    if is_pending:
        # User example shows summary even for pending blocks
        return "⏳️ Графік очікується\n---\n🔆 Світло є 0 год\n✖️ Світла нема 0 год"
    
    if not intervals:
        return "⏳️ Графік очікується"

    lines = []
    total_on, total_off = 0, 0
    day_start = 0 if is_today else 48
    day_end = 48 if is_today else 96
    
    day_intervals = []
    for inv in intervals:
        if inv['end_idx'] <= day_start or inv['start_idx'] >= day_end:
            continue
        
        disp_start_idx = max(inv['start_idx'], day_start)
        disp_end_idx = min(inv['end_idx'], day_end)
        disp_dur = (disp_end_idx - disp_start_idx) * 0.5
        
        if inv['state']: total_on += disp_dur
        else: total_off += disp_dur
        
        start_str = format_slot_time(disp_start_idx)
        end_str = format_slot_time(disp_end_idx)
        
        ui_cfg = cfg.get('ui', {})
        icons = ui_cfg.get('icons', {'on': '🔆', 'off': '✖️'})
        icon = icons.get('on', '🔆') if inv['state'] else icons.get('off', '✖️')
        
        dur_val = format_duration(disp_dur)
        dur_padded = f"{dur_val:>3}"
        
        line = f"{icon} {start_str}-{end_str} ({dur_padded})"
        day_intervals.append(line)
    
    lines.append("<code>")
    lines.extend(day_intervals)
    lines.append("</code>")
    lines.append("---")
    
    on_icon = cfg.get('ui', {}).get('icons', {}).get('on', '🔆')
    off_icon = cfg.get('ui', {}).get('icons', {}).get('off', '✖️')
    lines.append(f"{on_icon} Світло є <b>{format_duration(total_on)} год</b>")
    lines.append(f"{off_icon} Світла нема <b>{format_duration(total_off)} год</b>")
    
    return "\n".join(lines)

def load_state():
    if os.path.exists(TEXT_REPORT_STATE_FILE):
        try:
            with open(TEXT_REPORT_STATE_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"date": "", "morning_msg_id": None, "combined_msg_id": None, "hashes": {}}

def save_state(state):
    with open(TEXT_REPORT_STATE_FILE, "w") as f:
        json.dump(state, f)

def main():
    now = datetime.datetime.now(KYIV_TZ)
    h = now.hour
    print(f"DEBUG: Starting main at {now.strftime('%H:%M:%S')}")
    
    if h < 6 or h >= 23:
        print(f"DEBUG: Resting period (hour {h}). Skipping.")
        return

    cfg = load_config()
    if not os.path.exists(SCHEDULE_FILE): 
        print(f"DEBUG: Schedule file missing: {SCHEDULE_FILE}")
        return
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    groups = cfg.get("settings", {}).get("groups", ["GPV36.1"])
    group = groups[0] if groups else "GPV36.1"
    print(f"DEBUG: Processing group {group}")
    group_display = group.replace('GPV', '')
    
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    state = load_state()
    if state["date"] != today_str:
        state = {"date": today_str, "morning_msg_id": None, "combined_msg_id": None, "hashes": {}}

    def get_source_info(date_str, source_key):
        s_data = data.get(source_key, {}).get(group, {}).get(date_str, {})
        slots = s_data.get('slots')
        status = s_data.get('status', 'unknown')
        is_pending = (slots is None) or (status == 'pending')
        if source_key == 'github' and slots:
            if all(s == slots[0] for s in slots) and date_str == tomorrow_str: 
                is_pending = True
        
        source_name = cfg.get('sources', {}).get(source_key, {}).get('name', source_key.capitalize())
        content = generate_day_block_content(date_str == today_str, get_all_intervals(slots) if slots else [], cfg, is_pending)
        return source_name, content, is_pending

    tomorrow_available = False
    for s_key in ['github', 'yasno']:
        _, _, is_p = get_source_info(tomorrow_str, s_key)
        if not is_p:
            tomorrow_available = True
            break

    dates_to_show = [today_str]
    if tomorrow_available:
        dates_to_show.append(tomorrow_str)

    full_content_parts = []
    for d_str in dates_to_show:
        dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
        day_title = f"📆  <b>{dt.strftime('%d.%m')}  ({DAYS_UA[dt.weekday()]})</b>"
        
        s1_name, s1_content, _ = get_source_info(d_str, 'github')
        s2_name, s2_content, _ = get_source_info(d_str, 'yasno')

        if s1_content == s2_content:
            sources_label = f"<i>[{s1_name}, {s2_name}]</i>"
            block = f"{day_title}\n{sources_label}\n\n{s1_content}"
        else:
            block = f"{day_title}\n\n<i>[{s1_name}]</i>\n{s1_content}\n\n<i>[{s2_name}]</i>\n{s2_content}"
        
        full_content_parts.append(block)

    updated_time = now.strftime('%H:%M')
    footer = f"<i>🕐 Оновлено: {updated_time}</i>"
    
    # Header and Join blocks with the orange diamond separator
    full_text = f"📈 <b>Графік групи {group_display}</b>\n\n" + "\n\n🔸️🔸️🔸️\n".join(full_content_parts)
    
    if not full_text.strip().endswith("---"):
        full_text += "\n---"
    full_text += f"\n{footer}"
    
    content_hash = hashlib.md5(full_text.encode()).hexdigest()
    report_type = "combined" if tomorrow_available else "morning"
    
    target_msg_id = state["combined_msg_id"] if tomorrow_available else state["morning_msg_id"]
    old_hash = state["hashes"].get(report_type)

    if target_msg_id:
        if old_hash == content_hash: return 
        
        url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
        payload = {"chat_id": CHAT_ID, "message_id": target_msg_id, "text": full_text, "parse_mode": "HTML", "disable_web_page_preview": True}
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            state["hashes"][report_type] = content_hash
        else:
            if tomorrow_available: state["combined_msg_id"] = None
            else: state["morning_msg_id"] = None
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": full_text, "parse_mode": "HTML", "disable_web_page_preview": True}
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            new_id = r.json()['result']['message_id']
            if tomorrow_available:
                state["combined_msg_id"] = new_id
            else:
                state["morning_msg_id"] = new_id
            state["hashes"][report_type] = content_hash
            
    save_state(state)

if __name__ == "__main__":
    main()
