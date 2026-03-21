import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

def get_timezone():
    try:
        data_dir = os.environ.get("DATA_DIR", ".")
        config_path = os.path.join(data_dir, "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                cfg = json.load(f)
                tz_name = cfg.get("settings", {}).get("timezone", "Europe/Kyiv")
                return ZoneInfo(tz_name)
    except: pass
    return ZoneInfo("Europe/Kyiv")

KYIV_TZ = get_timezone()
GITHUB_URL = "https://raw.githubusercontent.com/Baskerville42/outage-data-ua/main/data/{region}.json"
YASNO_URL = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/{region_id}/dsos/{dso_id}/planned-outages"

def fetch_github(cfg: dict) -> Optional[dict]:
    if not cfg.get('sources', {}).get('github', {}).get('enabled', False):
        return None
    try:
        url = GITHUB_URL.format(region=cfg['settings'].get('region', 'kyiv'))
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"GitHub fetch error: {e}")
        return None

def fetch_yasno(cfg: dict) -> Optional[dict]:
    yasno_cfg = cfg.get('sources', {}).get('yasno', {})
    if not yasno_cfg.get('enabled', False):
        return None
    try:
        region_id = str(yasno_cfg.get('region_id', '25'))
        dso_id = str(yasno_cfg.get('dso_id', '902'))
        
        # Security validation: Ensure IDs are numeric to prevent URL manipulation
        if not (region_id.isdigit() and dso_id.isdigit()):
            print(f"Yasno fetch error: Invalid IDs detected (region_id={region_id}, dso_id={dso_id})")
            return None

        url = YASNO_URL.format(
            region_id=region_id,
            dso_id=dso_id
        )
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Yasno fetch error: {e}")
        return None

def parse_github_day(day_data: dict) -> list[bool]:
    slots = []
    for h in range(1, 25):
        s = day_data.get(str(h), "yes")
        if s == "yes": slots.extend([True, True])
        elif s == "no": slots.extend([False, False])
        elif s == "first": slots.extend([False, True])
        elif s == "second": slots.extend([True, False])
        else: slots.extend([True, True])
    return slots

def extract_github(data: dict, cfg: dict) -> dict:
    res = {}
    if not data: return res
    fact = data.get("fact", {}).get("data", {})
    for grp in cfg['settings'].get('groups', []):
        res[grp] = {}
        for ts in sorted(fact.keys(), key=int)[:3]:
            d = fact.get(ts, {}).get(grp)
            if not d: continue
            dt = datetime.fromtimestamp(int(ts), tz=KYIV_TZ)
            d_str = dt.strftime("%Y-%m-%d")
            if all(d.get(str(h), "yes") == "yes" for h in range(1, 25)):
                res[grp][d_str] = {"slots": [True] * 48, "status": "normal"}
            else:
                res[grp][d_str] = {"slots": parse_github_day(d), "status": "normal"}
    return res

def extract_yasno(data: dict, cfg: dict) -> dict:
    res = {}
    if not data: return res
    for grp in cfg['settings'].get('groups', []):
        key = grp.replace("GPV", "")
        if key not in data: continue
        res[grp] = {}
        for day in ["today", "tomorrow"]:
            d = data[key].get(day)
            if not d or "date" not in d: continue
            dt = datetime.fromisoformat(d["date"])
            d_str = dt.strftime("%Y-%m-%d")
            status = d.get("status", "")
            if status == "EmergencyShutdowns":
                res[grp][d_str] = {"slots": None, "status": "emergency"}
            elif not d.get("slots"):
                res[grp][d_str] = {"slots": None, "status": "pending"}
            else:
                slots = [True] * 48
                for s in d["slots"]:
                    start, end = s.get("start", 0) // 30, s.get("end", 0) // 30
                    is_on = (s.get("type") == "NotPlanned")
                    for i in range(start, min(end, 48)): slots[i] = is_on
                res[grp][d_str] = {"slots": slots, "status": "normal"}
    return res

def has_schedule_changed(old_cache: dict, new_cache: dict) -> bool:
    if not old_cache:
        return False
        
    for source in ['yasno', 'github']:
        if source not in new_cache:
            continue
            
        old_src = old_cache.get(source, {})
        new_src = new_cache[source]
        
        if not old_src:
            continue
            
        for group, new_dates in new_src.items():
            old_dates = old_src.get(group, {})
            for date_str, new_data in new_dates.items():
                old_data = old_dates.get(date_str)
                if not old_data or old_data.get('slots') != new_data.get('slots'):
                    return True
    return False

def update_local_schedules(config_path: str, output_path: str):
    try:
        with open(config_path, "r") as f:
            cfg = json.load(f)

        gh_data = fetch_github(cfg)
        ys_data = fetch_yasno(cfg)

        github_cache = extract_github(gh_data, cfg)
        yasno_cache = extract_yasno(ys_data, cfg)

        old_cache = {}
        if os.path.exists(output_path):
            try:
                with open(output_path, "r") as f:
                    old_cache = json.load(f)
            except Exception:
                pass

        new_cache = {}
        if github_cache:
            new_cache["github"] = github_cache
        if yasno_cache:
            new_cache["yasno"] = yasno_cache
            
        has_changed = has_schedule_changed(old_cache, new_cache)
            
        new_cache["last_update"] = datetime.now(KYIV_TZ).strftime("%Y-%m-%d %H:%M:%S")

        with open(output_path, "w") as f:
            json.dump(new_cache, f, indent=2)

        # Update schedule_history.json to preserve historical plans
        data_dir = os.environ.get("DATA_DIR", ".")
        history_path = os.path.join(data_dir, "schedule_history.json")
        history = {}
        if os.path.exists(history_path):
            try:
                with open(history_path, "r") as f:
                    history = json.load(f)
            except Exception:
                pass

        # Collect all dates from all available caches
        all_dates = set()
        if yasno_cache:
            for grp in yasno_cache:
                all_dates.update(yasno_cache[grp].keys())
        if github_cache:
            for grp in github_cache:
                all_dates.update(github_cache[grp].keys())

        history_updated = False
        for date_str in all_dates:
            # Find merged slots for this date across all sources (False wins)
            merged_new_slots = None
            for cache in [yasno_cache, github_cache]:
                if not cache: continue
                # We assume all groups in a cache for the same region have similar behavior or we pick the first
                grp = list(cache.keys())[0]
                day_data = cache[grp].get(date_str)
                if day_data and day_data.get("slots"):
                    s = day_data["slots"]
                    if merged_new_slots is None:
                        merged_new_slots = list(s)
                    else:
                        for i in range(min(len(merged_new_slots), len(s))):
                            if s[i] is False: merged_new_slots[i] = False
            
            if merged_new_slots:
                # Protective Merge: If day exists in history, preserve ALL existing False (outage) slots.
                # Never allow a Light slot (True) to overwrite an Outage slot (False) in history.
                if date_str in history:
                    old_slots = history[date_str].get("slots", [True] * 48)
                    final_slots = [
                        (old_slots[i] if old_slots[i] is False else merged_new_slots[i])
                        for i in range(min(len(old_slots), len(merged_new_slots)))
                    ]
                    history[date_str] = {"slots": final_slots}
                else:
                    history[date_str] = {"slots": merged_new_slots}
                history_updated = True

        if history_updated:
            with open(history_path, "w") as f:
                json.dump(history, f, indent=2)

        print(f"Local schedules updated successfully at {new_cache['last_update']}. Changed: {has_changed}")
        return True, has_changed
    except Exception as e:
        print(f"Failed to update local schedules: {e}")
        return False, False
