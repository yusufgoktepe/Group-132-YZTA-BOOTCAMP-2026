"""CampusMatch demo uygulaması için ortak kulüp ve etkinlik kataloğu üretir."""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
MOBILE_DATA_DIR = PROJECT_ROOT / "mobile" / "data"

UNIVERSITIES = [
    ("yok-ankara", "Ankara Üniversitesi"),
    ("yok-bogazici", "Boğaziçi Üniversitesi"),
    ("yok-hacettepe", "Hacettepe Üniversitesi"),
    ("yok-itu", "İstanbul Teknik Üniversitesi"),
    ("yok-iyte", "İzmir Yüksek Teknoloji Enstitüsü"),
    ("yok-yildiz", "Yıldız Teknik Üniversitesi"),
]

CATEGORY_DEFINITIONS = [
    {
        "id": "technology",
        "label": "Teknoloji",
        "color": "#DCEFE9",
        "icon": "sparkles",
        "clubs": ["Yapay Zekâ ve Veri Topluluğu", "Yazılım Geliştirme Kulübü"],
        "topics": [
            ("Üretken Yapay Zekâ Atölyesi", ["ai", "data-science"]),
            ("Mobil Uygulama Geliştirme Günü", ["mobile-development", "product"]),
            ("Siber Güvenliğe İlk Adım", ["cybersecurity", "web-development"]),
            ("Veriden Hikâye Çıkarma", ["data-science", "ai"]),
            ("Oyun Geliştirme Maratonu", ["game-development", "product"]),
            ("Modern Web Teknolojileri", ["web-development", "ui-ux"]),
            ("Açık Kaynak Katkı Buluşması", ["web-development", "career"]),
            ("No-Code Ürün Sprinti", ["product", "mobile-development"]),
        ],
    },
    {
        "id": "career",
        "label": "Kariyer",
        "color": "#FFEBD3",
        "icon": "rocket",
        "clubs": ["Kariyer ve Gelişim Kulübü", "Girişimcilik Topluluğu"],
        "topics": [
            ("Fikirden Ürüne Girişimcilik", ["entrepreneurship", "product"]),
            ("Staj Mülakatı Simülasyonu", ["career", "entrepreneurship"]),
            ("Finansal Okuryazarlık 101", ["finance", "career"]),
            ("Ürün Yönetimi Vaka Çalışması", ["product", "career"]),
            ("Mezunlarla Networking Akşamı", ["career", "entrepreneurship"]),
            ("CV ve LinkedIn Kliniği", ["career", "product"]),
            ("Sosyal Girişim Tasarımı", ["entrepreneurship", "social-responsibility"]),
            ("Kariyer Rotanı Tasarla", ["career", "wellbeing"]),
        ],
    },
    {
        "id": "design-art",
        "label": "Tasarım ve Sanat",
        "color": "#F6E2E7",
        "icon": "color-palette",
        "clubs": ["Tasarım ve İnovasyon Kulübü", "Kampüs Sanat Topluluğu"],
        "topics": [
            ("Tasarım Odaklı Düşünme", ["ui-ux", "product"]),
            ("Mobil Arayüz Tasarım Atölyesi", ["ui-ux", "mobile-development"]),
            ("Kampüste Fotoğraf Yürüyüşü", ["photography", "culture"]),
            ("Afiş Tasarım Laboratuvarı", ["graphic-design", "ui-ux"]),
            ("Doğaçlama Tiyatro Gecesi", ["theatre", "culture"]),
            ("Yeni Başlayanlar İçin Müzik", ["music", "wellbeing"]),
            ("Portfolyo Değerlendirme Günü", ["graphic-design", "career"]),
            ("Kısa Film Üretim Sprinti", ["photography", "theatre"]),
        ],
    },
    {
        "id": "science",
        "label": "Bilim",
        "color": "#E4E7FA",
        "icon": "flask",
        "clubs": ["Bilim ve Araştırma Kulübü", "Sağlık Bilimleri Topluluğu"],
        "topics": [
            ("Öğrenci Araştırmaları Konferansı", ["engineering", "natural-sciences"]),
            ("Sağlıkta Yapay Zekâ Paneli", ["health-sciences", "ai"]),
            ("Laboratuvar Güvenliği Eğitimi", ["natural-sciences", "engineering"]),
            ("Sosyal Bilimlerde Veri Analizi", ["social-sciences", "data-science"]),
            ("Robotik Proje Buluşması", ["engineering", "ai"]),
            ("Psikoloji Araştırmaları Günü", ["social-sciences", "mental-health"]),
            ("İklim Bilimi Söyleşisi", ["natural-sciences", "sustainability"]),
            ("Akademik Poster Atölyesi", ["natural-sciences", "graphic-design"]),
        ],
    },
    {
        "id": "sports-health",
        "label": "Spor ve Sağlık",
        "color": "#DFF1E0",
        "icon": "fitness",
        "clubs": ["Kampüs Spor Kulübü", "İyi Yaşam Topluluğu"],
        "topics": [
            ("Gün Doğumu Koşu Grubu", ["sports", "wellbeing"]),
            ("Yeni Başlayanlar İçin Yoga", ["sports", "mental-health"]),
            ("Kampüs Voleybol Turnuvası", ["sports", "wellbeing"]),
            ("Sınav Döneminde İyi Oluş", ["mental-health", "wellbeing"]),
            ("Öğrenciler İçin Sağlıklı Beslenme", ["nutrition", "wellbeing"]),
            ("Masa Tenisi Tanışma Günü", ["sports", "wellbeing"]),
            ("Nefes ve Odaklanma Atölyesi", ["mental-health", "wellbeing"]),
            ("Doğa Yürüyüşü Buluşması", ["sports", "sustainability"]),
        ],
    },
    {
        "id": "social-impact",
        "label": "Sosyal Etki",
        "color": "#FFF0CF",
        "icon": "people",
        "clubs": ["Gönüllülük Kulübü", "Sürdürülebilir Kampüs Topluluğu"],
        "topics": [
            ("Sosyal Etki Fikir Maratonu", ["social-responsibility", "entrepreneurship"]),
            ("Kampüs Geri Dönüşüm Günü", ["sustainability", "volunteering"]),
            ("Çocuklarla Bilim Atölyesi", ["volunteering", "natural-sciences"]),
            ("Erişilebilir Kampüs Tasarımı", ["social-responsibility", "ui-ux"]),
            ("Sokak Hayvanları Destek Günü", ["volunteering", "social-responsibility"]),
            ("Sürdürülebilir Yaşam Semineri", ["sustainability", "wellbeing"]),
            ("Toplumsal Fayda Proje Pazarı", ["social-responsibility", "product"]),
            ("Gönüllülük Deneyimi Paylaşımı", ["volunteering", "career"]),
        ],
    },
    {
        "id": "culture-community",
        "label": "Kültür ve Topluluk",
        "color": "#E8E3F4",
        "icon": "globe",
        "clubs": ["Kültürlerarası Etkileşim Kulübü", "Gezi ve Dil Topluluğu"],
        "topics": [
            ("İngilizce Konuşma Kulübü", ["languages", "international-community"]),
            ("Uluslararası Öğrenci Buluşması", ["international-community", "culture"]),
            ("İstanbul Kültür Rotası", ["travel", "culture"]),
            ("Dünya Mutfakları Gecesi", ["culture", "international-community"]),
            ("Erasmus Deneyim Paylaşımı", ["travel", "languages"]),
            ("Kampüs Kitap Sohbeti", ["culture", "languages"]),
            ("İşaret Diline Giriş", ["languages", "social-responsibility"]),
            ("Şehirde Müze Keşfi", ["travel", "culture"]),
        ],
    },
]

