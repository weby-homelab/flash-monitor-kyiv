import json
import os
import datetime
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import sys
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
DATA_DIR = os.environ.get("DATA_DIR", ".")
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
EVENT_LOG_FILE = os.path.join(DATA_DIR, "event_log.json")
SCHEDULE_FILE = os.path.join(DATA_DIR, "last_schedules.json")
HISTORY_FILE = os.path.join(DATA_DIR, "schedule_history.json")
REPORT_ID_FILE = os.path.join(DATA_DIR, "daily_report_id.json")
KYIV_TZ = ZoneInfo("Europe/Kyiv")

def load_events():
    if not os.path.exists(EVENT_LOG_FILE):
        return []
    try:
        with open(EVENT_LOG_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def load_schedule_slots(target_date):
    """
    Returns the list of 48 boolean slots (True=Light, False=Outage) for the target date.
    Checks last_schedules.json first, then schedule_history.json.
    """
    date_str = target_date.strftime("%Y-%m-%d")
    
    # 1. Try last_schedules.json (current/future)
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, 'r') as f:
                data = json.load(f)
            
            # Priority: Yasno -> Github
            source = data.get('yasno') or data.get('github')
            if source:
                group_key = list(source.keys())[0]
                schedule_data = source[group_key]
                
                if date_str in schedule_data and schedule_data[date_str].get('slots'):
                     return schedule_data[date_str]['slots']
        except Exception as e:
            print(f"Error loading schedule: {e}")

    # 2. Try schedule_history.json (past)
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                if date_str in history:
                    return history[date_str]
        except Exception as e:
            print(f"Error loading history: {e}")
            
    # If no schedule found, assume Light (True) for the whole day
    return [True] * 48

def get_intervals_for_date(target_date, events):
    """
    Returns a list of (start_time, end_time, state) for the target date.
    """
    
    # Target date range
    day_start = datetime.datetime.combine(target_date, datetime.time.min).replace(tzinfo=KYIV_TZ)
    day_end = datetime.datetime.combine(target_date, datetime.time.max).replace(tzinfo=KYIV_TZ)
    
    # If target is today, clip the calculation end to NOW for stats, 
    # but the chart X-axis will still cover the full day.
    now = datetime.datetime.now(KYIV_TZ)
    if target_date == now.date():
        calc_end = now
    else:
        calc_end = day_end

    # Sort events by timestamp
    events.sort(key=lambda x: x['timestamp'])
    
    intervals = []
    
    # Determine initial state at 00:00
    current_state = "unknown"
    
    # Find the last event BEFORE the start of the day
    for event in events:
        if event['timestamp'] < day_start.timestamp():
            current_state = event['event']
        else:
            break
            
    current_time = day_start
    
    # Iterate through events strictly within the day
    for event in events:
        event_ts = event['timestamp']
        event_dt = datetime.datetime.fromtimestamp(event_ts, KYIV_TZ)
        
        if event_dt < day_start:
            continue
        if event_dt > calc_end:
            break
            
        # Add interval from current_time to this event
        if current_time < event_dt:
            intervals.append((current_time, event_dt, current_state))
            
        current_time = event_dt
        current_state = event['event']
        
    # Add final interval to end of calculation period
    if current_time < calc_end:
        intervals.append((current_time, calc_end, current_state))
        
    return intervals

def get_schedule_intervals(target_date, slots):
    """
    Converts 48 boolean slots into time intervals for the chart.
    Returns list of (start_time, duration_hours, is_light)
    """
    if not slots: return []
    
    intervals = []
    day_start = datetime.datetime.combine(target_date, datetime.time.min).replace(tzinfo=KYIV_TZ)
    
    current_state = slots[0]
    start_idx = 0
    
    for i in range(1, 48):
        if slots[i] != current_state:
            # End of block
            end_idx = i
            
            # Create interval
            start_time = day_start + datetime.timedelta(minutes=start_idx*30)
            duration = (end_idx - start_idx) * 0.5 # hours
            intervals.append((start_time, duration, current_state))
            
            # Start new block
            current_state = slots[i]
            start_idx = i
            
    # Final block
    start_time = day_start + datetime.timedelta(minutes=start_idx*30)
    duration = (48 - start_idx) * 0.5
    intervals.append((start_time, duration, current_state))
    
    return intervals

