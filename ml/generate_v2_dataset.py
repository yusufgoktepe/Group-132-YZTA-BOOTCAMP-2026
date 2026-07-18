"""CampusMatch V2 için tekrar üretilebilir profil, etkinlik ve etkileşim verisi."""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


SEED = 132
PROFILE_COUNT = 1_000
EVENT_COUNT = 500
INTERACTION_COUNT = 50_000
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "sample" / "v2"

UNIVERSITIES = ["yok-ankara", "yok-bogazici", "yok-hacettepe", "yok-itu", "yok-iyte", "yok-yildiz"]
PROGRAMS = [
    ("computer-engineering", "bachelor", 4),
    ("industrial-engineering", "bachelor", 4),
    ("business", "bachelor", 4),
    ("medicine", "bachelor", 6),
    ("psychology", "bachelor", 4),
    ("graphic-design", "bachelor", 4),
]
INTERESTS_BY_CATEGORY = {
    "technology": ["ai", "data-science", "mobile-development", "web-development", "cybersecurity", "game-development"],
    "career": ["entrepreneurship", "product", "finance", "career"],
    "science": ["engineering", "health-sciences", "social-sciences", "natural-sciences"],
    "design-art": ["ui-ux", "graphic-design", "photography", "music", "theatre"],
    "sports-health": ["sports", "wellbeing", "nutrition", "mental-health"],
    "social-impact": ["volunteering", "sustainability", "social-responsibility"],
    "culture-community": ["languages", "culture", "travel", "international-community"],
}
GOALS = ["learn", "network", "career", "build-project", "compete", "social-impact"]
EVENT_TYPES = ["workshop", "seminar", "conference", "networking", "competition", "social", "trip"]
MODES = ["onsite", "online", "hybrid"]
TITLE_TEMPLATES = {
    "technology": ["{topic} Atölyesi", "{topic} Buluşması", "{topic} Proje Günü"],
    "career": ["{topic} Kariyer Sohbeti", "{topic} Networking Günü", "{topic} Semineri"],
    "science": ["{topic} Araştırma Günleri", "{topic} Konferansı", "{topic} Laboratuvar Atölyesi"],
    "design-art": ["{topic} Tasarım Atölyesi", "{topic} Sahne Gecesi", "{topic} Sergisi"],
    "sports-health": ["{topic} Kampüs Buluşması", "{topic} Başlangıç Etkinliği", "{topic} Turnuvası"],
    "social-impact": ["{topic} Gönüllülük Günü", "{topic} Fikir Maratonu", "{topic} Topluluk Buluşması"],
    "culture-community": ["{topic} Kültür Buluşması", "{topic} Konuşma Kulübü", "{topic} Kampüs Gezisi"],
}


def write_csv(filename: str, rows: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_DIR / filename).open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate_profiles(rng: random.Random) -> list[dict]:
    all_interests = [item for values in INTERESTS_BY_CATEGORY.values() for item in values]
    profiles = []
    for index in range(1, PROFILE_COUNT + 1):
        program_id, level, duration = rng.choice(PROGRAMS)
        profiles.append(
            {
                "profile_id": index,
                "schema_version": "2.0",
                "university_id": rng.choice(UNIVERSITIES),
                "program_id": program_id,
                "education_level": level,
                "class_year": rng.randint(1, duration),
                "interest_ids": ";".join(rng.sample(all_interests, rng.randint(3, 8))),
                "participation_goal_ids": ";".join(rng.sample(GOALS, rng.randint(1, 3))),
                "participation_modes": ";".join(rng.sample(MODES, rng.randint(1, 2))),
                "fee_preference": rng.choice(["free_only", "paid_ok", "no_preference"]),
                "language_preference": rng.choice(["tr", "en", "no_preference"]),
            }
        )
    return profiles


def generate_events(rng: random.Random) -> list[dict]:
    start = datetime(2026, 8, 1, 9, tzinfo=timezone.utc)
    events = []
    for index in range(1, EVENT_COUNT + 1):
        category = rng.choice(list(INTERESTS_BY_CATEGORY))
        event_interests = rng.sample(INTERESTS_BY_CATEGORY[category], rng.randint(1, 3))
        topic = event_interests[0].replace("-", " ").title()
        starts_at = start + timedelta(days=rng.randint(0, 180), hours=rng.randint(0, 10))
        mode = rng.choice(MODES)
        fee_type = rng.choices(["free", "paid"], weights=[75, 25], k=1)[0]
        events.append(
            {
                "event_id": index,
                "schema_version": "2.0",
                "club_id": rng.randint(1, 80),
                "university_id": rng.choice(UNIVERSITIES),
                "title": rng.choice(TITLE_TEMPLATES[category]).format(topic=topic),
                "description": f"{topic} alanında öğrencileri buluşturan uygulamalı kampüs etkinliği.",
                "category_id": category,
                "interest_ids": ";".join(event_interests),
                "target_goal_ids": ";".join(rng.sample(GOALS, rng.randint(1, 3))),
                "event_type": rng.choice(EVENT_TYPES),
                "starts_at": starts_at.isoformat(),
                "ends_at": (starts_at + timedelta(hours=rng.randint(1, 4))).isoformat(),
                "participation_mode": mode,
                "location_name": "Online" if mode == "online" else f"Kampüs Salon {rng.randint(1, 20)}",
                "fee_type": fee_type,
                "fee_amount": 0 if fee_type == "free" else rng.choice([50, 100, 150, 200]),
                "quota": rng.choice([20, 30, 40, 50, 80, 100]),
                "language": rng.choices(["tr", "en", "mixed"], weights=[70, 20, 10], k=1)[0],
                "status": "published",
            }
        )
    return events


def generate_interactions(rng: random.Random, profiles: list[dict], events: list[dict]) -> list[dict]:
    interactions = []
    for index in range(1, INTERACTION_COUNT + 1):
        profile = rng.choice(profiles)
        event = rng.choice(events)
        interests = set(profile["interest_ids"].split(";"))
        event_interests = set(event["interest_ids"].split(";"))
        goals = set(profile["participation_goal_ids"].split(";"))
        event_goals = set(event["target_goal_ids"].split(";"))
        match_strength = min(1.0, 0.15 + len(interests & event_interests) * 0.35 + len(goals & event_goals) * 0.12)
        if profile["fee_preference"] == "free_only" and event["fee_type"] == "paid":
            match_strength *= 0.35
        if event["participation_mode"] not in profile["participation_modes"].split(";"):
            match_strength *= 0.7

        action = rng.choices(
            ["skip", "view_detail", "save", "like", "apply"],
            weights=[55 - 35 * match_strength, 22, 8 + 8 * match_strength, 8 + 14 * match_strength, 2 + 13 * match_strength],
            k=1,
        )[0]
        interactions.append(
            {
                "interaction_id": index,
                "profile_id": profile["profile_id"],
                "event_id": event["event_id"],
                "action": action,
                "dwell_time_seconds": rng.randint(1, 5) if action == "skip" else rng.randint(6, 90),
                "interest_overlap_count": len(interests & event_interests),
                "goal_overlap_count": len(goals & event_goals),
            }
        )
    return interactions


def main() -> None:
    rng = random.Random(SEED)
    profiles = generate_profiles(rng)
    events = generate_events(rng)
    interactions = generate_interactions(rng, profiles, events)
    write_csv("profiles_v2.csv", profiles)
    write_csv("events_v2.csv", events)
    write_csv("interactions_v2.csv", interactions)
    print(
        f"V2 data generated: {len(profiles)} profiles, "
        f"{len(events)} events, {len(interactions)} interactions"
    )


if __name__ == "__main__":
    main()
