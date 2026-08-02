"""Faz 2 feed, cursor ve interaction idempotency testleri."""

from __future__ import annotations

from datetime import datetime


def test_feed_returns_ranked_candidate_page(client, created_profile):
    response = client.get(
        "/feed", params={"profile_id": created_profile["profile_id"], "limit": 10}
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["schema_version"] == "3.0"
    assert payload["profile_id"] == created_profile["profile_id"]
    assert payload["feed_token"].startswith("feed-")
    assert 0 < len(payload["items"]) <= 10
    assert payload["candidate_count"] <= 30
    assert [item["score"] for item in payload["items"]] == sorted(
        (item["score"] for item in payload["items"]), reverse=True
    )
    assert all(item["reasons"] for item in payload["items"])
    assert all(len(item["reasons"]) <= 3 for item in payload["items"])


def test_official_osym_education_ids_match_v3_feed_aliases(client, valid_profile):
    profile = {
        **valid_profile,
        "education_reference_version": "osym-yks-2026-2026-07-30",
        "university_id": "osym-bogazici-universitesi",
        "university_name": "Boğaziçi Üniversitesi",
        "program_id": "osym-102210277",
        "program_name": "Bilgisayar Mühendisliği (İngilizce)",
    }
    profile_id = client.post("/profiles", json=profile).json()["profile_id"]
    payload = client.get("/feed", params={"profile_id": profile_id, "limit": 30}).json()

    assert payload["items"]
    assert any(
        item["event"]["university_id"] == "yok-bogazici"
        for item in payload["items"]
    )
    assert any(
        "computer-engineering" in item["event"]["target_program_ids"]
        for item in payload["items"]
    )


def test_feed_cursor_returns_a_non_overlapping_page(client, created_profile):
    first = client.get(
        "/feed", params={"profile_id": created_profile["profile_id"], "limit": 5}
    ).json()
    assert first["has_more"] is True
    assert first["next_cursor"]

    second = client.get(
        "/feed",
        params={
            "profile_id": created_profile["profile_id"],
            "limit": 5,
            "cursor": first["next_cursor"],
        },
    ).json()
    first_ids = {item["event"]["event_id"] for item in first["items"]}
    second_ids = {item["event"]["event_id"] for item in second["items"]}

    assert len(second_ids) == 5
    assert first_ids.isdisjoint(second_ids)


def test_cursor_session_is_bounded_to_thirty_unique_candidates(client, created_profile):
    cursor = None
    seen: set[str] = set()
    while True:
        response = client.get(
            "/feed",
            params={
                "profile_id": created_profile["profile_id"],
                "limit": 7,
                **({"cursor": cursor} if cursor else {}),
            },
        ).json()
        ids = [item["event"]["event_id"] for item in response["items"]]
        assert seen.isdisjoint(ids)
        seen.update(ids)
        cursor = response["next_cursor"]
        if not response["has_more"]:
            assert cursor is None
            break

    assert 1 <= len(seen) <= 30


def test_invalid_or_other_profile_cursor_is_rejected(client, created_profile, valid_profile):
    malformed = client.get(
        "/feed", params={"profile_id": created_profile["profile_id"], "cursor": "not-a-cursor"}
    )
    assert malformed.status_code == 400
    assert malformed.json()["error"]["code"] == "invalid_feed_cursor"

    first = client.get("/feed", params={"profile_id": created_profile["profile_id"], "limit": 5}).json()
    other = client.post("/profiles", json={**valid_profile, "display_name": "Başka Profil"}).json()
    mismatched = client.get(
        "/feed", params={"profile_id": other["profile_id"], "cursor": first["next_cursor"]}
    )
    assert mismatched.status_code == 400


def test_feed_rejects_unknown_profile_and_invalid_limit(client):
    missing = client.get("/feed", params={"profile_id": "profile-missing"})
    too_large = client.get("/feed", params={"profile_id": "profile-missing", "limit": 31})

    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "profile_not_found"
    assert too_large.status_code == 422


def test_feed_filters_expired_blocked_unapproved_full_and_consumed_events(client, created_profile):
    payload = client.get("/feed", params={"profile_id": created_profile["profile_id"]}).json()
    generated_at = datetime.fromisoformat(payload["generated_at"])

    for item in payload["items"]:
        event = item["event"]
        assert event["status"] == "published"
        assert event["organizer_is_blacklisted"] == 0
        assert event["organizer_verification_status"] == "verified"
        assert event["quota"] <= 0 or event["participant_count"] < event["quota"]
        if event["event_tier"] == "official":
            assert event["approval_status"] == "approved"
        if event["event_tier"] == "micro":
            assert datetime.fromisoformat(event["expires_at"]) > generated_at


def test_interaction_retry_is_idempotent_and_consumed_event_leaves_feed(client, created_profile):
    first_feed = client.get(
        "/feed", params={"profile_id": created_profile["profile_id"], "limit": 5}
    ).json()
    event_id = first_feed["items"][0]["event"]["event_id"]
    body = {
        "profile_id": created_profile["profile_id"],
        "event_id": event_id,
        "action": "like",
        "dwell_ms": 6200,
        "interaction_key": "interaction-retry-0001",
        "feed_token": first_feed["feed_token"],
    }

    first = client.post("/interactions", json=body)
    retry = client.post("/interactions", json=body)
    stored = client.get(f"/profiles/{created_profile['profile_id']}/interactions").json()
    next_feed = client.get("/feed", params={"profile_id": created_profile["profile_id"]}).json()

    assert first.status_code == retry.status_code == 201
    assert first.json()["interaction_id"] == retry.json()["interaction_id"]
    assert first.json()["is_duplicate"] is False
    assert retry.json()["is_duplicate"] is True
    assert stored["count"] == 1
    assert event_id not in {item["event"]["event_id"] for item in next_feed["items"]}


def test_apply_action_is_supported(client, created_profile):
    event_id = client.get("/feed", params={"profile_id": created_profile["profile_id"]}).json()[
        "items"
    ][0]["event"]["event_id"]
    response = client.post(
        "/interactions",
        json={
            "profile_id": created_profile["profile_id"],
            "event_id": event_id,
            "action": "apply",
            "interaction_key": "apply-action-0001",
        },
    )

    assert response.status_code == 201
    assert response.json()["action"] == "apply"


def test_interaction_key_cannot_be_reused_for_a_different_action(client, created_profile):
    events = client.get("/feed", params={"profile_id": created_profile["profile_id"]}).json()[
        "items"
    ]
    key = "interaction-conflict-0001"
    first = client.post(
        "/interactions",
        json={
            "profile_id": created_profile["profile_id"],
            "event_id": events[0]["event"]["event_id"],
            "action": "like",
            "interaction_key": key,
        },
    )
    conflict = client.post(
        "/interactions",
        json={
            "profile_id": created_profile["profile_id"],
            "event_id": events[1]["event"]["event_id"],
            "action": "skip",
            "interaction_key": key,
        },
    )

    assert first.status_code == 201
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "interaction_key_conflict"
