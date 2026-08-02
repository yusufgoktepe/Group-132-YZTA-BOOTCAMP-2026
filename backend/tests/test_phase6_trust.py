"""Faz 6 anonim puanlama, güven eşiği ve moderasyon testleri."""

from __future__ import annotations

from backend.tests.test_phase5_events import _event_payload


def _attend(client, owner_id: str, profile_id: str, event_id: str) -> dict:
    participation = client.post(
        f"/events/{event_id}/apply", json={"profile_id": profile_id}
    ).json()
    approved = client.patch(
        f"/participations/{participation['participation_id']}",
        json={"actor_profile_id": owner_id, "status": "approved"},
    )
    assert approved.status_code == 200
    attended = client.patch(
        f"/participations/{participation['participation_id']}",
        json={"actor_profile_id": owner_id, "status": "attended"},
    )
    assert attended.status_code == 200
    return attended.json()


def test_rating_requires_verified_attendance_and_response_is_anonymous(
    client, created_profile, valid_profile
):
    event = client.post(
        "/events", json=_event_payload(created_profile["profile_id"], quota=5)
    ).json()
    participant = client.post(
        "/profiles", json={**valid_profile, "display_name": "Puanlayan"}
    ).json()

    denied = client.post(
        f"/events/{event['event_id']}/ratings",
        json={"profile_id": participant["profile_id"], "score": 5},
    )
    assert denied.status_code == 403

    _attend(client, created_profile["profile_id"], participant["profile_id"], event["event_id"])
    rating = client.post(
        f"/events/{event['event_id']}/ratings",
        json={"profile_id": participant["profile_id"], "score": 5},
    )
    duplicate = client.post(
        f"/events/{event['event_id']}/ratings",
        json={"profile_id": participant["profile_id"], "score": 4},
    )

    assert rating.status_code == 201
    assert rating.json()["is_anonymous"] is True
    assert "rater_profile_id" not in rating.json()
    assert "profile_id" not in rating.json()
    assert duplicate.status_code == 409


def test_three_low_ratings_block_publishing_remove_feed_and_create_moderation(
    client, created_profile, valid_profile, monkeypatch
):
    monkeypatch.setenv("CAMPUSMATCH_MODERATOR_KEY", "phase6-test-key")
    event = client.post(
        "/events", json=_event_payload(created_profile["profile_id"], quota=5)
    ).json()
    profiles = [
        client.post(
            "/profiles", json={**valid_profile, "display_name": f"Puanlayan {index}"}
        ).json()
        for index in range(3)
    ]
    for profile in profiles:
        _attend(client, created_profile["profile_id"], profile["profile_id"], event["event_id"])
        response = client.post(
            f"/events/{event['event_id']}/ratings",
            json={"profile_id": profile["profile_id"], "score": 1},
        )
        assert response.status_code == 201

    summary = client.get(f"/organizers/{event['organizer_id']}/trust-summary").json()
    assert summary["rating_count"] == 3
    assert summary["trust_score"] == 1.0
    assert summary["minimum_rating_threshold_met"] is True
    assert summary["publishing_blocked"] is True
    assert summary["open_moderation_action_count"] == 1

    feed = client.get("/feed", params={"profile_id": profiles[0]["profile_id"]}).json()
    assert event["event_id"] not in {item["event"]["event_id"] for item in feed["items"]}
    blocked = client.post("/events", json=_event_payload(created_profile["profile_id"]))
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "organizer_not_allowed"

    moderation = client.get(
        "/moderation/actions", headers={"X-Moderator-Key": "phase6-test-key"}
    ).json()
    assert any(
        action["organizer_id"] == event["organizer_id"]
        and action["action_type"] == "publish_block"
        for action in moderation["actions"]
    )


def test_official_verification_and_approval_require_moderator_key(client, monkeypatch):
    monkeypatch.setenv("CAMPUSMATCH_MODERATOR_KEY", "phase6-test-key")
    official = next(
        event for event in client.get("/events").json()["events"]
        if event["event_tier"] == "official" and event["organizer_id"]
    )
    body = {"approval_status": "rejected", "reason": "Demo moderasyon kontrolü"}

    denied = client.patch(f"/events/{official['event_id']}/approval", json=body)
    rejected = client.patch(
        f"/events/{official['event_id']}/approval",
        json=body,
        headers={"X-Moderator-Key": "phase6-test-key"},
    )
    verification = client.patch(
        f"/organizers/{official['organizer_id']}/verification",
        json={"verification_status": "rejected", "reason": "Kimlik doğrulaması başarısız"},
        headers={"X-Moderator-Key": "phase6-test-key"},
    )

    assert denied.status_code == 403
    assert rejected.status_code == 200
    assert rejected.json()["approval_status"] == "rejected"
    assert verification.status_code == 200
    assert verification.json()["verification_status"] == "rejected"
