import threading
import time
from datetime import datetime
from typing import Any

from app.arduino import arduino
from app.database import get_last_portion_ms, get_schedules

_scheduler_thread: threading.Thread | None = None
_scheduler_stop = threading.Event()
_scheduler_app = None
_last_triggered: dict[int, str] = {}


def _trigger_schedule(schedule: dict[str, Any], when: datetime) -> bool:
    schedule_id = int(schedule.get('id', -1))
    when_key = when.strftime('%Y-%m-%d %H:%M')
    if schedule_id in _last_triggered and _last_triggered[schedule_id] == when_key:
        return False

    portion_multiplier = max(1, int(schedule.get('portion', 1)))
    milliseconds = max(0, int(get_last_portion_ms()) * portion_multiplier)
    ok, response, error = arduino.send_command(f'DISPENSE:{milliseconds}')
    _last_triggered[schedule_id] = when_key
    return ok


def process_due_schedules(now: datetime | None = None) -> list[dict[str, Any]]:
    current = now or datetime.now()
    current_time = current.strftime('%H:%M')
    triggered: list[dict[str, Any]] = []

    for schedule in get_schedules():
        if schedule.get('time') != current_time:
            continue

        item = {
            'id': schedule.get('id'),
            'time': schedule.get('time'),
            'portion': schedule.get('portion'),
            'triggered_at': current.isoformat(timespec='seconds'),
        }
        if _trigger_schedule(schedule, current):
            triggered.append(item)

    return triggered


def _scheduler_loop() -> None:
    while not _scheduler_stop.is_set():
        try:
            if _scheduler_app is not None:
                with _scheduler_app.app_context():
                    process_due_schedules()
            else:
                process_due_schedules()
        except Exception:
            pass
        time.sleep(30)


def start_scheduler(app=None) -> threading.Thread | None:
    global _scheduler_thread, _scheduler_app

    if app is not None:
        _scheduler_app = app

    if app is not None and app.config.get('TESTING'):
        return None

    if _scheduler_thread is not None and _scheduler_thread.is_alive():
        return _scheduler_thread

    _scheduler_stop.clear()
    _scheduler_thread = threading.Thread(target=_scheduler_loop, name='feedy-scheduler', daemon=True)
    _scheduler_thread.start()
    return _scheduler_thread


def stop_scheduler() -> None:
    _scheduler_stop.set()
