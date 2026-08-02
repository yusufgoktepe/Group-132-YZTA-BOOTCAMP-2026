"""Faz 1 için V2 örneklerini iki katmanlı V3 veri setine dönüştürür.

Çıktı hedefi PDF kapsamıyla sınırlıdır: 80 resmî ve 170 mikro etkinlik.
V2 dosyaları korunur; V3 çıktıları ``data/sample/v3`` altında yeniden üretilebilir.
"""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


SEED = 132
OFFICIAL_EVENT_COUNT = 80
MICRO_EVENT_COUNT = 170
ORGANIZER_COUNT = 80
PROJECT_ROOT = Path(__file__).resolve().parent.parent
V2_DIR = PROJECT_ROOT / "data" / "sample" / "v2"
OUTPUT_DIR = PROJECT_ROOT / "data" / "sample" / "v3"
GENERATED_AT = datetime(2026, 8, 1, 9, tzinfo=timezone.utc)

CITY_BY_UNIVERSITY = {
    "yok-ankara": "ankara",
    "yok-bogazici": "istanbul",
    "yok-hacettepe": "ankara",
    "yok-itu": "istanbul",
    "yok-iyte": "izmir",
    "yok-yildiz": "istanbul",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_organizers(rng: random.Random) -> list[dict]:
    organizers = []
    for index in range(1, ORGANIZER_COUNT + 1):
        official = index <= 30
        organizer_type = rng.choice(["club", "university", "municipality", "company"]) if official else "student"
        rating_count = rng.randint(3, 80) if index % 9 else rng.randint(0, 2)
        is_blacklisted = not official and index in {72, 74, 76, 78, 80}
        trust_score = round(rng.uniform(1.2, 1.9), 2) if is_blacklisted else round(rng.uniform(3.2, 5.0), 2)
        university_id = rng.choice(list(CITY_BY_UNIVERSITY))
        organizers.append(
            {
                "organizer_id": f"organizer-v3-{index:03d}",
                "schema_version": "3.0",
                "user_id": "" if official else f"student-v3-{index:04d}",
                "organizer_type": organizer_type,
                "display_name": f"CampusMatch {'Kurum' if official else 'Öğrenci'} {index}",
                "university_id": university_id,
                "verification_status": "verified",
                "trust_score": trust_score,
                "rating_count": rating_count,
                "is_blacklisted": str(is_blacklisted).lower(),
                "blacklist_reason": "Güven ortalaması 2.0 altında" if is_blacklisted else "",
                "created_at": GENERATED_AT.isoformat(),
                "updated_at": GENERATED_AT.isoformat(),
            }
        )
    return organizers


def build_events(source: list[dict[str, str]], organizers: list[dict], rng: random.Random) -> list[dict]:
    selected = source[: OFFICIAL_EVENT_COUNT + MICRO_EVENT_COUNT]
    official_organizers = organizers[:30]
    student_organizers = organizers[30:]
    events = []

    for index, row in enumerate(selected, start=1):
        official = index <= OFFICIAL_EVENT_COUNT
        organizer = rng.choice(official_organizers if official else student_organizers)
        tier = "official" if official else "micro"
        starts_at = datetime.fromisoformat(row["starts_at"])
        if starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=timezone.utc)
        ends_at = datetime.fromisoformat(row["ends_at"])
        if ends_at.tzinfo is None:
            ends_at = ends_at.replace(tzinfo=timezone.utc)
        expires_at = "" if official else (starts_at - timedelta(minutes=30)).isoformat()
        university_id = row["university_id"]
        program_targets = "" if official and index % 3 else rng.choice(
            ["computer-engineering", "industrial-engineering", "business", "psychology"]
        )
        class_targets = "" if index % 4 else rng.choice(["1", "2", "3", "4"])

        events.append(
            {
                "event_id": f"event-v3-{index:04d}",
                "schema_version": "3.0",
                "organizer_id": organizer["organizer_id"],
                "event_tier": tier,
                "university_id": university_id,
                "campus_id": f"{university_id}-main",
                "city_id": CITY_BY_UNIVERSITY[university_id],
                "title": row["title"] if official else f"Mikro: {row['title']}",
                "description": row["description"],
                "category_id": row["category_id"],
                "interest_ids": row["interest_ids"],
                "target_program_ids": program_targets,
                "target_class_years": class_targets,
                "target_goal_ids": row["target_goal_ids"],
                "event_type": row["event_type"],
                "starts_at": starts_at.isoformat(),
                "ends_at": ends_at.isoformat(),
                "expires_at": expires_at,
                "participation_mode": row["participation_mode"],
                "location_name": row["location_name"],
                "fee_type": row["fee_type"],
                "fee_amount": row["fee_amount"],
                "quota": row["quota"],
                "language": row["language"],
                "status": "published",
                "approval_status": "approved" if official else "not_required",
                "organizer_trust_score": organizer["trust_score"],
                "image_url": "",
            }
        )
    return events


