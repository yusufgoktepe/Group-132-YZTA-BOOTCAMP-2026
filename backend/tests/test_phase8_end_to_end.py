"""Faz 8 ana demo yolunun tek veritabanında uçtan uca kabul testi."""

from __future__ import annotations

from backend.tests.test_phase5_events import _event_payload
from backend.tests.test_phase6_trust import _attend


def test_complete_student_creator_and_trust_demo_flow(
    client, created_profile, valid_profile, monkeypatch
):
    monkeypatch.setenv("CAMPUSMATCH_MODERATOR_KEY", "phase8-demo-key")
    creator_id = created_profile["profile_id"]

    initial_feed = client.get("/feed", params={"profile_id": creator_id, "limit": 5})
    assert initial_feed.status_code == 200
    first_item = initial_feed.json()["items"][0]
    interaction = {
        "profile_id": creator_id,
        "event_id": first_item["event"]["event_id"],
        "action": "save",
        "dwell_ms": 9_000,
        "interaction_key": "phase8-offline-retry-key",
        "feed_token": initial_feed.json()["feed_token"],
    }
    saved = client.post("/interactions", json=interaction)
    retried = client.post("/interactions", json=interaction)
    assert saved.status_code == retried.status_code == 201
    assert retried.json()["is_duplicate"] is True
    assert client.get(f"/profiles/{creator_id}/saved-events").json()["count"] == 1

    micro = client.post("/events", json=_event_payload(creator_id, quota=5))
    assert micro.status_code == 201
    event = micro.json()

    participants = [
        client.post(
            "/profiles", json={**valid_profile, "display_name": f"Demo Katılımcı {index}"}
        ).json()
        for index in range(3)
    ]
    for profile in participants:
        attendance = _attend(client, creator_id, profile["profile_id"], event["event_id"])
        assert attendance["attendance_verified"] == 1
        rating = client.post(
            f"/events/{event['event_id']}/ratings",
            json={"profile_id": profile["profile_id"], "score": 1},
        )
        assert rating.status_code == 201
        assert "profile_id" not in rating.json()

    trust = client.get(f"/organizers/{event['organizer_id']}/trust-summary").json()
    assert trust["publishing_blocked"] is True
    assert trust["rating_count"] == 3
    assert client.post("/events", json=_event_payload(creator_id)).status_code == 403

    refreshed_feed = client.get(
        "/feed", params={"profile_id": participants[0]["profile_id"]}
    ).json()
    assert event["event_id"] not in {
        item["event"]["event_id"] for item in refreshed_feed["items"]
    }
    actions = client.get(
        "/moderation/actions", headers={"X-Moderator-Key": "phase8-demo-key"}
    ).json()["actions"]
    assert any(
        item["organizer_id"] == event["organizer_id"]
        and item["action_type"] == "publish_block"
        for item in actions
    )
