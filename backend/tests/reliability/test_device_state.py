from datetime import datetime, timedelta, timezone

from app.services.device_state import (
    check_offline_devices,
    devices,
    touch_device,
)


def setup_function() -> None:
    devices.clear()


def test_timeout_marks_online_device_offline_once() -> None:
    now = datetime(2026, 9, 24, tzinfo=timezone.utc)
    touch_device("FF01", now=now - timedelta(seconds=11))

    first = check_offline_devices(now=now, timeout_seconds=10)
    second = check_offline_devices(now=now + timedelta(seconds=2), timeout_seconds=10)

    assert first == ["FF01"]
    assert second == []
    assert devices["FF01"]["device_status"] == "OFFLINE"


def test_valid_message_recovers_offline_device_and_updates_last_seen() -> None:
    old = datetime(2026, 9, 24, tzinfo=timezone.utc)
    touch_device("FF01", now=old)
    check_offline_devices(now=old + timedelta(seconds=11), timeout_seconds=10)
    latest = old + timedelta(seconds=12)

    recovered = touch_device("FF01", now=latest)

    assert recovered is True
    assert devices["FF01"]["device_status"] == "ONLINE"
    assert devices["FF01"]["last_seen"] == latest.isoformat()
