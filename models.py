from pydantic import BaseModel, Field, RootModel, ConfigDict
from typing import Dict, List, Optional, Any, Union

class AppSettings(BaseModel):
    model_config = ConfigDict(extra='ignore')
    timezone: str = "Europe/Kyiv"
    push_interval: int = 30
    safety_net_timeout: int = 35
    admin_chat_id: str = "6313526220"
    telegram_bot_token: Optional[str] = None
    telegram_channel_id: Optional[str] = None
    groups: List[str] = ["GPV_1"]

class Notifications(BaseModel):
    model_config = ConfigDict(extra='ignore')
    report_times: List[str] = ["06:00", "09:00", "20:00"]
    mute_during_night: bool = False
<<<<<<< Updated upstream
    telegram_air_raid_alerts: bool = True
=======
    telegram_air_raid_alerts: bool = False
>>>>>>> Stashed changes

class SourcesConfig(BaseModel):
    model_config = ConfigDict(extra='ignore')
    air_quality: Dict[str, Any] = {"lat": "50.45", "lon": "30.52", "seb_station": "17095", "location_name": "Київ"}

class AdvancedSettings(BaseModel):
    model_config = ConfigDict(extra='ignore')
    notifications: Notifications = Notifications()
    retention: Dict[str, int] = {"event_log_days": 30, "schedule_history_days": 14}
    data_sources: Dict[str, Any] = {"priority": "yasno"}
    dashboard: Dict[str, bool] = {"show_aq": True, "show_radiation": True, "show_temp_graph": True, "show_charts": True}

class AppConfig(BaseModel):
    model_config = ConfigDict(extra='ignore')
    settings: AppSettings = AppSettings()
    sources: SourcesConfig = SourcesConfig()
    advanced: AdvancedSettings = AdvancedSettings()
    ui: Dict[str, Any] = {}

class AppState(BaseModel):
    model_config = ConfigDict(extra='ignore')
    status: str = "unknown"
    last_seen: float = 0.0
    went_down_at: float = 0.0
    came_up_at: float = 0.0
    secret_key: Optional[str] = None
    alert_status: str = "clear"
    quiet_mode: str = "auto"
    quiet_status: str = "active"
    pending_confirmation: bool = False
    safety_net_pending: bool = False
    safety_net_sent_at: float = 0.0
    safety_net_triggered_for: float = 0.0
    muted_until: float = 0.0
    stability_start: float = 0.0
    admin_token: Optional[str] = None
    last_schedule_hash: Optional[str] = None
    alert_start_time: Optional[float] = None

class ScheduleDay(BaseModel):
    model_config = ConfigDict(extra='ignore')
    status: str = "unknown"
    slots: Optional[List[Union[bool, None]]] = None

class ScheduleGroup(RootModel):
    root: Dict[str, ScheduleDay]

class SchedulesData(BaseModel):
    model_config = ConfigDict(extra='ignore')
    yasno: Optional[Dict[str, Dict[str, ScheduleDay]]] = None
    github: Optional[Dict[str, Dict[str, ScheduleDay]]] = None