def format_duration(seconds):
    total_minutes = round(seconds / 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h} год {m} хв"

def generate_chart(target_date, intervals, schedule_intervals, theme='dark'):
    # Amethyst Mist Palette
    if theme == 'dark':
        bg_color = '#120B1F'
        card_color = '#1E1633'
        text_color = '#F0E6FF'
        fact_on_color = '#67E8F9'
        fact_off_color = '#FF6B81'
        plan_on_color = '#C4B5FD'
        plan_off_color = '#475569'
        plt_style = 'dark_background'
    else:
        bg_color = '#F7F4FF'
        card_color = '#FFFFFF'
        text_color = '#1a0933'
        fact_on_color = '#88E8C8'
        fact_off_color = '#FF6B81'
        plan_on_color = '#A78BFA'
        plan_off_color = '#94A3B8'
        plt_style = 'default'

    with plt.style.context(plt_style):
        fig, ax = plt.subplots(figsize=(10, 2.0), facecolor=bg_color)
        ax.set_facecolor(bg_color)
        
        # Define geometries - Glued together
        sched_y = 12.5
        sched_h = 2.5
        act_y = 15
        act_h = 2.5
        
        day_start = datetime.datetime.combine(target_date, datetime.time.min).replace(tzinfo=KYIV_TZ)
        day_end = datetime.datetime.combine(target_date, datetime.time.max).replace(tzinfo=KYIV_TZ)
        
        # --- Schedule Data (Bottom Bar) ---
        sched_color_map = {True: plan_on_color, False: plan_off_color}
        
        if schedule_intervals:
            for start, duration_hours, is_light in schedule_intervals:
                color = sched_color_map.get(is_light, plan_off_color)
                start_num = mdates.date2num(start)
                duration_days = duration_hours / 24.0
                ax.broken_barh([(start_num, duration_days)], (sched_y, sched_h), facecolors=color, edgecolor='none')

        # --- Separator Line (Background Color) ---
        ax.axhline(y=15, color=bg_color, linewidth=0.5, zorder=5)

        # --- Hour Markers on the Bars (Background Color) ---
        hour_points = []
        for h in range(0, 25):
            point_time = datetime.datetime.combine(target_date, datetime.time.min).replace(tzinfo=KYIV_TZ) + datetime.timedelta(hours=h)
            hour_points.append(mdates.date2num(point_time))
            
        ax.vlines(hour_points, 12.5, 17.5, colors=bg_color, linewidth=0.8, zorder=10)

        # --- Actual Data (Top Bar) ---
        color_map = {'up': fact_on_color, 'down': fact_off_color, 'unknown': fact_on_color}
        
        total_up = 0
        total_down = 0
        
        for start, end, state in intervals:
            duration_sec = (end - start).total_seconds()
            if state == 'up':
                total_up += duration_sec
            elif state == 'down':
                total_down += duration_sec
            elif state == 'unknown':
                total_up += duration_sec
                
            color = color_map.get(state, fact_on_color)
            
            start_num = mdates.date2num(start)
            end_num = mdates.date2num(end)
            duration_num = end_num - start_num
            
            ax.broken_barh([(start_num, duration_num)], (act_y, act_h), facecolors=color, edgecolor='none')

        # --- Formatting ---
        ax.set_ylim(11, 19) 
        ax.set_xlim(mdates.date2num(day_start), mdates.date2num(day_end))
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color(text_color)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=KYIV_TZ))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2, tz=KYIV_TZ))
        ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1, tz=KYIV_TZ))
        
        ax.tick_params(axis='x', colors=text_color)
        ax.tick_params(axis='y', colors=text_color)
        
        ax.set_yticks([sched_y + sched_h/2, act_y + act_h/2])
        ax.set_yticklabels(['Графік', 'Факт'], color=text_color)
        
        ax.set_title(f"Статистика світла за {target_date.strftime('%d.%m.%Y')}", fontsize=12, color=text_color)
        
        import matplotlib.patches as mpatches
        green_patch = mpatches.Patch(color=fact_on_color, label=f'Світло є')
        red_patch = mpatches.Patch(color=fact_off_color, label=f'Світла немає')
        yellow_patch = mpatches.Patch(color=plan_on_color, label='Графік: Є')
        gray_patch = mpatches.Patch(color=plan_off_color, label='Графік: Немає')
        
        legend = plt.legend(handles=[green_patch, red_patch, yellow_patch, gray_patch], 
                   loc='upper center', bbox_to_anchor=(0.5, -0.25),
                   fancybox=False, frameon=False, shadow=False, ncol=4, fontsize='small')
        plt.setp(legend.get_texts(), color=text_color)

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.35)
        
        suffix = "_light" if theme == 'light' else ""
        filename = f"report_{target_date.strftime('%Y-%m-%d')}{suffix}.png"
        plt.savefig(filename, dpi=100, facecolor=fig.get_facecolor())
        plt.close()
        
    return filename, total_up, total_down

