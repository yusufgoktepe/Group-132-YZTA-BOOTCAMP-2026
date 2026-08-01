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

# Faz 4: açık davranış sinyalleri küçük ve sınırlandırılmış adımlarla öğrenilir.
ACTION_INTEREST_DELTAS = {
    "like": 0.12,
    "skip": -0.10,
    "save": 0.16,
    "unsave": -0.08,
    "view_detail": 0.03,
    "apply": 0.22,
}
DWELL_SHORT_MS = 2_000
DWELL_LONG_MS = 8_000
DWELL_SHORT_DELTA = -0.02
DWELL_LONG_DELTA = 0.05


class InteractionKeyConflictError(ValueError):
    """Aynı idempotency anahtarı farklı bir interaction için kullanıldığında oluşur."""


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


def _ensure_student_organizer(
    connection: sqlite3.Connection, profile: dict[str, Any]
) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM organizers WHERE user_id = ? AND organizer_type = 'student'",
        (profile["profile_id"],),
    ).fetchone()
    if row:
        return dict(row)
    timestamp = _now()
    organizer_id = f"organizer-{profile['profile_id']}"
    connection.execute(
        """
        INSERT INTO organizers(
            organizer_id, schema_version, user_id, organizer_type, display_name,
            university_id, verification_status, trust_score, rating_count,
            is_blacklisted, created_at, updated_at
        ) VALUES (?, '3.0', ?, 'student', ?, ?, 'verified', 5.0, 0, 0, ?, ?)
        """,
        (
            organizer_id,
            profile["profile_id"],
            profile["display_name"] or "Öğrenci Organizatör",
            profile["university_id"],
            timestamp,
            timestamp,
        ),
    )
    return dict(connection.execute("SELECT * FROM organizers WHERE organizer_id = ?", (organizer_id,)).fetchone())


