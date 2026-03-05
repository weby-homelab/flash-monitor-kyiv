import pytest
import datetime
from zoneinfo import ZoneInfo
from light_service import format_event_message

KYIV_TZ = ZoneInfo("Europe/Kyiv")

from unittest.mock import patch

def test_format_event_message_very_soon_outage():
    # Light comes on at 19:29:50 (10 seconds before 19:30)
    event_time = datetime.datetime(2026, 3, 5, 19, 29, 50, tzinfo=KYIV_TZ).timestamp()
    prev_event_time = datetime.datetime(2026, 3, 5, 16, 40, 0, tzinfo=KYIV_TZ).timestamp()
    
    # Mock next_info to simulate an event in 10 seconds
    mock_next_info = {
        "time_left_sec": 10,
        "interval": "19:30-22:00"
    }
    
    with patch("light_service.get_next_scheduled_event", return_value=mock_next_info):
        with patch("light_service.get_deviation_info", return_value=None):
            msg = format_event_message(True, event_time, prev_event_time)
            
            assert "❌ Вимкнення через ~ менше хвилини" in msg
            assert "🗓 (19:30-22:00)" in msg

def test_short_duration_formatting():
    from light_service import format_duration
    # Current behavior of format_duration for < 60s is "0 хв"
    assert format_duration(30) == "0 хв"
    assert format_duration(60) == "1 хв"
