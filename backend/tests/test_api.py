"""Backend endpoint testleri."""

from __future__ import annotations

import pytest


# --- Sağlık ve referans veri ---------------------------------------------


def test_health_reports_seeded_database(client):
    payload = client.get("/health").json()

    assert payload["status"] == "ok"
    assert payload["database"]["counts"]["events"] > 0
    assert payload["database"]["counts"]["clubs"] > 0


def test_events_are_served_from_database_with_club_name(client):
    payload = client.get("/events").json()

    assert payload["count"] == len(payload["events"])
    assert all(event["club_name"] for event in payload["events"])


def test_events_can_be_filtered_by_category(client):
    payload = client.get("/events", params={"category": "technology"}).json()

    assert payload["count"] > 0
    assert {event["category"] for event in payload["events"]} == {"technology"}


def test_single_event_is_returned(client):
    event_id = client.get("/events").json()["events"][0]["event_id"]

    assert client.get(f"/events/{event_id}").json()["event_id"] == event_id


def test_unknown_event_returns_readable_error(client):
    response = client.get("/events/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "event_not_found"


def test_clubs_and_students_endpoints_return_rows(client):
    assert len(client.get("/clubs").json()["clubs"]) > 0
    assert len(client.get("/students").json()["students"]) > 0


# --- Profiller ------------------------------------------------------------


def test_profile_is_persisted_and_can_be_read_back(client, valid_profile):
    created = client.post("/profiles", json=valid_profile).json()

    assert created["profile_id"].startswith("profile-")
    assert created["interest_ids"] == valid_profile["interest_ids"]

    fetched = client.get(f"/profiles/{created['profile_id']}").json()
    assert fetched == created


def test_profile_survives_a_new_connection(client, created_profile):
    """Profil bellekte değil veritabanında tutulur."""
    from backend.app import repository
    from backend.app.db import connect

    connection = connect()
    try:
        stored = repository.get_profile(connection, created_profile["profile_id"])
    finally:
        connection.close()

    assert stored["display_name"] == created_profile["display_name"]


def test_profile_can_be_updated(client, created_profile, valid_profile):
    changed = {**valid_profile, "display_name": "Zeynep D.", "class_year": "3"}

    updated = client.put(f"/profiles/{created_profile['profile_id']}", json=changed).json()

    assert updated["display_name"] == "Zeynep D."
    assert updated["class_year"] == "3"
    assert updated["created_at"] == created_profile["created_at"]


def test_updating_unknown_profile_returns_404(client, valid_profile):
    response = client.put("/profiles/profile-missing", json=valid_profile)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "profile_not_found"


@pytest.mark.parametrize(
    ("field", "value", "expected_field"),
    [
        ("interest_ids", ["ai"], "interest_ids"),
        ("class_year", "9", "class_year"),
        ("education_level", "unknown", "education_level"),
        ("program_duration", 12, "program_duration"),
        ("participation_modes", [], "participation_modes"),
    ],
)
def test_invalid_profile_reports_the_failing_field(client, valid_profile, field, value, expected_field):
    response = client.post("/profiles", json={**valid_profile, field: value})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert expected_field in {item["field"] for item in body["error"]["fields"]}
    assert body["detail"]


def test_missing_field_is_reported_in_turkish(client, valid_profile):
    incomplete = {key: value for key, value in valid_profile.items() if key != "university_id"}

    body = client.post("/profiles", json=incomplete).json()

    messages = {item["field"]: item["message"] for item in body["error"]["fields"]}
    assert messages["university_id"] == "Bu alan zorunlu."


# --- Kullanıcı hareketleri ------------------------------------------------


@pytest.mark.parametrize("action", ["like", "skip", "save", "unsave", "view_detail"])
def test_every_action_type_is_recorded(client, created_profile, action):
    response = client.post(
        "/interactions",
        json={"profile_id": created_profile["profile_id"], "event_id": "1", "action": action},
    )

    assert response.status_code == 201
    assert response.json()["action"] == action

    stored = client.get(
        f"/profiles/{created_profile['profile_id']}/interactions", params={"action": action}
    ).json()
    assert stored["count"] == 1


def test_interaction_for_unknown_profile_is_rejected(client):
    response = client.post(
        "/interactions",
        json={"profile_id": "profile-missing", "event_id": "1", "action": "like"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "profile_not_found"


def test_interaction_for_unknown_event_is_rejected(client, created_profile):
    response = client.post(
        "/interactions",
        json={"profile_id": created_profile["profile_id"], "event_id": "999", "action": "like"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "event_not_found"


def test_invalid_action_is_rejected(client, created_profile):
    response = client.post(
        "/interactions",
        json={"profile_id": created_profile["profile_id"], "event_id": "1", "action": "swipe"},
    )

    assert response.status_code == 422
    assert "action" in {item["field"] for item in response.json()["error"]["fields"]}


def test_saved_events_follow_the_latest_save_or_unsave(client, created_profile):
    profile_id = created_profile["profile_id"]

    def act(event_id: str, action: str):
        client.post(
            "/interactions",
            json={"profile_id": profile_id, "event_id": event_id, "action": action},
        )

    act("1", "save")
    act("2", "save")
    act("1", "unsave")

    saved = client.get(f"/profiles/{profile_id}/saved-events").json()

    assert [event["event_id"] for event in saved["events"]] == ["2"]

    act("1", "save")
    saved_again = client.get(f"/profiles/{profile_id}/saved-events").json()
    assert {event["event_id"] for event in saved_again["events"]} == {"1", "2"}


# --- Öneriler -------------------------------------------------------------


def test_recommendations_are_sorted_and_explained(client, valid_profile):
    payload = client.post("/recommendations/profile", json=valid_profile).json()
    recommendations = payload["recommendations"]

    assert payload["schema_version"] == "2.0"
    assert len(recommendations) == client.get("/events").json()["count"]
    assert [item["score"] for item in recommendations] == sorted(
        (item["score"] for item in recommendations), reverse=True
    )
    for item in recommendations:
        assert 0 <= item["score"] <= 100
        assert item["reasons"], "her öneri en az bir gerekçe içermeli"
        assert len(item["reasons"]) <= 3
        assert set(item["score_breakdown"]) == {
            "profile_match",
            "dynamic_interest",
            "organizer_trust",
            "popularity",
            "personal_adjustment",
        }


def test_different_profiles_get_different_ranking(client, valid_profile):
    design_profile = {
        **valid_profile,
        "program_name": "Grafik Tasarımı",
        "interest_ids": ["ui-ux", "graphic-design", "photography"],
        "participation_modes": ["online"],
        "fee_preference": "paid_ok",
    }

    tech_top = client.post("/recommendations/profile", json=valid_profile).json()
    design_top = client.post("/recommendations/profile", json=design_profile).json()

    assert (
        tech_top["recommendations"][0]["event"]["event_id"]
        != design_top["recommendations"][0]["event"]["event_id"]
    )


def test_saved_profile_recommendations_react_to_user_actions(client, created_profile):
    profile_id = created_profile["profile_id"]
    before = client.post(f"/recommendations/profile/{profile_id}").json()
    top_event_id = before["recommendations"][0]["event"]["event_id"]

    client.post(
        "/interactions",
        json={"profile_id": profile_id, "event_id": top_event_id, "action": "skip"},
    )

    after = client.post(f"/recommendations/profile/{profile_id}").json()
    scores = {item["event"]["event_id"]: item["score"] for item in after["recommendations"]}
    before_scores = {item["event"]["event_id"]: item["score"] for item in before["recommendations"]}

    assert scores[top_event_id] < before_scores[top_event_id]
    assert after["profile_id"] == profile_id


def test_recommendations_for_unknown_profile_return_404(client):
    response = client.post("/recommendations/profile/profile-missing")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "profile_not_found"


def test_student_recommendations_still_work(client):
    payload = client.post("/recommendations/student/1").json()

    assert payload["student_id"] == "1"
    assert len(payload["recommendations"]) > 0


def test_unknown_student_returns_404(client):
    response = client.post("/recommendations/student/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "student_not_found"


def test_mobile_contract_fields_are_stable(client, valid_profile):
    """Mobil uygulama `event.event_id`, `score` ve `reasons` alanlarına bağımlıdır."""
    first = client.post("/recommendations/profile", json=valid_profile).json()["recommendations"][0]

    assert isinstance(first["event"]["event_id"], str)
    assert isinstance(first["score"], (int, float))
    assert isinstance(first["reasons"], list)
