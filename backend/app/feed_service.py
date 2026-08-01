"""Cursor tabanlı feed candidate generation ve açıklanabilir sıralama."""

from __future__ import annotations

import base64
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from . import repository
from .recommendation_service import SCORING_STRATEGY, recommend_events_for_profile

CANDIDATE_POOL_SIZE = 30
CURSOR_VERSION = 1


def _encode_cursor(profile_id: str, remaining_event_ids: list[str]) -> str:
    payload = json.dumps(
        {"v": CURSOR_VERSION, "profile_id": profile_id, "remaining": remaining_event_ids},
        separators=(",", ":"),
    ).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def _decode_cursor(cursor: str | None, profile_id: str) -> list[str] | None:
    if not cursor:
        return None
    try:
        padding = "=" * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(cursor + padding))
        if payload.get("v") != CURSOR_VERSION or payload.get("profile_id") != profile_id:
            raise ValueError
        remaining = payload["remaining"]
        if not isinstance(remaining, list) or len(remaining) > CANDIDATE_POOL_SIZE:
            raise ValueError
        if not all(isinstance(event_id, str) and event_id for event_id in remaining):
            raise ValueError
        return list(dict.fromkeys(remaining))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError("Geçersiz veya başka profile ait feed cursor değeri.") from exc


def build_feed(
    connection: sqlite3.Connection,
    profile: dict[str, Any],
    *,
    cursor: str | None,
    limit: int,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    remaining_event_ids = _decode_cursor(cursor, profile["profile_id"])
    if remaining_event_ids is None:
        candidates = repository.list_feed_candidates(
            connection, profile, now.isoformat(), CANDIDATE_POOL_SIZE
        )
    else:
        safe_candidates = repository.list_feed_candidates(
            connection, profile, now.isoformat(), 300
        )
        by_id = {event["event_id"]: event for event in safe_candidates}
        candidates = [by_id[event_id] for event_id in remaining_event_ids if event_id in by_id]
    ranked = recommend_events_for_profile(
        connection,
        profile,
        candidates,
        profile_id=profile["profile_id"],
    )
    page = ranked[:limit]
    has_more = len(ranked) > len(page)
    next_remaining = [item["event"]["event_id"] for item in ranked[len(page) :]]
    feed_token = f"feed-{uuid.uuid4().hex}"

    return {
        "schema_version": "3.0",
        "profile_id": profile["profile_id"],
        "feed_token": feed_token,
        "generated_at": now.isoformat(),
        "candidate_count": len(candidates),
        "scoring_strategy": SCORING_STRATEGY,
        "items": page,
        "next_cursor": _encode_cursor(profile["profile_id"], next_remaining) if has_more else None,
        "has_more": has_more,
    }