EVENT_TYPES = ["workshop", "seminar", "networking", "social", "competition", "conference", "trip"]
EVENT_TYPE_LABELS = {
    "workshop": "Atölye",
    "seminar": "Seminer",
    "networking": "Networking",
    "social": "Sosyal",
    "competition": "Yarışma",
    "conference": "Konferans",
    "trip": "Gezi",
}
GOALS = ["learn", "network", "career", "build-project", "compete", "social-impact"]
MODES = ["onsite", "hybrid", "online"]
MODE_LABELS = {"onsite": "Kampüste", "hybrid": "Hibrit", "online": "Online"}


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_catalog() -> tuple[list[dict], list[dict], list[dict]]:
    clubs: list[dict] = []
    events: list[dict] = []
    mobile_events: list[dict] = []
    start_date = date(2026, 8, 3)
    event_id = 1

    for category_index, category in enumerate(CATEGORY_DEFINITIONS):
        category_club_ids = []
        for club_name in category["clubs"]:
            club_id = str(len(clubs) + 1)
            category_club_ids.append(club_id)
            clubs.append(
                {
                    "club_id": club_id,
                    "club_name": club_name,
                    "category": category["id"],
                    "description": f"{category['label']} alanında öğrencileri buluşturan demo öğrenci topluluğu.",
                    "target_departments": "all",
                    "target_interests": ";".join(
                        sorted({interest for _, interests in category["topics"] for interest in interests})
                    ),
                    "activity_level": "high" if len(clubs) % 3 == 0 else "medium",
                }
            )

        for topic_index, (title, interests) in enumerate(category["topics"]):
            university_id, university_name = UNIVERSITIES[(event_id + category_index) % len(UNIVERSITIES)]
            mode = MODES[(topic_index + category_index) % len(MODES)]
            event_type = EVENT_TYPES[(topic_index + category_index * 2) % len(EVENT_TYPES)]
            event_date = start_date + timedelta(days=(event_id - 1) * 2)
            hour = 11 + ((event_id * 2) % 8)
            minute = 30 if event_id % 3 == 0 else 0
            fee_type = "paid" if event_id % 7 == 0 else "free"
            club_id = category_club_ids[topic_index % len(category_club_ids)]
            club_name = clubs[int(club_id) - 1]["club_name"]
            location = "Çevrim içi" if mode == "online" else f"{university_name} - Kampüs Etkinlik Alanı"
            goals = [GOALS[(topic_index + category_index) % len(GOALS)], GOALS[(topic_index + 2) % len(GOALS)]]
            goals = list(dict.fromkeys(goals))
            description = (
                f"{title}, farklı bölümlerden öğrencilerin birlikte öğrenmesi, yeni bağlantılar "
                "kurması ve kampüs deneyimini zenginleştirmesi için hazırlanan uygulamalı bir demo etkinliğidir."
            )
            row = {
                "event_id": str(event_id),
                "club_id": club_id,
                "university_id": university_id,
                "title": title,
                "description": description,
                "category": category["id"],
                "event_type": event_type,
                "level": "all",
                "date": event_date.isoformat(),
                "time": f"{hour:02d}.{minute:02d}",
                "location": location,
                "location_type": mode,
                "quota": str(25 + (event_id % 6) * 10),
                "target_interests": ";".join(interests),
                "target_departments": "all",
                "target_goals": ";".join(goals),
                "fee_type": fee_type,
                "language": "en" if event_id % 9 == 0 else "tr",
            }
            events.append(row)
            mobile_events.append(
                {
                    "id": f"event-{event_id}",
                    "title": title,
                    "clubName": club_name,
                    "category": category["label"],
                    "interestIds": interests,
                    "goalIds": goals,
                    "participationMode": mode,
                    "feeType": fee_type,
                    "language": row["language"],
                    "dateLabel": f"{event_date.day} {['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'][event_date.month - 1]}",
                    "time": row["time"],
                    "location": location,
                    "locationType": MODE_LABELS[mode],
                    "format": EVENT_TYPE_LABELS[event_type],
                    "matchScore": 55 + (event_id * 7) % 36,
                    "description": description,
                    "tags": [interest.replace("-", " ").title() for interest in interests] + [EVENT_TYPE_LABELS[event_type]],
                    "reasons": ["İlgi alanlarından biriyle eşleşiyor", "Yeni bir kampüs deneyimi sunuyor"],
                    "icon": category["icon"],
                    "color": category["color"],
                }
            )
            event_id += 1

    return clubs, events, mobile_events


def main() -> None:
    clubs, events, mobile_events = build_catalog()
    write_csv(SAMPLE_DIR / "clubs_sample.csv", list(clubs[0]), clubs)
    write_csv(SAMPLE_DIR / "events_sample.csv", list(events[0]), events)
    MOBILE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with (MOBILE_DATA_DIR / "demo-events.json").open("w", encoding="utf-8") as file:
        json.dump(mobile_events, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(f"Demo catalog generated: {len(clubs)} clubs, {len(events)} events")


if __name__ == "__main__":
    main()
