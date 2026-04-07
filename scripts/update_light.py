import re

with open("light_service.py", "r") as f:
    content = f.read()

# 1. Imports
content = re.sub(
    r'import json',
    'import json\nimport asyncio\nimport aiofiles\nfrom models import AppConfig, AppState',
    content,
    count=1
)

# 2. get_config Pydantic integration
config_func_old = """def get_config():
    try:
        config_path = os.path.join(DATA_DIR, "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
            
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}"""

config_func_new = """def get_config():
    try:
        config_path = os.path.join(DATA_DIR, "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
            
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                try:
                    return AppConfig(**data).dict(exclude_unset=False, by_alias=True)
                except Exception as e:
                    print(f"Config validation error: {e}")
                    return data
    except:
        pass
    return AppConfig().dict()"""

content = content.replace(config_func_old, config_func_new)

# 3. state_mgr as async context manager
state_mgr_old = """class SafeStateContext:
    def __init__(self):
        self._lock = threading.RLock()
        self._counter = 0
        self._flock_file = None
        self.file_lock_path = STATE_LOCK_FILE

    def __enter__(self):
        self._lock.acquire()
        self._counter += 1
        if self._counter == 1:
            try:
                self._flock_file = open(self.file_lock_path, 'a')
                fcntl.flock(self._flock_file, fcntl.LOCK_EX)
            except Exception as e:
                print(f"Error acquiring file lock: {e}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._counter == 1 and self._flock_file:
                try:
                    fcntl.flock(self._flock_file, fcntl.LOCK_UN)
                    self._flock_file.close()
                except:
                    pass
                self._flock_file = None
        finally:
            self._counter -= 1
            self._lock.release()

state_mgr = SafeStateContext()"""

state_mgr_new = """class SafeStateContextAsync:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._counter = 0
        self._flock_file = None
        self.file_lock_path = STATE_LOCK_FILE

    async def __aenter__(self):
        await self._lock.acquire()
        self._counter += 1
        if self._counter == 1:
            try:
                def _acquire():
                    self._flock_file = open(self.file_lock_path, 'a')
                    fcntl.flock(self._flock_file, fcntl.LOCK_EX)
                await asyncio.to_thread(_acquire)
            except Exception as e:
                print(f"Error acquiring file lock: {e}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._counter == 1 and self._flock_file:
                def _release():
                    try:
                        fcntl.flock(self._flock_file, fcntl.LOCK_UN)
                        self._flock_file.close()
                    except:
                        pass
                await asyncio.to_thread(_release)
                self._flock_file = None
        finally:
            self._counter -= 1
            self._lock.release()

state_mgr = SafeStateContextAsync()"""

content = content.replace(state_mgr_old, state_mgr_new)

# 4. log_event
log_old = """def log_event(event_type, timestamp):
    \"\"\"
    Logs an event (up/down) to a JSON file for historical analysis.
    \"\"\"
    try:
        entry = {
            "timestamp": timestamp,
            "event": event_type,
            "date_str": datetime.datetime.fromtimestamp(timestamp, KYIV_TZ).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with state_mgr:
            logs = []
            if os.path.exists(EVENT_LOG_FILE):
                try:
                    with open(EVENT_LOG_FILE, 'r') as f:
                        content = f.read().strip()
                        if content:
                            logs = json.loads(content)
                            if not isinstance(logs, list):
                                logs = []
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
                
            logs.append(entry)
            if len(logs) > 1000: 
                logs = logs[-1000:]
                
            temp_file = EVENT_LOG_FILE + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(logs, f, indent=2)
            os.replace(temp_file, EVENT_LOG_FILE)
                
    except Exception as e:
        print(f"Failed to log event: {e}")"""

log_new = """async def log_event(event_type, timestamp):
    \"\"\"
    Logs an event (up/down) to a JSON file for historical analysis.
    \"\"\"
    try:
        entry = {
            "timestamp": timestamp,
            "event": event_type,
            "date_str": datetime.datetime.fromtimestamp(timestamp, KYIV_TZ).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        async with state_mgr:
            logs = []
            if os.path.exists(EVENT_LOG_FILE):
                try:
                    async with aiofiles.open(EVENT_LOG_FILE, 'r') as f:
                        file_content = (await f.read()).strip()
                        if file_content:
                            logs = json.loads(file_content)
                            if not isinstance(logs, list):
                                logs = []
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
                
            logs.append(entry)
            if len(logs) > 1000: 
                logs = logs[-1000:]
                
            temp_file = EVENT_LOG_FILE + '.tmp'
            async with aiofiles.open(temp_file, 'w') as f:
                await f.write(json.dumps(logs, indent=2))
            
            def _replace():
                os.replace(temp_file, EVENT_LOG_FILE)
            await asyncio.to_thread(_replace)
                
    except Exception as e:
        print(f"Failed to log event: {e}")"""

content = content.replace(log_old, log_new)

# 5. load_state
load_old = """def load_state():
    global state
    with state_mgr:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    saved_state = json.load(f)
                    state.update(saved_state)
            except Exception as e:
                print(f"Error loading state: {e}")
    
    if not state.get("secret_key"):
        with state_mgr:
            state["secret_key"] = secrets.token_urlsafe(16)
            save_state()

    if not state.get("admin_token"):
        with state_mgr:
            state["admin_token"] = secrets.token_urlsafe(16)
            save_state()"""

