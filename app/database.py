import sqlite3
from typing import Any

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(_error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            portion INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    existing_portion = db.execute(
        "SELECT value FROM settings WHERE key = 'last_portion_ms'"
    ).fetchone()
    if existing_portion is None:
        db.execute(
            "INSERT INTO settings (key, value) VALUES ('last_portion_ms', '1200')"
        )

    schedule_count = db.execute("SELECT COUNT(*) FROM schedules").fetchone()[0]
    if schedule_count == 0:
        db.executemany(
            "INSERT INTO schedules (time, portion) VALUES (?, ?)",
            [('10:00', 2), ('14:00', 2)]
        )

    db.commit()


def get_last_portion_ms() -> int:
    db = get_db()
    result = db.execute(
        "SELECT value FROM settings WHERE key = 'last_portion_ms'"
    ).fetchone()
    if result is None:
        return 1200
    try:
        return int(result['value'])
    except (TypeError, ValueError):
        return 1200


def save_last_portion_ms(milliseconds: int) -> int:
    value = int(milliseconds)
    db = get_db()
    db.execute(
        "INSERT INTO settings (key, value) VALUES ('last_portion_ms', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (str(value),),
    )
    db.commit()
    return value


def get_schedules() -> list[dict[str, Any]]:
    db = get_db()
    rows = db.execute(
        "SELECT id, time, portion FROM schedules ORDER BY time ASC"
    ).fetchall()
    return [
        {'id': row['id'], 'time': row['time'], 'portion': row['portion']}
        for row in rows
    ]


def add_schedule(time: str, portion: int) -> dict[str, Any]:
    db = get_db()
    cursor = db.execute(
        "INSERT INTO schedules (time, portion) VALUES (?, ?)",
        (time, int(portion)),
    )
    db.commit()
    return {'id': cursor.lastrowid, 'time': time, 'portion': int(portion)}


def delete_schedule(schedule_id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM schedules WHERE id = ?", (int(schedule_id),))
    db.commit()
