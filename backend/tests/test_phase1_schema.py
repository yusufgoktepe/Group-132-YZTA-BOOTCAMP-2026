"""Faz 1 V3 şema, migration ve sentetik veri doğrulamaları."""

from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import jsonschema
import pytest

from backend.app.db import PROJECT_ROOT, init_db


SCHEMA_DIR = PROJECT_ROOT / "data" / "schemas"
V3_DIR = PROJECT_ROOT / "data" / "sample" / "v3"


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _rows(filename: str) -> list[dict[str, str]]:
    with (V3_DIR / filename).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _schema(filename: str) -> dict:
    return json.loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))


def _nullable(value: str):
    return value if value else None


def _list(value: str) -> list[str]:
    return [item for item in value.split(";") if item]


def _event_record(row: dict[str, str]) -> dict:
    return {
        **row,
        "university_id": _nullable(row["university_id"]),
        "campus_id": _nullable(row["campus_id"]),
        "city_id": _nullable(row["city_id"]),
        "interest_ids": _list(row["interest_ids"]),
        "target_program_ids": _list(row["target_program_ids"]),
        "target_class_years": _list(row["target_class_years"]),
        "target_goal_ids": _list(row["target_goal_ids"]),
        "ends_at": _nullable(row["ends_at"]),
        "expires_at": _nullable(row["expires_at"]),
        "location_name": _nullable(row["location_name"]),
        "fee_amount": float(row["fee_amount"]) if row["fee_amount"] else None,
        "quota": int(row["quota"]),
        "organizer_trust_score": float(row["organizer_trust_score"]),
        "image_url": _nullable(row["image_url"]),
    }


def _organizer_record(row: dict[str, str]) -> dict:
    return {
        **row,
        "user_id": _nullable(row["user_id"]),
        "university_id": _nullable(row["university_id"]),
        "trust_score": float(row["trust_score"]),
        "rating_count": int(row["rating_count"]),
        "is_blacklisted": row["is_blacklisted"] == "true",
        "blacklist_reason": _nullable(row["blacklist_reason"]),
    }


def _participation_record(row: dict[str, str]) -> dict:
    return {
        **row,
        "attendance_verified": row["attendance_verified"] == "true",
        "verified_at": _nullable(row["verified_at"]),
    }


def _rating_record(row: dict[str, str]) -> dict:
    return {**row, "score": int(row["score"])}


def _interest_record(row: dict[str, str]) -> dict:
    return {
        **row,
        "weight": float(row["weight"]),
        "explicit_weight": float(row["explicit_weight"]),
        "behavior_weight": float(row["behavior_weight"]),
    }


def test_every_v3_schema_is_a_valid_draft_2020_12_schema():
    for path in sorted(SCHEMA_DIR.glob("*_v3.schema.json")):
        jsonschema.Draft202012Validator.check_schema(_schema(path.name))


@pytest.mark.parametrize(
    ("csv_name", "schema_name", "adapter"),
    [
        ("organizers_v3.csv", "organizer_v3.schema.json", _organizer_record),
        ("events_v3.csv", "event_v3.schema.json", _event_record),
        ("participations_v3.csv", "participation_v3.schema.json", _participation_record),
        ("ratings_v3.csv", "rating_v3.schema.json", _rating_record),
        ("interest_weights_v3.csv", "interest_weight_v3.schema.json", _interest_record),
    ],
)
def test_every_v3_sample_row_matches_its_schema(csv_name, schema_name, adapter):
    validator = jsonschema.Draft202012Validator(
        _schema(schema_name), format_checker=jsonschema.FormatChecker()
    )
    for row_number, row in enumerate(_rows(csv_name), start=2):
        errors = sorted(validator.iter_errors(adapter(row)), key=lambda error: list(error.path))
        assert not errors, f"{csv_name}:{row_number}: {errors[0].message if errors else ''}"


def test_v3_dataset_matches_phase_one_size_and_trust_decisions():
    events = _rows("events_v3.csv")
    organizers = _rows("organizers_v3.csv")

    assert Counter(row["event_tier"] for row in events) == {"official": 80, "micro": 170}
    assert len(organizers) == 80
    assert sum(row["is_blacklisted"] == "true" for row in organizers) == 5
    assert all(row["expires_at"] for row in events if row["event_tier"] == "micro")
    assert all(row["approval_status"] == "approved" for row in events if row["event_tier"] == "official")
    assert all(row["approval_status"] == "not_required" for row in events if row["event_tier"] == "micro")

    organizer_map = {row["organizer_id"]: row for row in organizers}
    assert all(row["organizer_id"] in organizer_map for row in events)
    assert all(
        float(row["organizer_trust_score"])
        == float(organizer_map[row["organizer_id"]]["trust_score"])
        for row in events
    )


def test_initial_interest_weights_are_normalized_per_profile():
    totals: dict[str, float] = defaultdict(float)
    for row in _rows("interest_weights_v3.csv"):
        totals[row["profile_id"]] += float(row["weight"])

    assert len(totals) == 1000
    assert all(abs(total - 1.0) < 0.00001 for total in totals.values())