def create_micro_event(
    connection: sqlite3.Connection, profile: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    event_id = f"event-micro-{uuid.uuid4().hex[:12]}"
    with connection:
        organizer = _ensure_student_organizer(connection, profile)
        if organizer["is_blacklisted"] or organizer["verification_status"] != "verified":
            raise PermissionError("Organizatörün mikro etkinlik yayımlama yetkisi yok.")
        connection.execute(
            "INSERT OR IGNORE INTO clubs(club_id, club_name, category) VALUES ('micro-community', 'Öğrenci Buluşmaları', 'community')"
        )
        connection.execute(
            """
            INSERT INTO events(
                event_id, club_id, university_id, title, description, category,
                event_type, date, location_type, quota, target_interests,
                target_goals, fee_type, language, schema_version, organizer_id,
                event_tier, campus_id, category_id, interest_ids,
                target_program_ids, target_class_years, target_goal_ids,
                starts_at, ends_at, expires_at, participation_mode,
                location_name, fee_amount, status, approval_status,
                organizer_trust_score
            ) VALUES (
                ?, 'micro-community', ?, ?, ?, ?, 'micro_activity', ?, ?, ?, ?,
                ?, 'free', ?, '3.0', ?, 'micro', ?, ?, ?, '[]', '[]', ?,
                ?, ?, ?, ?, ?, 0, 'published', 'not_required', ?
            )
            """,
            (
                event_id, profile["university_id"], payload["title"], payload["description"],
                payload["category_id"], payload["starts_at"][:10], payload["participation_mode"],
                payload["quota"], ";".join(payload["interest_ids"]),
                ";".join(payload.get("target_goal_ids", [])), payload["language"],
                organizer["organizer_id"], profile.get("campus_id"), payload["category_id"],
                json.dumps(payload["interest_ids"], ensure_ascii=False),
                json.dumps(payload.get("target_goal_ids", []), ensure_ascii=False),
                payload["starts_at"], payload["ends_at"], payload["expires_at"],
                payload["participation_mode"], payload["location_name"], organizer["trust_score"],
            ),
        )
    return get_event(connection, event_id)  # type: ignore[return-value]


def _assert_event_owner(connection: sqlite3.Connection, event_id: str, profile_id: str) -> dict[str, Any]:
    event = get_event(connection, event_id)
    if not event:
        raise LookupError("event_not_found")
    owner = connection.execute(
        "SELECT user_id FROM organizers WHERE organizer_id = ?", (event["organizer_id"],)
    ).fetchone()
    if event["event_tier"] != "micro" or not owner or owner["user_id"] != profile_id:
        raise PermissionError("Bu etkinliği yalnızca oluşturan öğrenci değiştirebilir.")
    return event


def update_micro_event(
    connection: sqlite3.Connection, event_id: str, profile_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    current = _assert_event_owner(connection, event_id, profile_id)
    if current["status"] in {"cancelled", "completed", "expired"}:
        raise ValueError("Sona ermiş veya iptal edilmiş etkinlik güncellenemez.")
    occupied = connection.execute(
        "SELECT COUNT(*) FROM participations WHERE event_id=? AND status IN ('requested','approved','attended')",
        (event_id,),
    ).fetchone()[0]
    if payload["quota"] < occupied:
        raise ValueError("Kota mevcut aktif katılımcı sayısının altına indirilemez.")
    with connection:
        connection.execute(
            """
            UPDATE events SET title=?, description=?, category=?, category_id=?,
                date=?, location_type=?, participation_mode=?, location_name=?, quota=?,
                target_interests=?, interest_ids=?, target_goals=?, target_goal_ids=?,
                starts_at=?, ends_at=?, expires_at=?, language=?
            WHERE event_id=?
            """,
            (
                payload["title"], payload["description"], payload["category_id"], payload["category_id"],
                payload["starts_at"][:10], payload["participation_mode"], payload["participation_mode"],
                payload["location_name"], payload["quota"], ";".join(payload["interest_ids"]),
                json.dumps(payload["interest_ids"], ensure_ascii=False),
                ";".join(payload.get("target_goal_ids", [])),
                json.dumps(payload.get("target_goal_ids", []), ensure_ascii=False),
                payload["starts_at"], payload["ends_at"], payload["expires_at"], payload["language"],
                event_id,
            ),
        )
    return get_event(connection, event_id)  # type: ignore[return-value]


def cancel_micro_event(connection: sqlite3.Connection, event_id: str, profile_id: str) -> dict[str, Any]:
    _assert_event_owner(connection, event_id, profile_id)
    with connection:
        connection.execute("UPDATE events SET status='cancelled' WHERE event_id=?", (event_id,))
    return get_event(connection, event_id)  # type: ignore[return-value]


def request_participation(
    connection: sqlite3.Connection, profile_id: str, event_id: str
) -> tuple[dict[str, Any], bool]:
    event = get_event(connection, event_id)
    if not event:
        raise LookupError("event_not_found")
    if event["status"] != "published":
        raise ValueError("Etkinlik katılım isteğine açık değil.")
    now = datetime.now(timezone.utc)
    if event["expires_at"] and datetime.fromisoformat(event["expires_at"]) <= now:
        raise ValueError("Etkinliğin süresi dolmuş.")
    existing = connection.execute(
        "SELECT * FROM participations WHERE profile_id=? AND event_id=?", (profile_id, event_id)
    ).fetchone()
    if existing:
        return dict(existing), True
    occupied = connection.execute(
        "SELECT COUNT(*) FROM participations WHERE event_id=? AND status IN ('requested','approved','attended')",
        (event_id,),
    ).fetchone()[0]
    if event["quota"] > 0 and occupied >= event["quota"]:
        raise OverflowError("Etkinlik kotası dolu.")
    participation_id = f"participation-{uuid.uuid4().hex[:12]}"
    timestamp = _now()
    with connection:
        connection.execute(
            """INSERT INTO participations(
                participation_id, schema_version, profile_id, event_id, status,
                attendance_verified, requested_at
            ) VALUES (?, '3.0', ?, ?, 'requested', 0, ?)""",
            (participation_id, profile_id, event_id, timestamp),
        )
    return dict(connection.execute(
        "SELECT * FROM participations WHERE participation_id=?", (participation_id,)
    ).fetchone()), False


def list_participations(connection: sqlite3.Connection, profile_id: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        """SELECT participations.*, events.title, events.starts_at, events.location_name,
        EXISTS(SELECT 1 FROM ratings WHERE ratings.event_id=participations.event_id
            AND ratings.rater_profile_id=participations.profile_id) AS has_rated
        FROM participations JOIN events ON events.event_id=participations.event_id
        WHERE participations.profile_id=? ORDER BY participations.requested_at DESC""",
        (profile_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def update_participation_status(
    connection: sqlite3.Connection,
    participation_id: str,
    actor_profile_id: str,
    status: str,
) -> dict[str, Any]:
    row = connection.execute(
        """SELECT participations.*, organizers.user_id AS owner_profile_id
        FROM participations
        JOIN events ON events.event_id=participations.event_id
        LEFT JOIN organizers ON organizers.organizer_id=events.organizer_id
        WHERE participation_id=?""",
        (participation_id,),
    ).fetchone()
    if not row:
        raise LookupError("participation_not_found")
    is_participant = row["profile_id"] == actor_profile_id
    is_owner = row["owner_profile_id"] == actor_profile_id
    if status == "cancelled":
        if not (is_participant or is_owner):
            raise PermissionError("Bu katılım isteğini iptal etme yetkin yok.")
    elif not is_owner:
        raise PermissionError("Katılım durumunu yalnızca etkinlik sahibi değiştirebilir.")

    allowed = {
        "requested": {"approved", "rejected", "cancelled"},
        "approved": {"cancelled", "attended", "no_show"},
    }
    if status not in allowed.get(row["status"], set()):
        raise ValueError(f"'{row['status']}' durumundan '{status}' durumuna geçilemez.")
    verified_at = _now() if status in {"attended", "no_show"} else None
    with connection:
        connection.execute(
            """UPDATE participations SET status=?, attendance_verified=?, verified_at=?
            WHERE participation_id=?""",
            (status, int(status == "attended"), verified_at, participation_id),
        )
    return dict(connection.execute(
        "SELECT * FROM participations WHERE participation_id=?", (participation_id,)
    ).fetchone())


def create_rating(
    connection: sqlite3.Connection, event_id: str, profile_id: str, score: int
) -> dict[str, Any]:
    participation = connection.execute(
        """SELECT * FROM participations
        WHERE event_id=? AND profile_id=? AND status='attended' AND attendance_verified=1""",
        (event_id, profile_id),
    ).fetchone()
    if not participation:
        raise PermissionError("Yalnızca katılımı doğrulanmış öğrenci puan verebilir.")
    event = get_event(connection, event_id)
    if not event or not event["organizer_id"]:
        raise LookupError("event_not_found")
    existing = connection.execute(
        "SELECT 1 FROM ratings WHERE event_id=? AND rater_profile_id=?",
        (event_id, profile_id),
    ).fetchone()
    if existing:
        raise ValueError("Bu etkinlik için daha önce puan verdin.")

    rating_id = f"rating-{uuid.uuid4().hex[:12]}"
    timestamp = _now()
    with connection:
        connection.execute(
            """INSERT INTO ratings(
                rating_id, schema_version, event_id, organizer_id,
                rater_profile_id, score, created_at
            ) VALUES (?, '3.0', ?, ?, ?, ?, ?)""",
            (rating_id, event_id, event["organizer_id"], profile_id, score, timestamp),
        )
        aggregate = connection.execute(
            "SELECT COUNT(*) AS count, AVG(score) AS average FROM ratings WHERE organizer_id=?",
            (event["organizer_id"],),
        ).fetchone()
        rating_count = int(aggregate["count"])
        trust_score = round(float(aggregate["average"]), 2)
        should_block = rating_count >= 3 and trust_score < 2.0
        current_organizer = connection.execute(
            "SELECT is_blacklisted, blacklist_reason FROM organizers WHERE organizer_id=?",
            (event["organizer_id"],),
        ).fetchone()
        remains_blocked = bool(current_organizer["is_blacklisted"]) or should_block
        reason = (
            f"{rating_count} doğrulanmış puan sonrası güven ortalaması {trust_score:.2f}."
            if should_block else None
        )
        connection.execute(
            """UPDATE organizers SET trust_score=?, rating_count=?, is_blacklisted=?,
                blacklist_reason=?, updated_at=? WHERE organizer_id=?""",
            (
                trust_score,
                rating_count,
                int(remains_blocked),
                reason or current_organizer["blacklist_reason"],
                timestamp,
                event["organizer_id"],
            ),
        )
        connection.execute(
            "UPDATE events SET organizer_trust_score=? WHERE organizer_id=?",
            (trust_score, event["organizer_id"]),
        )
        if should_block and not connection.execute(
            """SELECT 1 FROM moderation_actions WHERE organizer_id=?
            AND action_type='publish_block' AND status='open'""",
            (event["organizer_id"],),
        ).fetchone():
            connection.execute(
                """INSERT INTO moderation_actions(
                    moderation_action_id, schema_version, organizer_id, event_id,
                    action_type, reason, status, created_at
                ) VALUES (?, '3.0', ?, NULL, 'publish_block', ?, 'open', ?)""",
                (f"moderation-{uuid.uuid4().hex[:12]}", event["organizer_id"], reason, timestamp),
            )
    # rater_profile_id özellikle genel cevaba dahil edilmez.
    return {
        "rating_id": rating_id,
        "schema_version": "3.0",
        "event_id": event_id,
        "organizer_id": event["organizer_id"],
        "score": score,
        "created_at": timestamp,
        "is_anonymous": True,
    }


def organizer_trust_summary(
    connection: sqlite3.Connection, organizer_id: str
) -> dict[str, Any] | None:
    organizer = connection.execute(
        "SELECT * FROM organizers WHERE organizer_id=?", (organizer_id,)
    ).fetchone()
    if not organizer:
        return None
    open_actions = connection.execute(
        "SELECT COUNT(*) FROM moderation_actions WHERE organizer_id=? AND status='open'",
        (organizer_id,),
    ).fetchone()[0]
    return {
        "schema_version": "3.0",
        "organizer_id": organizer_id,
        "display_name": organizer["display_name"],
        "verification_status": organizer["verification_status"],
        "trust_score": float(organizer["trust_score"]),
        "rating_count": int(organizer["rating_count"]),
        "minimum_rating_threshold_met": int(organizer["rating_count"]) >= 3,
        "publishing_blocked": bool(organizer["is_blacklisted"]),
        "open_moderation_action_count": int(open_actions),
    }


def set_organizer_verification(
    connection: sqlite3.Connection, organizer_id: str, status: str, reason: str
) -> dict[str, Any]:
    organizer = connection.execute(
        "SELECT * FROM organizers WHERE organizer_id=?", (organizer_id,)
    ).fetchone()
    if not organizer:
        raise LookupError("organizer_not_found")
    timestamp = _now()
    with connection:
        connection.execute(
            "UPDATE organizers SET verification_status=?, updated_at=? WHERE organizer_id=?",
            (status, timestamp, organizer_id),
        )
        if status == "rejected":
            connection.execute(
                """INSERT INTO moderation_actions(
                    moderation_action_id, schema_version, organizer_id, action_type,
                    reason, status, created_at
                ) VALUES (?, '3.0', ?, 'publish_block', ?, 'open', ?)""",
                (f"moderation-{uuid.uuid4().hex[:12]}", organizer_id, reason, timestamp),
            )
        elif status == "verified":
            connection.execute(
                """UPDATE moderation_actions SET status='resolved', resolved_at=?
                WHERE organizer_id=? AND action_type='publish_block' AND status='open'""",
                (timestamp, organizer_id),
            )
    return dict(connection.execute("SELECT * FROM organizers WHERE organizer_id=?", (organizer_id,)).fetchone())


def set_official_event_approval(
    connection: sqlite3.Connection, event_id: str, status: str, reason: str
) -> dict[str, Any]:
    event = get_event(connection, event_id)
    if not event:
        raise LookupError("event_not_found")
    if event["event_tier"] != "official":
        raise ValueError("Yayın onayı yalnızca resmî etkinlikler için kullanılabilir.")
    with connection:
        connection.execute(
            "UPDATE events SET approval_status=? WHERE event_id=?", (status, event_id)
        )
        if status == "rejected":
            connection.execute(
                """INSERT INTO moderation_actions(
                    moderation_action_id, schema_version, organizer_id, event_id,
                    action_type, reason, status, created_at
                ) VALUES (?, '3.0', ?, ?, 'feed_removal', ?, 'open', ?)""",
                (f"moderation-{uuid.uuid4().hex[:12]}", event["organizer_id"], event_id, reason, _now()),
            )
    return get_event(connection, event_id)  # type: ignore[return-value]


def list_moderation_actions(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """SELECT moderation_action_id, schema_version, organizer_id, event_id,
        action_type, reason, status, created_at, resolved_at
        FROM moderation_actions ORDER BY created_at DESC"""
    ).fetchall()
    return [dict(row) for row in rows]


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
    interaction_key: str | None = None,
    feed_token: str | None = None,
) -> dict[str, Any]:
    if interaction_key:
        existing = connection.execute(
            "SELECT * FROM interactions WHERE interaction_key = ?", (interaction_key,)
        ).fetchone()
        if existing:
            if (
                existing["profile_id"] != profile_id
                or existing["event_id"] != event_id
                or existing["action"] != action
            ):
                raise InteractionKeyConflictError(
                    "interaction_key daha önce farklı bir hareket için kullanılmış."
                )
            return {**dict(existing), "is_duplicate": True}

    timestamp = _now()
    with connection:
        cursor = connection.execute(
            "INSERT INTO interactions "
            "(profile_id, event_id, action, dwell_ms, interaction_key, feed_token, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (profile_id, event_id, action, dwell_ms, interaction_key, feed_token, timestamp),
        )
        update_interest_weights_for_interaction(
            connection, profile_id, event_id, action, dwell_ms, timestamp
        )
    return {
        "interaction_id": cursor.lastrowid,
        "profile_id": profile_id,
        "event_id": event_id,
        "action": action,
        "dwell_ms": dwell_ms,
        "interaction_key": interaction_key,
        "feed_token": feed_token,
        "created_at": timestamp,
        "is_duplicate": False,
    }


def _event_interest_ids(connection: sqlite3.Connection, event_id: str) -> list[str]:
    row = connection.execute(
        "SELECT interest_ids, target_interests FROM events WHERE event_id = ?", (event_id,)
    ).fetchone()
    if not row:
        return []
    raw = row["interest_ids"] or row["target_interests"] or ""
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return list(dict.fromkeys(str(item).strip().lower() for item in parsed if str(item).strip()))
    except json.JSONDecodeError:
        pass
    return list(dict.fromkeys(item.strip().lower() for item in raw.split(";") if item.strip()))


def update_interest_weights_for_interaction(
    connection: sqlite3.Connection,
    profile_id: str,
    event_id: str,
    action: str,
    dwell_ms: int | None,
    timestamp: str | None = None,
) -> None:
    """Etkileşimden kalıcı, normalize edilmiş ilgi vektörü üretir.

    Dwell tek başına 2 saniyenin altında zayıf negatif, 8 saniye ve üzerinde
    pozitif sinyaldir. Aradaki süre nötr kabul edilir. Davranış bileşeni [-1, 1]
    aralığında, nihai ağırlıklar ise profil başına toplam 1 olacak şekilde tutulur.
    """
    interest_ids = _event_interest_ids(connection, event_id)
    if not interest_ids:
        return

    rows = connection.execute(
        "SELECT * FROM user_interest_weights WHERE profile_id = ?", (profile_id,)
    ).fetchall()
    weights = {row["interest_id"]: dict(row) for row in rows}
    if not weights:
        profile = get_profile(connection, profile_id)
        explicit_ids = list(dict.fromkeys(profile["interest_ids"] if profile else []))
        base = 1.0 / len(explicit_ids) if explicit_ids else 0.0
        for interest_id in explicit_ids:
            weights[interest_id] = {
                "interest_id": interest_id,
                "explicit_weight": base,
                "behavior_weight": 0.0,
            }

    delta = ACTION_INTEREST_DELTAS.get(action, 0.0)
    if dwell_ms is not None:
        if dwell_ms < DWELL_SHORT_MS:
            delta += DWELL_SHORT_DELTA
        elif dwell_ms >= DWELL_LONG_MS:
            delta += DWELL_LONG_DELTA

    for interest_id in interest_ids:
        weights.setdefault(
            interest_id,
            {"interest_id": interest_id, "explicit_weight": 0.0, "behavior_weight": 0.0},
        )
        weights[interest_id]["behavior_weight"] = max(
            -1.0, min(1.0, float(weights[interest_id]["behavior_weight"]) + delta)
        )

    raw_weights = {
        key: max(0.0, float(value["explicit_weight"]) + float(value["behavior_weight"]))
        for key, value in weights.items()
    }
    total = sum(raw_weights.values())
    if total <= 0:
        raw_weights = {key: float(value["explicit_weight"]) for key, value in weights.items()}
        total = sum(raw_weights.values()) or 1.0

    timestamp = timestamp or _now()
    for interest_id, value in weights.items():
        connection.execute(
            """
            INSERT INTO user_interest_weights(
                profile_id, interest_id, schema_version, weight,
                explicit_weight, behavior_weight, updated_at
            ) VALUES (?, ?, '3.0', ?, ?, ?, ?)
            ON CONFLICT(profile_id, interest_id) DO UPDATE SET
                weight=excluded.weight,
                explicit_weight=excluded.explicit_weight,
                behavior_weight=excluded.behavior_weight,
                updated_at=excluded.updated_at
            """,
            (
                profile_id,
                interest_id,
                raw_weights[interest_id] / total,
                float(value["explicit_weight"]),
                float(value["behavior_weight"]),
                timestamp,
            ),
        )


def interest_weight_map(connection: sqlite3.Connection, profile_id: str) -> dict[str, float]:
    rows = connection.execute(
        "SELECT interest_id, weight FROM user_interest_weights WHERE profile_id = ?",
        (profile_id,),
    ).fetchall()
    return {row["interest_id"]: float(row["weight"]) for row in rows}


def list_interest_weights(connection: sqlite3.Connection, profile_id: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT interest_id, weight, explicit_weight, behavior_weight, updated_at
        FROM user_interest_weights
        WHERE profile_id = ?
        ORDER BY weight DESC, interest_id ASC
        """,
        (profile_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def list_feed_candidates(
    connection: sqlite3.Connection,
    profile: dict[str, Any],
    now_iso: str,
    limit: int = 30,
) -> list[dict[str, Any]]:
    """Feed ranking öncesi güvenli ve uygun aday havuzunu SQL ile üretir."""
    program_id = profile["program_id"]
    class_year = profile["class_year"]
    rows = connection.execute(
        """
        SELECT events.*, COALESCE(clubs.club_name, organizers.display_name, '') AS club_name,
               COALESCE(organizers.is_blacklisted, 0) AS organizer_is_blacklisted,
               COALESCE(organizers.verification_status, 'verified') AS organizer_verification_status,
               COALESCE((
                   SELECT COUNT(*) FROM participations
                   WHERE participations.event_id = events.event_id
                     AND participations.status IN ('requested', 'approved', 'attended')
               ), 0) AS participant_count
        FROM events
        LEFT JOIN clubs ON clubs.club_id = events.club_id
        LEFT JOIN organizers ON organizers.organizer_id = events.organizer_id
        WHERE events.status = 'published'
          AND (events.starts_at IS NULL OR events.starts_at > ?)
          AND (events.event_tier != 'official' OR events.approval_status = 'approved')
          AND (events.event_tier != 'micro' OR events.expires_at IS NULL OR events.expires_at > ?)
          AND COALESCE(organizers.is_blacklisted, 0) = 0
          AND (events.organizer_id IS NULL OR organizers.verification_status = 'verified')
          AND (events.quota <= 0 OR events.quota > COALESCE((
              SELECT COUNT(*) FROM participations
              WHERE participations.event_id = events.event_id
                AND participations.status IN ('requested', 'approved', 'attended')
          ), 0))
          AND (
              events.university_id = ? OR events.university_id = '' OR
              events.participation_mode IN ('online', 'hybrid')
          )
          AND (events.target_program_ids = '[]' OR events.target_program_ids LIKE ?)
          AND (events.target_class_years = '[]' OR events.target_class_years LIKE ?)
          AND NOT EXISTS (
              SELECT 1 FROM interactions
              WHERE interactions.profile_id = ?
                AND interactions.event_id = events.event_id
                AND interactions.action IN ('like', 'skip', 'apply')
          )
        ORDER BY events.starts_at ASC, events.event_id ASC
        LIMIT ?
        """,
        (
            now_iso,
            now_iso,
            profile["university_id"],
            f'%"{program_id}"%',
            f'%"{class_year}"%',
            profile["profile_id"],
            limit,
        ),
    ).fetchall()
    return [dict(row) for row in rows]


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
    """Etkinlik kimliğinden o profilin yaptığı hareketlere eşleme.

    Öneri sıralamasında beğenilen etkinlikleri öne, geçilenleri geriye almak için kullanılır.
    """
    rows = connection.execute(
        "SELECT event_id, action FROM interactions WHERE profile_id = ?", (profile_id,)
    ).fetchall()
    actions: dict[str, set[str]] = {}
    for row in rows:
        actions.setdefault(row["event_id"], set()).add(row["action"])
    return actions


def interaction_counts(connection: sqlite3.Connection) -> dict[str, int]:
    row = connection.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM clubs)        AS clubs,
            (SELECT COUNT(*) FROM events)       AS events,
            (SELECT COUNT(*) FROM students)     AS students,
            (SELECT COUNT(*) FROM profiles)     AS profiles,
            (SELECT COUNT(*) FROM interactions) AS interactions,
            (SELECT COUNT(*) FROM organizers)   AS organizers,
            (SELECT COUNT(*) FROM participations) AS participations,
            (SELECT COUNT(*) FROM ratings)      AS ratings,
            (SELECT COUNT(*) FROM user_interest_weights) AS interest_weights,
            (SELECT COUNT(*) FROM moderation_actions) AS moderation_actions
        """
    ).fetchone()
    return dict(row)
