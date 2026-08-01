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
V3_SAMPLE_DATA_DIR = SAMPLE_DATA_DIR / "v3"
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
    location_type      TEXT NOT NULL DEFAULT '',
    quota              INTEGER NOT NULL DEFAULT 0,
    target_interests   TEXT NOT NULL DEFAULT '',
    target_departments TEXT NOT NULL DEFAULT '',
    target_goals       TEXT NOT NULL DEFAULT '',
    fee_type           TEXT NOT NULL DEFAULT '',
    language           TEXT NOT NULL DEFAULT '',
    schema_version     TEXT NOT NULL DEFAULT '2.0',
    organizer_id       TEXT,
    event_tier         TEXT NOT NULL DEFAULT 'official',
    campus_id          TEXT,
    city_id            TEXT,
    category_id        TEXT NOT NULL DEFAULT '',
    interest_ids       TEXT NOT NULL DEFAULT '[]',
    target_program_ids TEXT NOT NULL DEFAULT '[]',
    target_class_years TEXT NOT NULL DEFAULT '[]',
    target_goal_ids    TEXT NOT NULL DEFAULT '[]',
    starts_at          TEXT,
    ends_at            TEXT,
    expires_at         TEXT,
    participation_mode TEXT,
    location_name      TEXT,
    fee_amount         REAL,
    status             TEXT NOT NULL DEFAULT 'published',
    approval_status    TEXT NOT NULL DEFAULT 'approved',
    organizer_trust_score REAL NOT NULL DEFAULT 5.0,
    image_url          TEXT
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
    action         TEXT NOT NULL CHECK (action IN ('like', 'skip', 'save', 'unsave', 'view_detail', 'apply')),
    dwell_ms       INTEGER,
    interaction_key TEXT,
    feed_token     TEXT,
    created_at     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_interactions_profile ON interactions(profile_id, created_at);
CREATE INDEX IF NOT EXISTS idx_interactions_event ON interactions(event_id, action);