def test_fresh_database_contains_v3_tables_and_seed_is_idempotent():
    connection = _connection()
    try:
        first = init_db(connection)
        first_event_count = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        second = init_db(connection)
        second_event_count = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        tiers = dict(connection.execute("SELECT event_tier, COUNT(*) FROM events GROUP BY event_tier"))

        assert {"organizers", "participations", "ratings", "user_interest_weights", "moderation_actions", "schema_migrations"} <= tables
        assert first["events_v3"] == second["events_v3"] == 250
        assert first["profiles_v3"] == second["profiles_v3"] == 1000
        assert first_event_count == second_event_count == 254
        assert tiers == {"micro": 170, "official": 84}
        assert connection.execute("SELECT COUNT(*) FROM organizers").fetchone()[0] == 80
        assert connection.execute("SELECT COUNT(*) FROM profiles").fetchone()[0] == 1000
        assert connection.execute("SELECT COUNT(*) FROM participations").fetchone()[0] == 1200
        assert connection.execute("SELECT COUNT(*) FROM ratings").fetchone()[0] == 800
        assert connection.execute("SELECT COUNT(*) FROM user_interest_weights").fetchone()[0] == 5393
        assert connection.execute("SELECT COUNT(*) FROM schema_migrations WHERE version='phase-1-v3'").fetchone()[0] == 1
    finally:
        connection.close()


def test_migration_preserves_an_existing_legacy_event():
    connection = _connection()
    try:
        connection.executescript(
            """
            CREATE TABLE clubs (
                club_id TEXT PRIMARY KEY, club_name TEXT NOT NULL, category TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '', target_departments TEXT NOT NULL DEFAULT '',
                target_interests TEXT NOT NULL DEFAULT '', activity_level TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE events (
                event_id TEXT PRIMARY KEY, club_id TEXT NOT NULL REFERENCES clubs(club_id),
                university_id TEXT NOT NULL DEFAULT '', title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '', category TEXT NOT NULL DEFAULT '',
                event_type TEXT NOT NULL DEFAULT '', level TEXT NOT NULL DEFAULT '', date TEXT NOT NULL DEFAULT '',
                location_type TEXT NOT NULL DEFAULT '', quota INTEGER NOT NULL DEFAULT 0,
                target_interests TEXT NOT NULL DEFAULT '', target_departments TEXT NOT NULL DEFAULT '',
                target_goals TEXT NOT NULL DEFAULT '', fee_type TEXT NOT NULL DEFAULT '', language TEXT NOT NULL DEFAULT ''
            );
            INSERT INTO clubs(club_id, club_name) VALUES ('legacy-club', 'Korunan Kulüp');
            INSERT INTO events(event_id, club_id, title) VALUES ('legacy-event', 'legacy-club', 'Korunan Etkinlik');
            """
        )

        init_db(connection)
        legacy = connection.execute(
            "SELECT title, schema_version, event_tier, status FROM events WHERE event_id='legacy-event'"
        ).fetchone()
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(events)")}

        assert tuple(legacy) == ("Korunan Etkinlik", "2.0", "official", "published")
        assert {"organizer_id", "event_tier", "expires_at", "approval_status", "organizer_trust_score"} <= columns
    finally:
        connection.close()


def test_phase_two_migration_preserves_legacy_interactions():
    connection = _connection()
    try:
        init_db(connection)
        profile_id = connection.execute("SELECT profile_id FROM profiles LIMIT 1").fetchone()[0]
        event_id = connection.execute("SELECT event_id FROM events LIMIT 1").fetchone()[0]
        connection.execute(
            "INSERT INTO interactions(profile_id, event_id, action, dwell_ms, created_at) "
            "VALUES (?, ?, 'like', 1200, '2026-08-01T09:00:00+00:00')",
            (profile_id, event_id),
        )
        connection.commit()

        # Eski sözleşmeyi taklit etmek için yeni kolonlu tabloyu veri kaybetmeden yeniden kurar.
        connection.execute("DROP INDEX IF EXISTS idx_interactions_key")
        connection.execute("ALTER TABLE interactions RENAME TO interactions_current")
        connection.executescript(
            """
            CREATE TABLE interactions (
                interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
                event_id TEXT NOT NULL REFERENCES events(event_id),
                action TEXT NOT NULL CHECK (action IN ('like', 'skip', 'save', 'unsave', 'view_detail')),
                dwell_ms INTEGER,
                created_at TEXT NOT NULL
            );
            INSERT INTO interactions(interaction_id, profile_id, event_id, action, dwell_ms, created_at)
            SELECT interaction_id, profile_id, event_id, action, dwell_ms, created_at
            FROM interactions_current;
            DROP TABLE interactions_current;
            """
        )

        init_db(connection)
        row = connection.execute("SELECT * FROM interactions LIMIT 1").fetchone()
        columns = {item["name"] for item in connection.execute("PRAGMA table_info(interactions)")}

        assert row["profile_id"] == profile_id
        assert {"interaction_key", "feed_token"} <= columns
        connection.execute(
            "INSERT INTO interactions(profile_id, event_id, action, interaction_key, created_at) "
            "VALUES (?, ?, 'apply', 'migration-apply-key', '2026-08-01T10:00:00+00:00')",
            (profile_id, event_id),
        )
    finally:
        connection.close()
