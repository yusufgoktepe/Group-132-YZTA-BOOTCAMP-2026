"""Faz 4 dinamik ilgi vektörü, dwell ve açıklanabilir ranking testleri."""

from __future__ import annotations

import json
from collections import defaultdict

import pytest


def _interest_ids(event: dict) -> list[str]:
    raw = event.get("interest_ids") or "[]"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [item for item in raw.split(";") if item]


def _two_events_with_shared_interest(client) -> tuple[dict, dict, str]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for event in client.get("/events").json()["events"]:
        for interest_id in _interest_ids(event):
            grouped[interest_id].append(event)
    interest_id, events = next(
        (interest_id, events)
        for interest_id, events in grouped.items()
        if len(events) >= 2
    )
    return events[0], events[1], interest_id


def test_interaction_updates_normalized_interest_vector_once(client, created_profile):
    source_event, _, interest_id = _two_events_with_shared_interest(client)
    body = {
        "profile_id": created_profile["profile_id"],
        "event_id": source_event["event_id"],
        "action": "like",
        "dwell_ms": 9_000,
        "interaction_key": "phase4-idempotent-like",
    }

    first = client.post("/interactions", json=body)
    before_retry = client.get(
        f"/profiles/{created_profile['profile_id']}/interest-weights"
    ).json()["weights"]
    retry = client.post("/interactions", json=body)
    after_retry = client.get(
        f"/profiles/{created_profile['profile_id']}/interest-weights"
    ).json()["weights"]

    assert first.status_code == retry.status_code == 201
    assert retry.json()["is_duplicate"] is True
    assert before_retry == after_retry
    assert abs(sum(row["weight"] for row in after_retry) - 1.0) < 0.000001
    learned = next(row for row in after_retry if row["interest_id"] == interest_id)
    assert learned["behavior_weight"] == pytest.approx(0.17)


def test_long_dwell_strengthens_related_event_more_than_short_dwell(
    client, valid_profile
):
    source_event, related_event, interest_id = _two_events_with_shared_interest(client)
    short_profile = client.post(
        "/profiles", json={**valid_profile, "display_name": "Kısa İzleme"}
    ).json()
    long_profile = client.post(
        "/profiles", json={**valid_profile, "display_name": "Uzun İzleme"}
    ).json()

    for profile, dwell_ms, key in (
        (short_profile, 1_000, "phase4-short-dwell"),
        (long_profile, 9_000, "phase4-long-dwell"),
    ):
        response = client.post(
            "/interactions",
            json={
                "profile_id": profile["profile_id"],
                "event_id": source_event["event_id"],
                "action": "view_detail",
                "dwell_ms": dwell_ms,
                "interaction_key": key,
            },
        )
        assert response.status_code == 201

    short_weights = client.get(
        f"/profiles/{short_profile['profile_id']}/interest-weights"
    ).json()["weights"]
    long_weights = client.get(
        f"/profiles/{long_profile['profile_id']}/interest-weights"
    ).json()["weights"]
    short_weight = next(row["weight"] for row in short_weights if row["interest_id"] == interest_id)
    long_weight = next(row["weight"] for row in long_weights if row["interest_id"] == interest_id)
    assert long_weight > short_weight

    short_recs = client.post(
        f"/recommendations/profile/{short_profile['profile_id']}"
    ).json()["recommendations"]
    long_recs = client.post(
        f"/recommendations/profile/{long_profile['profile_id']}"
    ).json()["recommendations"]
    short_score = next(
        item["score"] for item in short_recs if item["event"]["event_id"] == related_event["event_id"]
    )
    long_item = next(
        item for item in long_recs if item["event"]["event_id"] == related_event["event_id"]
    )
    assert long_item["score"] > short_score
    assert long_item["score_breakdown"]["dynamic_interest"] > 0
    assert any("Güncel ilgi profilinle" in reason for reason in long_item["reasons"])
