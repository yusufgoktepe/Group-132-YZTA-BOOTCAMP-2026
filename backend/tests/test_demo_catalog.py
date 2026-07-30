from __future__ import annotations

import json
from pathlib import Path


def test_catalog_has_enough_variety_for_demo(client) -> None:
    events = client.get("/events").json()["events"]
    clubs = client.get("/clubs").json()["clubs"]

    assert len(events) == 56
    assert len(clubs) == 14
    assert len({event["category"] for event in events}) >= 7
    assert len({event["event_id"] for event in events}) == len(events)
    assert all(event["time"] and event["location"] for event in events)


def test_mobile_fallback_uses_the_same_event_ids(client) -> None:
    project_root = Path(__file__).resolve().parents[2]
    with (project_root / "mobile" / "data" / "demo-events.json").open(
        encoding="utf-8"
    ) as file:
        mobile_events = json.load(file)

    backend_events = client.get("/events").json()["events"]
    backend_ids = {f"event-{event['event_id']}" for event in backend_events}
    mobile_ids = {event["id"] for event in mobile_events}
    assert backend_ids == mobile_ids


def test_profile_receives_the_full_ranked_catalog(client, valid_profile) -> None:
    result = client.post("/recommendations/profile", json=valid_profile).json()
    recommendations = result["recommendations"]

    assert len(recommendations) == 56
    assert recommendations[0]["score"] >= recommendations[-1]["score"]
    assert all(0 <= item["score"] <= 100 for item in recommendations)
    assert all(item["reasons"] for item in recommendations)