CREATE TABLE IF NOT EXISTS organizers (
    organizer_id        TEXT PRIMARY KEY,
    schema_version      TEXT NOT NULL DEFAULT '3.0',
    user_id             TEXT,
    organizer_type      TEXT NOT NULL CHECK (organizer_type IN ('student', 'club', 'university', 'municipality', 'company')),
    display_name        TEXT NOT NULL,
    university_id       TEXT,
    verification_status TEXT NOT NULL CHECK (verification_status IN ('pending', 'verified', 'rejected')),
    trust_score         REAL NOT NULL DEFAULT 5.0 CHECK (trust_score BETWEEN 0 AND 5),
    rating_count        INTEGER NOT NULL DEFAULT 0 CHECK (rating_count >= 0),
    is_blacklisted      INTEGER NOT NULL DEFAULT 0 CHECK (is_blacklisted IN (0, 1)),
    blacklist_reason    TEXT,
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS participations (
    participation_id   TEXT PRIMARY KEY,
    schema_version     TEXT NOT NULL DEFAULT '3.0',
    profile_id         TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    event_id           TEXT NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    status             TEXT NOT NULL CHECK (status IN ('requested', 'approved', 'rejected', 'cancelled', 'attended', 'no_show')),
    attendance_verified INTEGER NOT NULL DEFAULT 0 CHECK (attendance_verified IN (0, 1)),
    requested_at       TEXT NOT NULL,
    verified_at        TEXT,
    UNIQUE(profile_id, event_id)
);

CREATE TABLE IF NOT EXISTS ratings (
    rating_id          TEXT PRIMARY KEY,
    schema_version     TEXT NOT NULL DEFAULT '3.0',
    event_id           TEXT NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    organizer_id       TEXT NOT NULL REFERENCES organizers(organizer_id) ON DELETE CASCADE,
    rater_profile_id   TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    score              INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
    created_at         TEXT NOT NULL,
    UNIQUE(event_id, rater_profile_id)
);

CREATE TABLE IF NOT EXISTS user_interest_weights (
    profile_id         TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    interest_id        TEXT NOT NULL,
    schema_version     TEXT NOT NULL DEFAULT '3.0',
    weight             REAL NOT NULL CHECK (weight BETWEEN 0 AND 1),
    explicit_weight    REAL NOT NULL CHECK (explicit_weight BETWEEN 0 AND 1),
    behavior_weight    REAL NOT NULL DEFAULT 0 CHECK (behavior_weight BETWEEN -1 AND 1),
    updated_at         TEXT NOT NULL,
    PRIMARY KEY(profile_id, interest_id)
);

CREATE TABLE IF NOT EXISTS moderation_actions (
    moderation_action_id TEXT PRIMARY KEY,
    schema_version       TEXT NOT NULL DEFAULT '3.0',
    organizer_id         TEXT NOT NULL REFERENCES organizers(organizer_id) ON DELETE CASCADE,
    event_id             TEXT REFERENCES events(event_id) ON DELETE SET NULL,
    action_type          TEXT NOT NULL CHECK (action_type IN ('publish_block', 'feed_removal', 'manual_review', 'warning', 'restore')),
    reason               TEXT NOT NULL,
    status               TEXT NOT NULL CHECK (status IN ('open', 'resolved', 'dismissed')),
    created_at           TEXT NOT NULL,
    resolved_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_organizers_trust ON organizers(is_blacklisted, trust_score);
CREATE INDEX IF NOT EXISTS idx_participations_profile ON participations(profile_id, status);
CREATE INDEX IF NOT EXISTS idx_ratings_organizer ON ratings(organizer_id, created_at);
"""

EVENT_V3_COLUMNS: dict[str, str] = {
    "schema_version": "TEXT NOT NULL DEFAULT '2.0'",
    "organizer_id": "TEXT",
    "event_tier": "TEXT NOT NULL DEFAULT 'official'",
    "campus_id": "TEXT",
    "city_id": "TEXT",
    "category_id": "TEXT NOT NULL DEFAULT ''",
    "interest_ids": "TEXT NOT NULL DEFAULT '[]'",
    "target_program_ids": "TEXT NOT NULL DEFAULT '[]'",
    "target_class_years": "TEXT NOT NULL DEFAULT '[]'",
    "target_goal_ids": "TEXT NOT NULL DEFAULT '[]'",
    "starts_at": "TEXT",
    "ends_at": "TEXT",
    "expires_at": "TEXT",
    "participation_mode": "TEXT",
    "location_name": "TEXT",
    "fee_amount": "REAL",
    "status": "TEXT NOT NULL DEFAULT 'published'",
    "approval_status": "TEXT NOT NULL DEFAULT 'approved'",
    "organizer_trust_score": "REAL NOT NULL DEFAULT 5.0",
    "image_url": "TEXT",
}

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


def _read_csv_path(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _to_int(value: str, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def _to_bool_int(value: str | bool | int) -> int:
    return int(str(value).strip().lower() in {"1", "true", "yes"})


def _json_array(value: str) -> str:
    return json.dumps(
        [item.strip() for item in (value or "").split(";") if item.strip()],
        ensure_ascii=False,
    )


def _ensure_event_v3_columns(connection: sqlite3.Connection) -> None:
    """Mevcut event kayıtlarını silmeden V3 kolonlarını ileri yönlü ekler."""
    existing = {
        row["name"] for row in connection.execute("PRAGMA table_info(events)").fetchall()
    }
    for column, definition in EVENT_V3_COLUMNS.items():
        if column not in existing:
            connection.execute(f"ALTER TABLE events ADD COLUMN {column} {definition}")


def _migrate_interactions_v3(connection: sqlite3.Connection) -> None:
    """Interaction sözleşmesini veri kaybetmeden idempotency alanlarına taşır."""
    columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(interactions)").fetchall()
    }
    table_sql_row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='interactions'"
    ).fetchone()
    table_sql = (table_sql_row["sql"] if table_sql_row else "").lower()
    if {"interaction_key", "feed_token"} <= columns and "'apply'" in table_sql:
        return

    connection.execute("ALTER TABLE interactions RENAME TO interactions_legacy")
    connection.executescript(
        """
        CREATE TABLE interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id     TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
            event_id       TEXT NOT NULL REFERENCES events(event_id),
            action         TEXT NOT NULL CHECK (action IN ('like', 'skip', 'save', 'unsave', 'view_detail', 'apply')),
            dwell_ms       INTEGER,
            interaction_key TEXT,
            feed_token     TEXT,
            created_at     TEXT NOT NULL
        );
        """
    )
    legacy_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(interactions_legacy)").fetchall()
    }
    interaction_key = "interaction_key" if "interaction_key" in legacy_columns else "NULL"
    feed_token = "feed_token" if "feed_token" in legacy_columns else "NULL"
    connection.execute(
        f"""
        INSERT INTO interactions(
            interaction_id, profile_id, event_id, action, dwell_ms,
            interaction_key, feed_token, created_at
        )
        SELECT interaction_id, profile_id, event_id, action, dwell_ms,
               {interaction_key}, {feed_token}, created_at
        FROM interactions_legacy
        """
    )
    connection.execute("DROP TABLE interactions_legacy")
    connection.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_interactions_profile
            ON interactions(profile_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_interactions_event
            ON interactions(event_id, action);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_interactions_key
            ON interactions(interaction_key) WHERE interaction_key IS NOT NULL;
        """
    )


