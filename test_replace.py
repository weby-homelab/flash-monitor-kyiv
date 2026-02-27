import sys

with open('/root/geminicli/flash-monitor-kyiv/generate_text_report.py', 'r') as f:
    text = f.read()

old = """    for d_idx, d_str in enumerate([today_str, tomorrow_str]):
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

        day_title = f"{icons.get('calendar', '📆')}  <b>{dt.strftime('%d.%m')} ({DAYS_UA[dt.weekday()]})</b>"
        group_display = group.replace('GPV', '')
        if len(source_blocks) == 2 and source_blocks[0][1] == source_blocks[1][1]:
            sources_label = f"<i>[{source_blocks[0][0]}, {source_blocks[1][0]}]</i>"
            content = f"{day_title}\n{sources_label}\n{source_blocks[0][1]}"
        else:
            blocks = [day_title]
            for name, txt in source_blocks:
                blocks.append(f"<i>[{name}]</i>\n{txt}")
            content = "\n\n".join(blocks)

        updated_text = cfg.get('ui', {}).get('text', {}).get('updated', 'Оновлено')
        footer = f"<i>{icons.get('clock', '🕐')} {updated_text}: {now.strftime('%H:%M')}</i>"
        full_text = f"📈 <b>Графік групи {group_display}</b>\n\n{content}\n\n{footer}"
        
        content_hash = hashlib.md5(full_text.encode()).hexdigest()
        
        date_info = report_state.get(d_str, {})
        last_id = date_info.get("message_id")
        last_hash = date_info.get("hash")

        if last_id:
            if last_hash == content_hash:
                continue
            
            url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            payload = {"chat_id": CHAT_ID, "message_id": last_id, "text": full_text, "parse_mode": "HTML", "disable_web_page_preview": True}
            r = requests.post(url, json=payload)
            if r.status_code == 200:
                report_state[d_str] = {"message_id": last_id, "hash": content_hash}
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": full_text, "parse_mode": "HTML", "disable_web_page_preview": True}
            r = requests.post(url, json=payload)
            if r.status_code == 200:
                new_id = r.json()['result']['message_id']
                report_state[d_str] = {"message_id": new_id, "hash": content_hash}
        
        save_report_state(report_state)"""

new = """    all_day_contents = []
    
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

        day_title = f"{icons.get('calendar', '📆')}  <b>{dt.strftime('%d.%m')} ({DAYS_UA[dt.weekday()]})</b>"
        if len(source_blocks) == 2 and source_blocks[0][1] == source_blocks[1][1]:
            sources_label = f"<i>[{source_blocks[0][0]}, {source_blocks[1][0]}]</i>"
            day_content = f"{day_title}\n{sources_label}\n{source_blocks[0][1]}"
        else:
            blocks = [day_title]
            for name, txt in source_blocks:
                blocks.append(f"<i>[{name}]</i>\n{txt}")
            day_content = "\n\n".join(blocks)
            
        all_day_contents.append(day_content)

    if not all_day_contents:
        return

    group_display = group.replace('GPV', '')
    combined_content = "\n\n\n".join(all_day_contents)

    updated_text = cfg.get('ui', {}).get('text', {}).get('updated', 'Оновлено')
    footer = f"<i>{icons.get('clock', '🕐')} {updated_text}: {now.strftime('%H:%M')}</i>"
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
            save_report_state(report_state)"""

if old in text:
    print("Found! Replacing...")
    with open('/root/geminicli/flash-monitor-kyiv/generate_text_report.py', 'w') as f:
        f.write(text.replace(old, new))
else:
    print("Not found!")
