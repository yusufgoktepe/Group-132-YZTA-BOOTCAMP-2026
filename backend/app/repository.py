"""Veritabanı okuma/yazma işlemleri.

Endpoint'ler doğrudan SQL yazmaz; tüm sorgular bu katmandan geçer.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from .db import JSON_PROFILE_FIELDS, profile_row_to_dict

SAVE_ACTIONS = ("save", "unsave")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- Referans veri --------------------------------------------------------


def list_students(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute("SELECT * FROM students ORDER BY student_id").fetchall()
    return [dict(row) for row in rows]


def get_student(connection: sqlite3.Connection, student_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM students WHERE student_id = ?", (student_id,)
    ).fetchone()
    return dict(row) if row else None


def list_clubs(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute("SELECT * FROM clubs ORDER BY club_id").fetchall()
    return [dict(row) for row in rows]


def list_events(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT events.*, COALESCE(clubs.club_name, '') AS club_name
        FROM events
        LEFT JOIN clubs ON clubs.club_id = events.club_id
        ORDER BY CAST(events.event_id AS INTEGER), events.event_id
        """
    ).fetchall()
    return [dict(row) for row in rows]


def get_event(connection: sqlite3.Connection, event_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        """
        SELECT events.*, COALESCE(clubs.club_name, '') AS club_name
        FROM events
        LEFT JOIN clubs ON clubs.club_id = events.club_id
        WHERE events.event_id = ?
        """,
        (event_id,),
    ).fetchone()
    return dict(row) if row else None


def event_exists(connection: sqlite3.Connection, event_id: str) -> bool:
    return (
        connection.execute(
            "SELECT 1 FROM events WHERE event_id = ?", (event_id,)
        ).fetchone()
        is not None
    )


# --- Profiller ------------------------------------------------------------


def _profile_columns(profile: dict[str, Any]) -> dict[str, Any]:
    stored = dict(profile)
    for field in JSON_PROFILE_FIELDS:
        stored[field] = json.dumps(stored[field], ensure_ascii=False)
    return stored


def create_profile(connection: sqlite3.Connection, profile: dict[str, Any]) -> dict[str, Any]:
    profile_id = profile.get("profile_id") or f"profile-{uuid.uuid4().hex[:12]}"
    timestamp = _now()
    stored = _profile_columns(profile)
    stored.update(profile_id=profile_id, created_at=timestamp, updated_at=timestamp)

    columns = [
        "profile_id",
        "schema_version",
        "education_reference_version",
        "display_name",
        "university_id",
        "university_name",
        "program_id",
        "program_name",
        "education_level",
        "program_duration",
        "class_year",
        "interest_ids",
        "participation_goal_ids",
        "participation_modes",
        "fee_preference",
        "language_preference",
        "campus_id",
        "created_at",
        "updated_at",
    ]
    with connection:
        connection.execute(
            f"INSERT INTO profiles ({', '.join(columns)}) "
            f"VALUES ({', '.join('?' for _ in columns)})",
            tuple(stored.get(column) for column in columns),
        )
    return get_profile(connection, profile_id)  # type: ignore[return-value]


def get_profile(connection: sqlite3.Connection, profile_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM profiles WHERE profile_id = ?", (profile_id,)
    ).fetchone()
    return profile_row_to_dict(row) if row else None


def update_profile(
    connection: sqlite3.Connection, profile_id: str, profile: dict[str, Any]
) -> dict[str, Any] | None:
    if get_profile(connection, profile_id) is None:
        return None

    stored = _profile_columns(profile)
    stored["updated_at"] = _now()
    columns = [column for column in stored if column != "profile_id"]

    with connection:
        connection.execute(
            f"UPDATE profiles SET {', '.join(f'{column} = ?' for column in columns)} "
            f"WHERE profile_id = ?",
            (*(stored[column] for column in columns), profile_id),
        )
    return get_profile(connection, profile_id)


# --- Etkileşimler ---------------------------------------------------------


def record_interaction(
    connection: sqlite3.Connection,
    profile_id: str,
    event_id: str,
    action: str,
    dwell_ms: int | None = None,
) -> dict[str, Any]:
    timestamp = _now()
    with connection:
        cursor = connection.execute(
            "INSERT INTO interactions (profile_id, event_id, action, dwell_ms, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (profile_id, event_id, action, dwell_ms, timestamp),
        )
    return {
        "interaction_id": cursor.lastrowid,
        "profile_id": profile_id,
        "event_id": event_id,
        "action": action,
        "dwell_ms": dwell_ms,
        "created_at": timestamp,
    }


def list_interactions(
    connection: sqlite3.Connection, profile_id: str, action: str | None = None
) -> list[dict[str, Any]]:
    query = "SELECT * FROM interactions WHERE profile_id = ?"
    params: list[Any] = [profile_id]
    if action:
        query += " AND action = ?"
        params.append(action)
    query += " ORDER BY interaction_id DESC"
    return [dict(row) for row in connection.execute(query, params).fetchall()]


def saved_event_ids(connection: sqlite3.Connection, profile_id: str) -> list[str]:
    """Her etkinlik için en son `save`/`unsave` hareketini dikkate alır."""
    rows = connection.execute(
        """
        SELECT event_id, action
        FROM interactions
        WHERE profile_id = ?
          AND action IN ('save', 'unsave')
          AND interaction_id IN (
              SELECT MAX(interaction_id) FROM interactions
              WHERE profile_id = ? AND action IN ('save', 'unsave')
              GROUP BY event_id
          )
        ORDER BY interaction_id DESC
        """,
        (profile_id, profile_id),
    ).fetchall()
    return [row["event_id"] for row in rows if row["action"] == "save"]


def saved_events(connection: sqlite3.Connection, profile_id: str) -> list[dict[str, Any]]:
    event_ids = saved_event_ids(connection, profile_id)
    if not event_ids:
        return []
    events = {event["event_id"]: event for event in list_events(connection)}
    return [events[event_id] for event_id in event_ids if event_id in events]


def profile_action_map(connection: sqlite3.Connection, profile_id: str) -> dict[str, set[str]]:
    """Etkinlik kimliğinden profil için geçerli hareket durumuna eşleme.

    Save/unsave ve like/skip çiftlerinde yalnızca son durum öneri skoruna katılır.
    """
    rows = connection.execute(
        "SELECT event_id, action FROM interactions WHERE profile_id = ? "
        "ORDER BY interaction_id",
        (profile_id,),
    ).fetchall()
    actions: dict[str, set[str]] = {}
    for row in rows:
        event_actions = actions.setdefault(row["event_id"], set())
        action = row["action"]
        if action == "save":
            event_actions.add("save")
        elif action == "unsave":
            event_actions.discard("save")
        elif action in {"like", "skip"}:
            event_actions.difference_update({"like", "skip"})
            event_actions.add(action)
        else:
            event_actions.add(action)
    return actions


def interaction_counts(connection: sqlite3.Connection) -> dict[str, int]:
    row = connection.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM clubs)        AS clubs,
            (SELECT COUNT(*) FROM events)       AS events,
            (SELECT COUNT(*) FROM students)     AS students,
            (SELECT COUNT(*) FROM profiles)     AS profiles,
            (SELECT COUNT(*) FROM interactions) AS interactions
        """
    ).fetchone()
    return dict(row)
