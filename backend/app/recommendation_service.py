"""Açıklanabilir, kural bazlı öneri skorlaması.

Skor üç sinyalin ağırlıklı birleşimidir:

- profil eşleşmesi (%80)
- sentetik swipe verisindeki sağa kaydırma oranı (%20)
- kullanıcının kendi `like` / `skip` hareketlerinden gelen düzeltme

Her öneri, hangi sinyalin katkı yaptığını gösteren `reasons` listesiyle döner.
"""

from __future__ import annotations

import csv
import json
import sqlite3
from functools import lru_cache
from typing import Any

from .db import SAMPLE_DATA_DIR
from . import repository

SCORING_STRATEGY = "explainable_rule_based_v3"

# Kullanıcının kendi hareketlerinin skora etkisi.
LIKE_BONUS = 8.0
SAVE_BONUS = 12.0
SKIP_PENALTY = 25.0


def _split_tags(value: str) -> set[str]:
    return {item.strip().lower() for item in (value or "").split(";") if item.strip()}


def _profile_score(student: dict[str, Any], event: dict[str, Any]) -> tuple[float, list[str]]:
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


def _profile_v2_score(profile: dict[str, Any], event: dict[str, Any]) -> tuple[float, list[str]]:
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

    if event["university_id"] == profile["university_id"]:
        score += 10
        reasons.append("Kendi üniversitendeki bir topluluk tarafından düzenleniyor.")

    if profile["fee_preference"] != "free_only" or event["fee_type"] == "free":
        score += 5
        if profile["fee_preference"] == "free_only":
            reasons.append("Ücretsiz etkinlik tercihine uyuyor.")

    language_preference = profile["language_preference"]
    if language_preference == "no_preference" or event["language"] in {language_preference, "mixed"}:
        score += 5

    return min(score, 100), reasons


@lru_cache(maxsize=1)
def _interaction_stats() -> dict[str, dict[str, float]]:
    """Sentetik swipe veri setinden etkinlik başına popülerlik sinyali."""
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


def _personal_adjustment(actions: set[str]) -> tuple[float, list[str]]:
    """Kullanıcının kendi hareketlerine göre skor düzeltmesi."""
    adjustment = 0.0
    reasons: list[str] = []

    if "save" in actions:
        adjustment += SAVE_BONUS
        reasons.append("Bu etkinliği daha önce kaydettin.")
    if "like" in actions:
        adjustment += LIKE_BONUS
        reasons.append("Benzer etkinlikleri beğendin.")
    if "skip" in actions:
        adjustment -= SKIP_PENALTY
        reasons.append("Daha önce geçtiğin için sıralamada geriye alındı.")

    return adjustment, reasons


def _build_recommendation(
    event: dict[str, Any],
    profile_score: float,
    reasons: list[str],
    actions: set[str],
    interest_weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    stats = _interaction_stats().get(
        event["event_id"], {"interaction_count": 0, "right_swipe_rate": 0.0}
    )
    interaction_score = float(stats["right_swipe_rate"]) * 100
    personal_adjustment, personal_reasons = _personal_adjustment(actions)
    event_interests = _split_tags(event.get("target_interests", ""))
    try:
        event_interests.update(
            str(item).lower() for item in json.loads(event.get("interest_ids") or "[]")
        )
    except (TypeError, ValueError):
        event_interests.update(_split_tags(event.get("interest_ids", "")))
    dynamic_match = min(1.0, sum((interest_weights or {}).get(item, 0.0) for item in event_interests))
    trust_score = max(0.0, min(5.0, float(event.get("organizer_trust_score") or 0.0))) / 5.0 * 100

    contributions = {
        "profile_match": round(profile_score * 0.65, 1),
        "dynamic_interest": round(dynamic_match * 20.0, 1),
        "organizer_trust": round(trust_score * 0.10, 1),
        "popularity": round(interaction_score * 0.05, 1),
        "personal_adjustment": round(personal_adjustment, 1),
    }
    final_score = round(max(0.0, min(100.0, sum(contributions.values()))), 1)

    dynamic_reasons = []
    if dynamic_match > 0:
        dynamic_reasons.append(
            f"Güncel ilgi profilinle %{round(dynamic_match * 100)} uyumlu."
        )
    if trust_score >= 80:
        dynamic_reasons.append("Güven puanı yüksek bir organizatör tarafından düzenleniyor.")
    explanation_reasons = (
        dynamic_reasons[:1]
        + personal_reasons[:1]
        + reasons
        + dynamic_reasons[1:]
        + personal_reasons[1:]
    )[:3]

    return {
        "event": event,
        "score": final_score,
        "score_breakdown": contributions,
        "reasons": explanation_reasons,
        "interaction_stats": {
            "interaction_count": int(stats["interaction_count"]),
            "right_swipe_rate": round(float(stats["right_swipe_rate"]), 4),
        },
    }


def recommend_for_student(
    connection: sqlite3.Connection, student_id: str
) -> dict[str, Any] | None:
    student = repository.get_student(connection, student_id)
    if student is None:
        return None

    recommendations = [
        _build_recommendation(event, *_profile_score(student, event), actions=set())
        for event in repository.list_events(connection)
    ]
    recommendations.sort(key=lambda item: item["score"], reverse=True)
    return {
        "student_id": student_id,
        "scoring_strategy": SCORING_STRATEGY,
        "recommendations": recommendations,
    }


def recommend_for_profile(
    connection: sqlite3.Connection,
    profile: dict[str, Any],
    profile_id: str | None = None,
) -> dict[str, Any]:
    """Profil için sıralı öneri listesi üretir.

    `profile_id` verilirse kullanıcının kaydedilmiş like/skip/save hareketleri
    de skora katılır.
    """
    recommendations = recommend_events_for_profile(
        connection,
        profile,
        repository.list_events(connection),
        profile_id=profile_id,
    )
    return {
        "schema_version": "2.0",
        "recommendation_source": "profile_and_interactions",
        "scoring_strategy": SCORING_STRATEGY,
        "profile_id": profile_id,
        "recommendations": recommendations,
    }


def recommend_events_for_profile(
    connection: sqlite3.Connection,
    profile: dict[str, Any],
    events: list[dict[str, Any]],
    profile_id: str | None = None,
) -> list[dict[str, Any]]:
    """Yalnız candidate generation tarafından seçilmiş etkinlikleri sıralar."""
    actions_by_event = (
        repository.profile_action_map(connection, profile_id) if profile_id else {}
    )
    interest_weights = repository.interest_weight_map(connection, profile_id) if profile_id else {}
    recommendations = []
    for event in events:
        profile_score, reasons = _profile_v2_score(profile, event)
        recommendation = _build_recommendation(
            event,
            profile_score,
            reasons,
            actions_by_event.get(event["event_id"], set()),
            interest_weights,
        )
        if not recommendation["reasons"]:
            recommendation["reasons"] = ["Yeni ilgi alanlarını keşfetmen için önerildi."]
        recommendations.append(recommendation)

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    return recommendations
