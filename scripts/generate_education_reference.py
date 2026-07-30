"""Generate the mobile education catalog from official OSYM YKS tables."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import xlrd


REFERENCE_VERSION = "osym-yks-2026-2026-07-30"
SOURCE_URLS = [
    "https://dokuman.osym.gov.tr/web//2026/7/tablo-3-29u1s7pl.xls",
    "https://dokuman.osym.gov.tr/web//2026/7/tablo-4-295piovw.xls",
]
PROVINCES = {
    "ADANA", "ADIYAMAN", "AFYONKARAHİSAR", "AĞRI", "AKSARAY", "AMASYA", "ANKARA",
    "ANTALYA", "ARDAHAN", "ARTVİN", "AYDIN", "BALIKESİR", "BARTIN", "BATMAN",
    "BAYBURT", "BİLECİK", "BİNGÖL", "BİTLİS", "BOLU", "BURDUR", "BURSA",
    "ÇANAKKALE", "ÇANKIRI", "ÇORUM", "DENİZLİ", "DİYARBAKIR", "DÜZCE", "EDİRNE",
    "ELAZIĞ", "ERZİNCAN", "ERZURUM", "ESKİŞEHİR", "GAZİANTEP", "GİRESUN",
    "GÜMÜŞHANE", "HAKKARİ", "HATAY", "IĞDIR", "ISPARTA", "İSTANBUL", "İZMİR",
    "KAHRAMANMARAŞ", "KARABÜK", "KARAMAN", "KARS", "KASTAMONU", "KAYSERİ",
    "KIRIKKALE", "KIRKLARELİ", "KIRŞEHİR", "KİLİS", "KOCAELİ", "KONYA", "KÜTAHYA",
    "MALATYA", "MANİSA", "MARDİN", "MERSİN", "MUĞLA", "MUŞ", "NEVŞEHİR", "NİĞDE",
    "ORDU", "OSMANİYE", "RİZE", "SAKARYA", "SAMSUN", "SİİRT", "SİNOP", "SİVAS",
    "ŞANLIURFA", "ŞIRNAK", "TEKİRDAĞ", "TOKAT", "TRABZON", "TUNCELİ", "UŞAK",
    "VAN", "YALOVA", "YOZGAT", "ZONGULDAK",
}
CITY_OVERRIDES = {
    "ANADOLU ÜNİVERSİTESİ": "Eskişehir",
    "ATATÜRK ÜNİVERSİTESİ": "Erzurum",
    "BOĞAZİÇİ ÜNİVERSİTESİ": "İstanbul",
    "DİCLE ÜNİVERSİTESİ": "Diyarbakır",
    "EGE ÜNİVERSİTESİ": "İzmir",
    "FIRAT ÜNİVERSİTESİ": "Elazığ",
    "GEBZE TEKNİK ÜNİVERSİTESİ": "Kocaeli",
    "HACETTEPE ÜNİVERSİTESİ": "Ankara",
    "İNÖNÜ ÜNİVERSİTESİ": "Malatya",
    "MARMARA ÜNİVERSİTESİ": "İstanbul",
    "MİMAR SİNAN GÜZEL SANATLAR ÜNİVERSİTESİ": "İstanbul",
    "ORTA DOĞU TEKNİK ÜNİVERSİTESİ": "Ankara",
    "SELÇUK ÜNİVERSİTESİ": "Konya",
    "TRAKYA ÜNİVERSİTESİ": "Edirne",
    "TÜRK-JAPON BİLİM VE TEKNOLOJİ ÜNİVERSİTESİ": "İstanbul",
}
TYPE_PATTERN = re.compile(r"^(.*?)\s*\((Devlet|Vakıf) Üniversitesi\)\s*$")
VARIANT_PATTERN = re.compile(
    r"\s*\((?:Burslu|Ücretli|%\d+ İndirimli|KKTC Uyruklu)\)\s*$", re.IGNORECASE
)
PREP_PATTERN = re.compile(r"\((?:İngilizce|Almanca|Fransızca|Arapça|Rusça)\)", re.IGNORECASE)


def title_city(value: str) -> str:
    return title_tr(value)


def title_tr(value: str) -> str:
    lowered = value.translate(str.maketrans("Iİ", "ıi")).lower()
    parts = re.split(r"([\s-]+)", lowered)
    seen_word = False
    for index, part in enumerate(parts):
        if not part or re.fullmatch(r"[\s-]+", part):
            continue
        if seen_word and part in {"ve", "ile"}:
            continue
        first = {"i": "İ", "ı": "I"}.get(part[0], part[0].upper())
        parts[index] = first + part[1:]
        seen_word = True
    return "".join(parts)


def slugify(value: str) -> str:
    translations = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    ascii_value = unicodedata.normalize("NFKD", value.translate(translations)).encode(
        "ascii", "ignore"
    ).decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")


def parse_university_heading(value: str):
    match = TYPE_PATTERN.match(value.strip())
    if not match:
        return None

    raw_name, raw_type = match.groups()
    if " ADINA " in f" {raw_name} " or "KKTC" in raw_name or "YURTDIŞI" in raw_name:
        return None
    if "ÜNİVERSİTESİ" not in raw_name and "YÜKSEK TEKNOLOJİ ENSTİTÜSÜ" not in raw_name:
        return None

    city = None
    city_match = re.search(r"\s+\(([^()]*)\)\s*$", raw_name)
    if city_match and city_match.group(1) in PROVINCES:
        city = title_city(city_match.group(1))
        raw_name = raw_name[: city_match.start()].strip()

    if not city:
        for province in sorted(PROVINCES, key=len, reverse=True):
            if raw_name == province or raw_name.startswith(f"{province} "):
                city = title_city(province)
                break

    city = city or CITY_OVERRIDES.get(raw_name)
    return {
        "id": f"osym-{slugify(raw_name)}",
        "name": title_tr(raw_name),
        "city": city,
        "type": "state" if raw_type == "Devlet" else "foundation",
        "programs": {},
    }


def clean_program_name(value: str) -> str:
    cleaned = value.strip()
    while VARIANT_PATTERN.search(cleaned):
        cleaned = VARIANT_PATTERN.sub("", cleaned)
    return cleaned


def load_table(path: Path, level: str, universities: dict[str, dict]) -> None:
    sheet = xlrd.open_workbook(path).sheet_by_index(0)
    current = None

    for row_index in range(sheet.nrows):
        code = sheet.cell_value(row_index, 0)
        label = str(sheet.cell_value(row_index, 1)).strip()
        if not label:
            continue

        if not code:
            parsed = parse_university_heading(label)
            if parsed:
                current = universities.setdefault(parsed["id"], parsed)
            continue

        if not current:
            continue

        try:
            program_code = int(float(str(code).strip()))
        except ValueError:
            continue

        duration_value = sheet.cell_value(row_index, 2)
        if not isinstance(duration_value, (int, float)) or duration_value <= 0:
            continue

        name = clean_program_name(label)
        duration = int(duration_value)
        dedupe_key = f"{name.casefold()}:{duration}:{level}"
        current["programs"].setdefault(
            dedupe_key,
            {
                "id": f"osym-{program_code}",
                "name": name,
                "level": level,
                "duration": duration,
                "hasPreparatoryClass": bool(PREP_PATTERN.search(name)),
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("table3", type=Path)
    parser.add_argument("table4", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    universities: dict[str, dict] = {}
    load_table(args.table3, "associate", universities)
    load_table(args.table4, "bachelor", universities)

    unresolved = sorted(item["name"] for item in universities.values() if not item["city"])
    if unresolved:
        raise ValueError(f"Şehri belirlenemeyen üniversiteler: {', '.join(unresolved)}")

    records = []
    for university in universities.values():
        university["programs"] = sorted(
            university["programs"].values(), key=lambda item: item["name"].casefold()
        )
        if university["programs"]:
            records.append(university)
    records.sort(key=lambda item: item["name"].casefold())

    payload = {
        "metadata": {
            "referenceVersion": REFERENCE_VERSION,
            "updatedAt": "2026-07-30",
            "sourceLabel": "ÖSYM 2026-YKS Tablo 3 ve Tablo 4",
            "sourceUrls": SOURCE_URLS,
            "universityCount": len(records),
            "programCount": sum(len(item["programs"]) for item in records),
            "notes": "Hazırlık bilgisi, program adındaki öğretim dilinden türetilmiştir.",
        },
        "universities": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(records)} üniversite ve {payload['metadata']['programCount']} program yazıldı.")


if __name__ == "__main__":
    main()
