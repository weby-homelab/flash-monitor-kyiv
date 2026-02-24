import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

KYIV_TZ = ZoneInfo("Europe/Kyiv")
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
        url = YASNO_URL.format(
            region_id=yasno_cfg.get('region_id', '25'),
            dso_id=yasno_cfg.get('dso_id', '902')
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
                res[grp][d_str] = {"slots": None, "status": "pending"}
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

def update_local_schedules(config_path: str, output_path: str):
    try:
        with open(config_path, "r") as f:
            cfg = json.load(f)
        
        gh_data = fetch_github(cfg)
        ys_data = fetch_yasno(cfg)
        
        cache = {
            "github": extract_github(gh_data, cfg),
            "yasno": extract_yasno(ys_data, cfg),
            "last_update": datetime.now(KYIV_TZ).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(output_path, "w") as f:
            json.dump(cache, f, indent=2)
        print(f"Local schedules updated successfully at {cache['last_update']}")
        return True
    except Exception as e:
        print(f"Failed to update local schedules: {e}")
        return False
