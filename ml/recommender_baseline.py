"""
Baseline recommendation logic for CampusMatch AI.

This is a simple, explainable, score-based prototype.
It can be improved with TF-IDF, embeddings or interaction-based models later.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def _split_tags(value: str) -> set[str]:
    if not value:
        return set()
    return {item.strip().lower() for item in value.split(";") if item.strip()}


def calculate_recommendation_score(student: Dict, event: Dict) -> Tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    student_interests = _split_tags(student.get("interests", ""))
    event_interests = _split_tags(event.get("target_interests", ""))
    interest_overlap = student_interests.intersection(event_interests)

    if interest_overlap:
        score += 40
        reasons.append(f"İlgi alanı uyumu: {', '.join(sorted(interest_overlap))}")

    student_department = str(student.get("department", "")).lower()
    target_departments = str(event.get("target_departments", "")).lower()

    if student_department and student_department in target_departments:
        score += 25
        reasons.append("Bölüm bilgisi etkinliğin hedef kitlesiyle uyumlu.")

    if str(student.get("skill_level", "")).lower() == str(event.get("level", "")).lower():
        score += 20
        reasons.append("Etkinlik seviyesi öğrencinin yetkinlik seviyesiyle uyumlu.")

    preferred_types = _split_tags(student.get("preferred_event_types", ""))
    event_type = str(event.get("event_type", "")).lower()

    if event_type in preferred_types:
        score += 10
        reasons.append("Etkinlik türü öğrencinin tercihleriyle uyumlu.")

    location_pref = str(student.get("location_preference", "")).lower()
    location_type = str(event.get("location_type", "")).lower()

    if location_pref == location_type or location_type == "hybrid":
        score += 5
        reasons.append("Lokasyon/format tercihi uyumlu.")

    return score, reasons


if __name__ == "__main__":
    demo_student = {
        "interests": "data science;ai;business analytics",
        "department": "Management Information Systems",
        "skill_level": "beginner",
        "preferred_event_types": "workshop;seminar",
        "location_preference": "hybrid",
    }

    demo_event = {
        "target_interests": "data science;python;ai",
        "target_departments": "Management Information Systems;Computer Engineering;Statistics",
        "level": "beginner",
        "event_type": "workshop",
        "location_type": "hybrid",
    }

    demo_score, demo_reasons = calculate_recommendation_score(demo_student, demo_event)
    print("Score:", demo_score)
    print("Reasons:")
    for reason in demo_reasons:
        print("-", reason)
