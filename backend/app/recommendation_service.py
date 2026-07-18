from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA_DIR = PROJECT_ROOT / "data" / "sample"


def _read_csv(filename: str) -> list[dict[str, str]]:
    with (SAMPLE_DATA_DIR / filename).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _split_tags(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(";") if item.strip()}


def _profile_score(student: dict[str, str], event: dict[str, str]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    interest_overlap = _split_tags(student["interests"]) & _split_tags(event["target_interests"])
    if interest_overlap:
        score += 40
        reasons.append(f"İlgi alanı uyumu: {', '.join(sorted(interest_overlap))}")

    if student["department"].lower() in event["target_departments"].lower():
        score += 25
        reasons.append("Bölüm bilgisi etkinliğin hedef kitlesiyle uyumlu.")

    if student["skill_level"].lower() == event["level"].lower():
        score += 20
        reasons.append("Etkinlik seviyesi yetkinlik seviyenle uyumlu.")

    if event["event_type"].lower() in _split_tags(student["preferred_event_types"]):
        score += 10
        reasons.append("Etkinlik türü tercihlerinle uyumlu.")

    location_preference = student["location_preference"].lower()
    location_type = event["location_type"].lower()
    if location_preference == location_type or location_type == "hybrid":
        score += 5
        reasons.append("Katılım biçimi tercihinle uyumlu.")

    return score, reasons


def _profile_v2_score(profile: dict[str, Any], event: dict[str, str]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    interest_overlap = set(profile["interest_ids"]) & _split_tags(event["target_interests"])
    if interest_overlap:
        score += min(50, 30 + (len(interest_overlap) - 1) * 10)
        reasons.append(f"İlgi alanı uyumu: {', '.join(sorted(interest_overlap))}")

    target_departments = event["target_departments"].lower()
    if target_departments == "all" or profile["program_name"].lower() in target_departments:
        score += 15
        reasons.append("Programın etkinliğin hedef kitlesiyle uyumlu.")

    goal_overlap = set(profile["participation_goal_ids"]) & _split_tags(event["target_goals"])
    if goal_overlap:
        score += 15
        reasons.append("Etkinlik katılım amaçlarından en az birini destekliyor.")

    if event["location_type"] in profile["participation_modes"]:
        score += 10
        reasons.append("Katılım biçimi tercihine uyuyor.")

    if profile["fee_preference"] != "free_only" or event["fee_type"] == "free":
        score += 5
        if profile["fee_preference"] == "free_only":
            reasons.append("Ücretsiz etkinlik tercihine uyuyor.")

    language_preference = profile["language_preference"]
    if language_preference == "no_preference" or event["language"] in {language_preference, "mixed"}:
        score += 5

    return score, reasons


@lru_cache(maxsize=1)
def _interaction_stats() -> dict[str, dict[str, float | int]]:
    totals: dict[str, int] = {}
    right_swipes: dict[str, int] = {}

    with (SAMPLE_DATA_DIR / "campusmatch_mvp_data.csv").open(
        encoding="utf-8-sig", newline=""
    ) as file:
        for row in csv.DictReader(file):
            event_id = row["etkinlik_id"]
            totals[event_id] = totals.get(event_id, 0) + 1
            right_swipes[event_id] = right_swipes.get(event_id, 0) + int(row["is_swiped_right"])

    return {
        event_id: {
            "interaction_count": total,
            "right_swipe_rate": right_swipes.get(event_id, 0) / total,
        }
        for event_id, total in totals.items()
    }


def list_students() -> list[dict[str, str]]:
    return _read_csv("students_sample.csv")


def list_clubs() -> list[dict[str, str]]:
    return _read_csv("clubs_sample.csv")


def list_events() -> list[dict[str, str]]:
    clubs = {club["club_id"]: club for club in list_clubs()}
    return [
        {**event, "club_name": clubs.get(event["club_id"], {}).get("club_name", "")}
        for event in _read_csv("events_sample.csv")
    ]


def recommend_for_student(student_id: str) -> dict[str, Any] | None:
    student = next(
        (item for item in list_students() if item["student_id"] == student_id),
        None,
    )
    if student is None:
        return None

    interaction_stats = _interaction_stats()
    recommendations = []

    for event in list_events():
        profile_score, reasons = _profile_score(student, event)
        stats = interaction_stats.get(
            event["event_id"], {"interaction_count": 0, "right_swipe_rate": 0.0}
        )
        interaction_score = float(stats["right_swipe_rate"]) * 100
        final_score = round(profile_score * 0.8 + interaction_score * 0.2, 1)

        recommendations.append(
            {
                "event": event,
                "score": final_score,
                "score_breakdown": {
                    "profile_match": profile_score,
                    "interaction_signal": round(interaction_score, 1),
                },
                "reasons": reasons,
                "interaction_stats": {
                    "interaction_count": stats["interaction_count"],
                    "right_swipe_rate": round(float(stats["right_swipe_rate"]), 4),
                },
            }
        )

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    return {"student_id": student_id, "recommendations": recommendations}


def recommend_for_profile(profile: dict[str, Any]) -> dict[str, Any]:
    interaction_stats = _interaction_stats()
    recommendations = []

    for event in list_events():
        profile_score, reasons = _profile_v2_score(profile, event)
        stats = interaction_stats.get(
            event["event_id"], {"interaction_count": 0, "right_swipe_rate": 0.0}
        )
        interaction_score = float(stats["right_swipe_rate"]) * 100
        final_score = round(profile_score * 0.8 + interaction_score * 0.2, 1)

        recommendations.append(
            {
                "event": event,
                "score": final_score,
                "score_breakdown": {
                    "profile_match": profile_score,
                    "interaction_signal": round(interaction_score, 1),
                },
                "reasons": reasons or ["Yeni ilgi alanlarını keşfetmen için önerildi."],
                "interaction_stats": {
                    "interaction_count": stats["interaction_count"],
                    "right_swipe_rate": round(float(stats["right_swipe_rate"]), 4),
                },
            }
        )

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    return {
        "schema_version": "2.0",
        "recommendation_source": "profile_and_interactions",
        "recommendations": recommendations,
    }