def build_participations(events: list[dict], rng: random.Random) -> list[dict]:
    rows = []
    seen: set[tuple[str, str]] = set()
    while len(rows) < 1200:
        event = rng.choice(events)
        profile_id = f"profile-v3-{rng.randint(1, 1000):04d}"
        key = (profile_id, event["event_id"])
        if key in seen:
            continue
        seen.add(key)
        index = len(rows) + 1
        attended = index <= 800
        requested_at = datetime.fromisoformat(event["starts_at"]) - timedelta(days=rng.randint(1, 20))
        rows.append(
            {
                "participation_id": f"participation-v3-{index:05d}",
                "schema_version": "3.0",
                "profile_id": profile_id,
                "event_id": event["event_id"],
                "status": "attended" if attended else "approved",
                "attendance_verified": str(attended).lower(),
                "requested_at": requested_at.isoformat(),
                "verified_at": event["ends_at"] if attended else "",
            }
        )
    return rows


def build_ratings(participations: list[dict], event_map: dict[str, dict], rng: random.Random) -> list[dict]:
    ratings = []
    seen: set[tuple[str, str]] = set()
    for participation in participations:
        if participation["attendance_verified"] != "true":
            continue
        key = (participation["event_id"], participation["profile_id"])
        if key in seen:
            continue
        seen.add(key)
        event = event_map[participation["event_id"]]
        ratings.append(
            {
                "rating_id": f"rating-v3-{len(ratings) + 1:05d}",
                "schema_version": "3.0",
                "event_id": event["event_id"],
                "organizer_id": event["organizer_id"],
                "rater_profile_id": participation["profile_id"],
                "score": rng.choices([1, 2, 3, 4, 5], weights=[3, 5, 15, 37, 40], k=1)[0],
                "created_at": event["ends_at"],
            }
        )
    return ratings


def build_interest_weights(profiles: list[dict[str, str]]) -> list[dict]:
    rows = []
    for profile in profiles:
        interests = profile["interest_ids"].split(";")
        explicit_weight = round(1 / len(interests), 6)
        for interest in interests:
            rows.append(
                {
                    "schema_version": "3.0",
                    "profile_id": f"profile-v3-{int(profile['profile_id']):04d}",
                    "interest_id": interest,
                    "weight": explicit_weight,
                    "explicit_weight": explicit_weight,
                    "behavior_weight": 0.0,
                    "updated_at": GENERATED_AT.isoformat(),
                }
            )
    return rows


def main() -> None:
    rng = random.Random(SEED)
    source_events = read_csv(V2_DIR / "events_v2.csv")
    source_profiles = read_csv(V2_DIR / "profiles_v2.csv")
    required = OFFICIAL_EVENT_COUNT + MICRO_EVENT_COUNT
    if len(source_events) < required:
        raise ValueError(f"V3 dönüşümü için en az {required} V2 etkinliği gerekli.")

    organizers = build_organizers(rng)
    events = build_events(source_events, organizers, rng)
    participations = build_participations(events, rng)
    ratings = build_ratings(participations, {row["event_id"]: row for row in events}, rng)
    interest_weights = build_interest_weights(source_profiles)

    write_csv(OUTPUT_DIR / "organizers_v3.csv", organizers)
    write_csv(OUTPUT_DIR / "events_v3.csv", events)
    write_csv(OUTPUT_DIR / "participations_v3.csv", participations)
    write_csv(OUTPUT_DIR / "ratings_v3.csv", ratings)
    write_csv(OUTPUT_DIR / "interest_weights_v3.csv", interest_weights)

    official_count = sum(row["event_tier"] == "official" for row in events)
    micro_count = sum(row["event_tier"] == "micro" for row in events)
    print(
        f"V3 generated: {len(organizers)} organizers, {official_count} official, "
        f"{micro_count} micro, {len(participations)} participations, "
        f"{len(ratings)} ratings, {len(interest_weights)} interest weights"
    )


if __name__ == "__main__":
    main()
