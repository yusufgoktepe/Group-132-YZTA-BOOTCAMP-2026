"""SQLite bağlantısı, şema kurulumu ve referans veri aktarımı.

Ek bağımlılık eklememek için standart kütüphanedeki ``sqlite3`` kullanılır.
Veritabanı dosyası ``CAMPUSMATCH_DB_PATH`` ortam değişkeni ile değiştirilebilir;
testler bu sayede geçici bir dosya üzerinde çalışır.
"""

from __future__ import annotations

import csv
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Iterator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA_DIR = PROJECT_ROOT / "data" / "sample"
DEFAULT_DB_PATH = PROJECT_ROOT / "backend" / "campusmatch.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS clubs (
    club_id            TEXT PRIMARY KEY,
    club_name          TEXT NOT NULL,
    category           TEXT NOT NULL DEFAULT '',
    description        TEXT NOT NULL DEFAULT '',
    target_departments TEXT NOT NULL DEFAULT '',
    target_interests   TEXT NOT NULL DEFAULT '',
    activity_level     TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS events (
    event_id           TEXT PRIMARY KEY,
    club_id            TEXT NOT NULL REFERENCES clubs(club_id),
    university_id      TEXT NOT NULL DEFAULT '',
    title              TEXT NOT NULL,
    description        TEXT NOT NULL DEFAULT '',
    category           TEXT NOT NULL DEFAULT '',
    event_type         TEXT NOT NULL DEFAULT '',
    level              TEXT NOT NULL DEFAULT '',
    date               TEXT NOT NULL DEFAULT '',
    time               TEXT NOT NULL DEFAULT '',
    location           TEXT NOT NULL DEFAULT '',
    location_type      TEXT NOT NULL DEFAULT '',
    quota              INTEGER NOT NULL DEFAULT 0,
    target_interests   TEXT NOT NULL DEFAULT '',
    target_departments TEXT NOT NULL DEFAULT '',
    target_goals       TEXT NOT NULL DEFAULT '',
    fee_type           TEXT NOT NULL DEFAULT '',
    language           TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS students (
    student_id            TEXT PRIMARY KEY,
    name                  TEXT NOT NULL DEFAULT '',
    school_type           TEXT NOT NULL DEFAULT '',
    university_or_school  TEXT NOT NULL DEFAULT '',
    department            TEXT NOT NULL DEFAULT '',
    grade                 TEXT NOT NULL DEFAULT '',
    interests             TEXT NOT NULL DEFAULT '',
    career_goals          TEXT NOT NULL DEFAULT '',
    skill_level           TEXT NOT NULL DEFAULT '',
    preferred_event_types TEXT NOT NULL DEFAULT '',
    availability          TEXT NOT NULL DEFAULT '',
    location_preference   TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS profiles (
    profile_id                  TEXT PRIMARY KEY,
    schema_version              TEXT NOT NULL,
    education_reference_version TEXT NOT NULL,
    display_name                TEXT NOT NULL DEFAULT '',
    university_id               TEXT NOT NULL,
    university_name             TEXT NOT NULL,
    program_id                  TEXT NOT NULL,
    program_name                TEXT NOT NULL,
    education_level             TEXT NOT NULL,
    program_duration            INTEGER NOT NULL,
    class_year                  TEXT NOT NULL,
    interest_ids                TEXT NOT NULL,
    participation_goal_ids      TEXT NOT NULL,
    participation_modes         TEXT NOT NULL,
    fee_preference              TEXT NOT NULL,
    language_preference         TEXT NOT NULL,
    campus_id                   TEXT,
    created_at                  TEXT NOT NULL,
    updated_at                  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id     TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    event_id       TEXT NOT NULL REFERENCES events(event_id),
    action         TEXT NOT NULL CHECK (action IN ('like', 'skip', 'save', 'unsave', 'view_detail')),
    dwell_ms       INTEGER,
    created_at     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_interactions_profile ON interactions(profile_id, created_at);
CREATE INDEX IF NOT EXISTS idx_interactions_event ON interactions(event_id, action);
"""

# Mobil uygulama ve sentetik etkileşim verisi aynı etkinlik kimliklerini kullanır.
JSON_PROFILE_FIELDS = ("interest_ids", "participation_goal_ids", "participation_modes")


def get_db_path() -> Path:
    override = os.environ.get("CAMPUSMATCH_DB_PATH")
    return Path(override) if override else DEFAULT_DB_PATH


def connect() -> sqlite3.Connection:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_connection() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency: istek başına bağlantı açar ve kapatır."""
    connection = connect()
    try:
        yield connection
    finally:
        connection.close()


def _read_csv(filename: str) -> list[dict[str, str]]:
    with (SAMPLE_DATA_DIR / filename).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _to_int(value: str, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _ensure_event_columns(connection: sqlite3.Connection) -> None:
    """Önceki geliştirme veritabanlarını veri kaybetmeden günceller."""
    existing = {
        row["name"] for row in connection.execute("PRAGMA table_info(events)").fetchall()
    }
    for column in ("time", "location"):
        if column not in existing:
            connection.execute(
                f"ALTER TABLE events ADD COLUMN {column} TEXT NOT NULL DEFAULT ''"
            )


def _upsert(connection: sqlite3.Connection, table: str, key: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    columns = list(rows[0])
    placeholders = ", ".join("?" for _ in columns)
    updates = ", ".join(f"{column} = excluded.{column}" for column in columns if column != key)
    statement = (
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) "
        f"ON CONFLICT({key}) DO UPDATE SET {updates}"
    )
    connection.executemany(statement, [tuple(row[column] for column in columns) for row in rows])
    return len(rows)


def seed_reference_data(connection: sqlite3.Connection) -> dict[str, int]:
    """Kulüp, etkinlik ve örnek öğrenci verisini CSV'den veritabanına aktarır.

    Idempotenttir: aynı kimlikler tekrar çalıştırıldığında güncellenir, çoğaltılmaz.
    Kullanıcı profilleri ve etkileşimleri bu işlemden etkilenmez.
    """
    clubs = [
        {
            "club_id": row["club_id"],
            "club_name": row["club_name"],
            "category": row.get("category", ""),
            "description": row.get("description", ""),
            "target_departments": row.get("target_departments", ""),
            "target_interests": row.get("target_interests", ""),
            "activity_level": row.get("activity_level", ""),
        }
        for row in _read_csv("clubs_sample.csv")
    ]
    events = [
        {
            "event_id": row["event_id"],
            "club_id": row["club_id"],
            "university_id": row.get("university_id", ""),
            "title": row["title"],
            "description": row.get("description", ""),
            "category": row.get("category", ""),
            "event_type": row.get("event_type", ""),
            "level": row.get("level", ""),
            "date": row.get("date", ""),
            "time": row.get("time", ""),
            "location": row.get("location", ""),
            "location_type": row.get("location_type", ""),
            "quota": _to_int(row.get("quota", "0")),
            "target_interests": row.get("target_interests", ""),
            "target_departments": row.get("target_departments", ""),
            "target_goals": row.get("target_goals", ""),
            "fee_type": row.get("fee_type", ""),
            "language": row.get("language", ""),
        }
        for row in _read_csv("events_sample.csv")
    ]
    students = [
        {
            "student_id": row["student_id"],
            "name": row.get("name", ""),
            "school_type": row.get("school_type", ""),
            "university_or_school": row.get("university_or_school", ""),
            "department": row.get("department", ""),
            "grade": row.get("grade", ""),
            "interests": row.get("interests", ""),
            "career_goals": row.get("career_goals", ""),
            "skill_level": row.get("skill_level", ""),
            "preferred_event_types": row.get("preferred_event_types", ""),
            "availability": row.get("availability", ""),
            "location_preference": row.get("location_preference", ""),
        }
        for row in _read_csv("students_sample.csv")
    ]

    with connection:
        counts = {
            "clubs": _upsert(connection, "clubs", "club_id", clubs),
            "events": _upsert(connection, "events", "event_id", events),
            "students": _upsert(connection, "students", "student_id", students),
        }
    return counts


def init_db(connection: sqlite3.Connection | None = None) -> dict[str, int]:
    """Şemayı kurar ve referans veriyi yükler. Uygulama açılışında çağrılır."""
    owned = connection is None
    connection = connection or connect()
    try:
        with connection:
            connection.executescript(SCHEMA)
            _ensure_event_columns(connection)
        return seed_reference_data(connection)
    finally:
        if owned:
            connection.close()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def profile_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Profil satırındaki JSON kolonlarını listeye çevirir."""
    profile = dict(row)
    for field in JSON_PROFILE_FIELDS:
        profile[field] = json.loads(profile[field])
    return profile
