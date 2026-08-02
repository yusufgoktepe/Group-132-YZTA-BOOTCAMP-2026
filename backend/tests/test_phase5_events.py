"""Faz 5 mikro etkinlik CRUD, sahiplik, kota ve katılım testleri."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _event_payload(profile_id: str, **overrides) -> dict:
    starts = datetime.now(timezone.utc) + timedelta(days=10)
    payload = {
        "creator_profile_id": profile_id,
        "title": "Kampüste Masa Oyunu Buluşması",
        "description": "Yeni insanlarla tanışmak için kısa bir masa oyunu buluşması.",
        "category_id": "community",
        "interest_ids": ["board-games", "social-community"],
        "target_goal_ids": ["socialize"],
        "starts_at": starts.isoformat(),
        "ends_at": (starts + timedelta(hours=2)).isoformat(),
        "expires_at": (starts + timedelta(hours=3)).isoformat(),
        "participation_mode": "onsite",
        "location_name": "Beytepe Kampüsü Öğrenci Merkezi",
        "quota": 2,
        "language": "tr",
    }
    return {**payload, **overrides}


def test_owner_can_create_update_and_cancel_micro_event(client, created_profile):
    created = client.post("/events", json=_event_payload(created_profile["profile_id"]))
    assert created.status_code == 201
    event = created.json()
    assert event["event_tier"] == "micro"
    assert event["status"] == "published"
    assert event["approval_status"] == "not_required"

    updated_payload = _event_payload(
        created_profile["profile_id"], title="Güncellenen Masa Oyunu Buluşması", quota=4
    )
    updated = client.put(f"/events/{event['event_id']}", json=updated_payload)
    assert updated.status_code == 200
    assert updated.json()["title"] == "Güncellenen Masa Oyunu Buluşması"
    assert updated.json()["quota"] == 4

    cancelled = client.delete(
        f"/events/{event['event_id']}",
        params={"actor_profile_id": created_profile["profile_id"]},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    feed = client.get("/feed", params={"profile_id": created_profile["profile_id"]}).json()
    assert event["event_id"] not in {item["event"]["event_id"] for item in feed["items"]}


def test_other_profile_cannot_edit_or_cancel_micro_event(client, created_profile, valid_profile):
    event = client.post("/events", json=_event_payload(created_profile["profile_id"])).json()
    other = client.post("/profiles", json={**valid_profile, "display_name": "Başka Öğrenci"}).json()

    update = client.put(
        f"/events/{event['event_id']}", json=_event_payload(other["profile_id"])
    )
    cancel = client.delete(
        f"/events/{event['event_id']}", params={"actor_profile_id": other["profile_id"]}
    )
    assert update.status_code == cancel.status_code == 403
    assert update.json()["error"]["code"] == "event_owner_required"


def test_micro_event_rejects_invalid_timeline(client, created_profile):
    starts = datetime.now(timezone.utc) + timedelta(days=5)
    response = client.post(
        "/events",
        json=_event_payload(
            created_profile["profile_id"],
            starts_at=starts.isoformat(),
            ends_at=(starts - timedelta(hours=1)).isoformat(),
            expires_at=(starts + timedelta(hours=1)).isoformat(),
        ),
    )
    assert response.status_code == 422


def test_participation_is_idempotent_and_quota_is_enforced(
    client, created_profile, valid_profile
):
    event = client.post(
        "/events", json=_event_payload(created_profile["profile_id"], quota=1)
    ).json()
    participant = client.post(
        "/profiles", json={**valid_profile, "display_name": "Katılımcı"}
    ).json()
    waiting = client.post(
        "/profiles", json={**valid_profile, "display_name": "Bekleyen"}
    ).json()

    first = client.post(
        f"/events/{event['event_id']}/apply", json={"profile_id": participant["profile_id"]}
    )
    retry = client.post(
        f"/events/{event['event_id']}/apply", json={"profile_id": participant["profile_id"]}
    )
    full = client.post(
        f"/events/{event['event_id']}/apply", json={"profile_id": waiting["profile_id"]}
    )

    assert first.status_code == retry.status_code == 201
    assert first.json()["participation_id"] == retry.json()["participation_id"]
    assert first.json()["is_duplicate"] is False
    assert retry.json()["is_duplicate"] is True
    assert full.status_code == 409
    assert full.json()["error"]["code"] == "event_quota_full"

    participations = client.get(
        f"/profiles/{participant['profile_id']}/participations"
    ).json()
    assert participations["count"] == 1
    assert participations["participations"][0]["status"] == "requested"


def test_owner_manages_participation_status_and_participant_can_cancel(
    client, created_profile, valid_profile
):
    event = client.post("/events", json=_event_payload(created_profile["profile_id"])).json()
    participant = client.post(
        "/profiles", json={**valid_profile, "display_name": "Katılımcı"}
    ).json()
    participation = client.post(
        f"/events/{event['event_id']}/apply", json={"profile_id": participant["profile_id"]}
    ).json()

    unauthorized = client.patch(
        f"/participations/{participation['participation_id']}",
        json={"actor_profile_id": participant["profile_id"], "status": "approved"},
    )
    approved = client.patch(
        f"/participations/{participation['participation_id']}",
        json={"actor_profile_id": created_profile["profile_id"], "status": "approved"},
    )
    attended = client.patch(
        f"/participations/{participation['participation_id']}",
        json={"actor_profile_id": created_profile["profile_id"], "status": "attended"},
    )
    assert unauthorized.status_code == 403
    assert approved.status_code == 200
    assert attended.json()["attendance_verified"] == 1
    assert attended.json()["verified_at"]

    second_event = client.post("/events", json=_event_payload(created_profile["profile_id"])).json()
    second = client.post(
        f"/events/{second_event['event_id']}/apply",
        json={"profile_id": participant["profile_id"]},
    ).json()
    cancelled = client.patch(
        f"/participations/{second['participation_id']}",
        json={"actor_profile_id": participant["profile_id"], "status": "cancelled"},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"


def test_quota_cannot_be_reduced_below_active_requests(client, created_profile, valid_profile):
    event = client.post("/events", json=_event_payload(created_profile["profile_id"], quota=3)).json()
    participant = client.post(
        "/profiles", json={**valid_profile, "display_name": "Katılımcı"}
    ).json()
    participant_two = client.post(
        "/profiles", json={**valid_profile, "display_name": "İkinci Katılımcı"}
    ).json()
    client.post(f"/events/{event['event_id']}/apply", json={"profile_id": participant["profile_id"]})
    client.post(f"/events/{event['event_id']}/apply", json={"profile_id": participant_two["profile_id"]})

    response = client.put(
        f"/events/{event['event_id']}",
        json=_event_payload(created_profile["profile_id"], quota=1),
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "event_not_editable"