def migrate_schema(connection: sqlite3.Connection) -> None:
    """Faz 1 şemasını idempotent biçimde uygular ve eski kayıtları korur."""
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    connection.executescript(SCHEMA)
    _ensure_event_v3_columns(connection)
    _migrate_interactions_v3(connection)
    connection.executescript(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_interactions_key
            ON interactions(interaction_key) WHERE interaction_key IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_events_feed_v3
            ON events(status, starts_at, event_tier);
        CREATE INDEX IF NOT EXISTS idx_events_location_v3
            ON events(university_id, campus_id, city_id);
        """
    )
    connection.execute(
        "INSERT OR IGNORE INTO schema_migrations(version) VALUES ('phase-1-v3')"
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


def seed_v3_data(connection: sqlite3.Connection) -> dict[str, int]:
    """Üretilmiş V3 örneklerini bağımlılık sırasıyla idempotent olarak yükler."""
    organizer_rows = _read_csv_path(V3_SAMPLE_DATA_DIR / "organizers_v3.csv")
    event_rows = _read_csv_path(V3_SAMPLE_DATA_DIR / "events_v3.csv")
    profile_rows = _read_csv_path(SAMPLE_DATA_DIR / "v2" / "profiles_v2.csv")
    participation_rows = _read_csv_path(V3_SAMPLE_DATA_DIR / "participations_v3.csv")
    rating_rows = _read_csv_path(V3_SAMPLE_DATA_DIR / "ratings_v3.csv")
    interest_rows = _read_csv_path(V3_SAMPLE_DATA_DIR / "interest_weights_v3.csv")
    if not organizer_rows or not event_rows or not profile_rows:
        return {
            "organizers_v3": 0,
            "events_v3": 0,
            "profiles_v3": 0,
            "participations_v3": 0,
            "ratings_v3": 0,
            "interest_weights_v3": 0,
        }

    organizers = [
        {
            "organizer_id": row["organizer_id"],
            "schema_version": row["schema_version"],
            "user_id": row.get("user_id") or None,
            "organizer_type": row["organizer_type"],
            "display_name": row["display_name"],
            "university_id": row.get("university_id") or None,
            "verification_status": row["verification_status"],
            "trust_score": _to_float(row["trust_score"], 5.0),
            "rating_count": _to_int(row["rating_count"]),
            "is_blacklisted": _to_bool_int(row["is_blacklisted"]),
            "blacklist_reason": row.get("blacklist_reason") or None,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in organizer_rows
    ]

    events = []
    for index, row in enumerate(event_rows):
        starts_at = row["starts_at"]
        events.append(
            {
                "event_id": row["event_id"],
                "club_id": str(index % 4 + 1),
                "university_id": row.get("university_id", ""),
                "title": row["title"],
                "description": row["description"],
                "category": row["category_id"],
                "event_type": row["event_type"],
                "level": "all",
                "date": starts_at[:10],
                "location_type": row["participation_mode"],
                "quota": _to_int(row["quota"], 1),
                "target_interests": row["interest_ids"],
                "target_departments": row["target_program_ids"] or "all",
                "target_goals": row["target_goal_ids"],
                "fee_type": row["fee_type"],
                "language": row["language"],
                "schema_version": row["schema_version"],
                "organizer_id": row["organizer_id"],
                "event_tier": row["event_tier"],
                "campus_id": row.get("campus_id") or None,
                "city_id": row.get("city_id") or None,
                "category_id": row["category_id"],
                "interest_ids": _json_array(row["interest_ids"]),
                "target_program_ids": _json_array(row["target_program_ids"]),
                "target_class_years": _json_array(row["target_class_years"]),
                "target_goal_ids": _json_array(row["target_goal_ids"]),
                "starts_at": starts_at,
                "ends_at": row.get("ends_at") or None,
                "expires_at": row.get("expires_at") or None,
                "participation_mode": row["participation_mode"],
                "location_name": row.get("location_name") or None,
                "fee_amount": _to_float(row["fee_amount"]) if row.get("fee_amount") else None,
                "approval_status": row["approval_status"],
                "organizer_trust_score": _to_float(row["organizer_trust_score"], 5.0),
                "image_url": row.get("image_url") or None,
            }
        )

    duration_by_program = {
        "medicine": 6,
        "computer-engineering": 4,
        "industrial-engineering": 4,
        "business": 4,
        "psychology": 4,
        "graphic-design": 4,
    }
    profiles = []
    for row in profile_rows:
        profile_id = f"profile-v3-{int(row['profile_id']):04d}"
        timestamp = "2026-08-01T09:00:00+00:00"
        profiles.append(
            {
                "profile_id": profile_id,
                "schema_version": row["schema_version"],
                "education_reference_version": "synthetic-v3-2026-08",
                "display_name": f"Sentetik Öğrenci {int(row['profile_id']):04d}",
                "university_id": row["university_id"],
                "university_name": row["university_id"],
                "program_id": row["program_id"],
                "program_name": row["program_id"],
                "education_level": row["education_level"],
                "program_duration": duration_by_program.get(row["program_id"], 4),
                "class_year": row["class_year"],
                "interest_ids": json.dumps(row["interest_ids"].split(";"), ensure_ascii=False),
                "participation_goal_ids": json.dumps(row["participation_goal_ids"].split(";"), ensure_ascii=False),
                "participation_modes": json.dumps(row["participation_modes"].split(";"), ensure_ascii=False),
                "fee_preference": row["fee_preference"],
                "language_preference": row["language_preference"],
                "campus_id": None,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        )

    participations = [
        {
            "participation_id": row["participation_id"],
            "schema_version": row["schema_version"],
            "profile_id": row["profile_id"],
            "event_id": row["event_id"],
            "status": row["status"],
            "attendance_verified": _to_bool_int(row["attendance_verified"]),
            "requested_at": row["requested_at"],
            "verified_at": row.get("verified_at") or None,
        }
        for row in participation_rows
    ]
    ratings = [
        {
            "rating_id": row["rating_id"],
            "schema_version": row["schema_version"],
            "event_id": row["event_id"],
            "organizer_id": row["organizer_id"],
            "rater_profile_id": row["rater_profile_id"],
            "score": _to_int(row["score"]),
            "created_at": row["created_at"],
        }
        for row in rating_rows
    ]
    interest_weights = [
        {
            "profile_id": row["profile_id"],
            "interest_id": row["interest_id"],
            "schema_version": row["schema_version"],
            "weight": _to_float(row["weight"]),
            "explicit_weight": _to_float(row["explicit_weight"]),
            "behavior_weight": _to_float(row["behavior_weight"]),
            "updated_at": row["updated_at"],
        }
        for row in interest_rows
    ]

    with connection:
        counts = {
            "organizers_v3": _upsert(connection, "organizers", "organizer_id", organizers),
            "events_v3": _upsert(connection, "events", "event_id", events),
            "profiles_v3": _upsert(connection, "profiles", "profile_id", profiles),
            "participations_v3": _upsert(
                connection, "participations", "participation_id", participations
            ),
            "ratings_v3": _upsert(connection, "ratings", "rating_id", ratings),
        }
        if interest_weights:
            columns = list(interest_weights[0])
            placeholders = ", ".join("?" for _ in columns)
            updates = ", ".join(
                f"{column}=excluded.{column}"
                for column in columns
                if column not in {"profile_id", "interest_id"}
            )
            connection.executemany(
                f"INSERT INTO user_interest_weights ({', '.join(columns)}) "
                f"VALUES ({placeholders}) ON CONFLICT(profile_id, interest_id) "
                f"DO UPDATE SET {updates}",
                [tuple(row[column] for column in columns) for row in interest_weights],
            )
        counts["interest_weights_v3"] = len(interest_weights)
        return counts


def init_db(connection: sqlite3.Connection | None = None) -> dict[str, int]:
    """Şemayı kurar ve referans veriyi yükler. Uygulama açılışında çağrılır."""
    owned = connection is None
    connection = connection or connect()
    try:
        with connection:
            migrate_schema(connection)
        counts = seed_reference_data(connection)
        counts.update(seed_v3_data(connection))
        return counts
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