def get_last_report_id(target_date):
    if os.path.exists(REPORT_ID_FILE):
        try:
            with open(REPORT_ID_FILE, 'r') as f:
                data = json.load(f)
                # Ensure data is a dictionary
                if isinstance(data, dict):
                    date_str = target_date.strftime("%Y-%m-%d")
                    # Backwards compatibility: if old format, check and return
                    if 'date' in data and 'message_id' in data:
                         if data.get('date') == date_str:
                             return data.get('message_id')
                         else:
                             return None
                    # New format: a mapping of date_str -> message_id
                    return data.get(date_str)
        except:
            pass
    return None

def save_report_id(message_id, target_date):
    data = {}
    if os.path.exists(REPORT_ID_FILE):
        try:
            with open(REPORT_ID_FILE, 'r') as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, dict):
                    # Migration: if old format, convert to new format
                    if 'date' in loaded_data and 'message_id' in loaded_data:
                        old_date = loaded_data['date']
                        old_id = loaded_data['message_id']
                        data[old_date] = old_id
                    else:
                        data = loaded_data
        except:
            pass
            
    date_str = target_date.strftime("%Y-%m-%d")
    data[date_str] = message_id
    
    # Keep only the last 3 entries to avoid unbounded growth
    if len(data) > 3:
        # Sort by date and keep only the latest 3
        sorted_keys = sorted(data.keys())
        keys_to_remove = sorted_keys[:-3]
        for k in keys_to_remove:
            del data[k]
            
    try:
        with open(REPORT_ID_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def update_telegram_photo(message_id, photo_path, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageMedia"
    
    media_json = json.dumps({
        'type': 'photo',
        'media': 'attach://chart',
        'caption': caption,
        'parse_mode': 'HTML'
    })
    
    with open(photo_path, 'rb') as f:
        files = {'chart': f}
        data = {
            'chat_id': CHAT_ID,
            'message_id': message_id,
            'media': media_json
        }
        try:
            r = requests.post(url, files=files, data=data, timeout=20)
            if r.status_code == 200:
                print("Report updated successfully.")
                return True
            else:
                print(f"Failed to update report: {r.text}")
                return False
        except Exception as e:
            print(f"Error updating report: {e}")
            return False

def send_telegram_photo(photo_path, caption, target_date):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(photo_path, 'rb') as f:
        files = {'photo': f}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML', 'disable_notification': True}
        try:
            r = requests.post(url, files=files, data=data, timeout=10)
            if r.status_code == 200:
                print("Report sent successfully.")
                res = r.json()
                if res.get('ok'):
                    msg_id = res['result']['message_id']
                    save_report_id(msg_id, target_date)
            else:
                print(f"Failed to send report: {r.text}")
        except Exception as e:
            print(f"Error sending report: {e}")

if __name__ == "__main__":
    target_date = datetime.datetime.now(KYIV_TZ).date()
    
    # Simple argument parsing
    for arg in sys.argv[1:]:
        if arg == "--no-send":
            continue
        try:
            target_date = datetime.datetime.strptime(arg, "%Y-%m-%d").date()
        except ValueError:
            pass # Ignore non-date arguments
        
    print(f"Generating report for {target_date}...")
    
    events = load_events()
    slots = load_schedule_slots(target_date)
    
    intervals = get_intervals_for_date(target_date, events)
    sched_intervals = get_schedule_intervals(target_date, slots)
    
    if not intervals:
        day_start = datetime.datetime.combine(target_date, datetime.time.min).replace(tzinfo=KYIV_TZ)
        now = datetime.datetime.now(KYIV_TZ)
        calc_end = now if target_date == now.date() else day_start + datetime.timedelta(hours=24)
        intervals = [(day_start, calc_end, "unknown")]

    filename, t_up, t_down = generate_chart(target_date, intervals, sched_intervals, theme='dark')
    filename_light, _, _ = generate_chart(target_date, intervals, sched_intervals, theme='light')
    
    # Save copy for Web Dashboard
    web_dir = os.path.join(DATA_DIR, "static")
    if not os.path.exists(web_dir): os.makedirs(web_dir)
    shutil.copy(filename, os.path.join(web_dir, "chart.png"))
    shutil.copy(filename_light, os.path.join(web_dir, "chart_light.png"))
    
    caption = (f"📊 <b>Звіт за {target_date.strftime('%d.%m.%Y')}</b>\n\n"
               f"💡 Світло було: <b>{format_duration(t_up)}</b>\n"
               f"❌ Світла не було: <b>{format_duration(t_down)}</b>")

    if slots:
        plan_up_cnt = sum(1 for s in slots if s)
        plan_up_sec = plan_up_cnt * 1800  # 30 min * 60 sec
        
        diff_sec = t_up - plan_up_sec
        diff_hours = diff_sec / 3600
        sign = "+" if diff_hours > 0 else ""
        
        compliance_pct = (t_up / plan_up_sec * 100) if plan_up_sec > 0 else 0
        
        # Save stats for Web Dashboard
        try:
            stats_data = {
                "plan_up": format_duration(plan_up_sec),
                "fact_up": format_duration(t_up),
                "diff": diff_hours,
                "pct": int(compliance_pct),
                "updated_at": datetime.datetime.now(KYIV_TZ).strftime("%H:%M")
            }
            with open(os.path.join(web_dir, "stats.json"), "w") as f:
                json.dump(stats_data, f)
        except Exception as e:
            print(f"Error saving stats json: {e}")
        
        caption += f"\n\n📉 <b>План vs Факт:</b>\n"
        caption += f" • За планом світло: <b>{format_duration(plan_up_sec)}</b>\n"
        caption += f" • Реально світло: <b>{format_duration(t_up)}</b>\n"
        caption += f" • Відхилення: <b>{sign}{diff_hours:.1f}год</b> (Світла {compliance_pct:.0f}% від плану)"
               
    if "--no-send" not in sys.argv:
        # Check if we can update an existing message
        last_id = get_last_report_id(target_date)
        if last_id:
            print(f"Updating existing report (ID: {last_id})...")
            sent = update_telegram_photo(last_id, filename, caption)
            if not sent:
                print("Update failed, but NOT sending a new message to avoid spam.")
        else:
            print("No report ID for today. Sending new report...")
            send_telegram_photo(filename, caption, target_date)
    else:
        print("Telegram sending skipped (--no-send).")
    
    if os.path.exists(filename):
        os.remove(filename)
    if os.path.exists(filename_light):
        os.remove(filename_light)