load_new = """async def load_state():
    global state
    async with state_mgr:
        if os.path.exists(STATE_FILE):
            try:
                async with aiofiles.open(STATE_FILE, 'r') as f:
                    file_content = await f.read()
                    saved_state = json.loads(file_content)
                    state.update(saved_state)
            except Exception as e:
                print(f"Error loading state: {e}")
                
        try:
            validated_state = AppState(**state).dict(exclude_unset=False)
            state.update(validated_state)
        except Exception as e:
            print(f"State validation error: {e}")

    if not state.get("secret_key"):
        async with state_mgr:
            state["secret_key"] = secrets.token_urlsafe(16)
            await save_state()

    if not state.get("admin_token"):
        async with state_mgr:
            state["admin_token"] = secrets.token_urlsafe(16)
            await save_state()"""

content = content.replace(load_old, load_new)

# 6. save_state
save_old = """def save_state():
    with state_mgr:
        try:
            temp_file = STATE_FILE + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(state, f)
            os.replace(temp_file, STATE_FILE)
        except Exception as e:
            print(f"Error saving state: {e}")"""

save_new = """async def save_state():
    async with state_mgr:
        try:
            temp_file = STATE_FILE + '.tmp'
            async with aiofiles.open(temp_file, 'w') as f:
                await f.write(json.dumps(state))
            def _replace():
                os.replace(temp_file, STATE_FILE)
            await asyncio.to_thread(_replace)
        except Exception as e:
            print(f"Error saving state: {e}")"""

content = content.replace(save_old, save_new)

# 7. update_quiet_status
upd_quiet_old = """def update_quiet_status():
    with state_mgr:
        q_mode = state.get("quiet_mode", "auto")
        old_status = state.get("quiet_status", "active")
        is_eligible = check_quiet_mode_eligibility()
        new_status = "quiet" if q_mode == "forced_on" else ("active" if q_mode == "forced_off" else ("quiet" if is_eligible else "active"))
        if new_status != old_status:
            state["quiet_status"] = new_status
            if new_status == "quiet":
                state["stability_start"] = time.time()
            else:
                def trigger_report():
                    try:
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        python_exec = sys.executable
                        script_path = os.path.join(base_dir, "generate_text_report.py")
                        time.sleep(2)
                        subprocess.run([python_exec, script_path, "--force-new"], check=True, cwd=base_dir)
                    except Exception as e:
                        print(f"Failed to trigger text report: {e}")
                threading.Thread(target=trigger_report).start()
            save_state()
            print(f"Quiet mode status updated to: {new_status}")"""

upd_quiet_new = """async def update_quiet_status():
    async with state_mgr:
        q_mode = state.get("quiet_mode", "auto")
        old_status = state.get("quiet_status", "active")
        is_eligible = check_quiet_mode_eligibility()
        new_status = "quiet" if q_mode == "forced_on" else ("active" if q_mode == "forced_off" else ("quiet" if is_eligible else "active"))
        if new_status != old_status:
            state["quiet_status"] = new_status
            if new_status == "quiet":
                state["stability_start"] = time.time()
            else:
                def trigger_report():
                    try:
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        python_exec = sys.executable
                        script_path = os.path.join(base_dir, "generate_text_report.py")
                        time.sleep(2)
                        subprocess.run([python_exec, script_path, "--force-new"], check=True, cwd=base_dir)
                    except Exception as e:
                        print(f"Failed to trigger text report: {e}")
                threading.Thread(target=trigger_report).start()
            await save_state()
            print(f"Quiet mode status updated to: {new_status}")"""

content = content.replace(upd_quiet_old, upd_quiet_new)

# 8. sync_schedules
sync_old = """                        with state_mgr:
                            if current_hash == state.get("last_schedule_hash"): should_alert = False
                            else: state["last_schedule_hash"] = current_hash; save_state()"""
sync_new = """                        async with state_mgr:
                            if current_hash == state.get("last_schedule_hash"): should_alert = False
                            else: state["last_schedule_hash"] = current_hash; await save_state()"""
content = content.replace(sync_old, sync_new)
content = content.replace("def sync_schedules():", "async def sync_schedules():")

# 9. monitor_loop
content = content.replace("def monitor_loop():", "async def monitor_loop():")
content = content.replace("time.sleep(5)", "await asyncio.sleep(5)")
content = content.replace("load_state()", "await load_state()")
content = content.replace("with state_mgr:", "async with state_mgr:")
content = content.replace("log_event(\"down\"", "await log_event(\"down\"")
content = content.replace("save_state()", "await save_state()")

# 10. alerts_loop
content = content.replace("def alerts_loop():", "async def alerts_loop():")
content = content.replace("time.sleep(60)", "await asyncio.sleep(60)")

# 11. schedule_loop
content = content.replace("def schedule_loop():", "async def schedule_loop():")
content = content.replace("time.sleep(65)", "await asyncio.sleep(65)")
content = content.replace("sync_schedules()", "await sync_schedules()")
content = content.replace("update_quiet_status()", "await update_quiet_status()")


with open("light_service.py", "w") as f:
    f.write(content)

